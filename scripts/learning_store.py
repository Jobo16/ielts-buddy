#!/usr/bin/env python3
"""Local mirror for cloud-backed IELTS learning events and learning policy."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

STORE_SCHEMA_VERSION = 1
EVENT_SCHEMA_VERSION = 1
RECENCY_WEIGHTS = (0.50, 0.70, 0.85, 0.95, 1.00)
REVIEW_INTERVAL_DAYS = (1, 3, 7, 14, 30, 60, 90)
CONFIDENCE_LEVELS = ("low", "medium", "high")
TAXONOMY_PATH = Path(__file__).resolve().with_name("skill-taxonomy.json")


def load_taxonomy() -> dict[str, Any]:
    with TAXONOMY_PATH.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value.get("subjects"), dict) or not isinstance(value.get("evidenceTypes"), dict):
        raise ValueError(f"Invalid skill taxonomy: {TAXONOMY_PATH}")
    return value


TAXONOMY = load_taxonomy()
SUPPORTED_SUBJECTS = tuple(TAXONOMY["subjects"])
SKILL_SUBJECTS = {
    skill_code: subject
    for subject, skill_codes in TAXONOMY["subjects"].items()
    for skill_code in skill_codes
}
RATING_PERFORMANCE = TAXONOMY["evidenceTypes"]["retrieval"]["ratings"]


def default_db_path() -> Path:
    home = Path(os.environ.get("IELTS_BUDDY_HOME", Path.home() / ".ielts-buddy"))
    return home / "learning.db"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_datetime(value: str | None = None) -> str:
    parsed = parse_datetime(value) if value else utc_now()
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return utc_now()
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def open_store(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode = WAL")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS metadata (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS learning_events (
          local_seq INTEGER PRIMARY KEY AUTOINCREMENT,
          event_id TEXT NOT NULL UNIQUE,
          device_id TEXT NOT NULL,
          event_type TEXT NOT NULL,
          subject_code TEXT,
          object_type TEXT,
          object_id TEXT,
          skill_codes_json TEXT NOT NULL DEFAULT '[]',
          payload_json TEXT NOT NULL DEFAULT '{}',
          schema_version INTEGER NOT NULL DEFAULT 1,
          occurred_at TEXT NOT NULL,
          synced INTEGER NOT NULL DEFAULT 0,
          remote_cursor INTEGER,
          created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_local_learning_events_occurred
          ON learning_events(occurred_at, local_seq);
        CREATE INDEX IF NOT EXISTS idx_local_learning_events_sync
          ON learning_events(synced, local_seq);
        """
    )
    ensure_metadata(connection, "schema_version", str(STORE_SCHEMA_VERSION))
    ensure_metadata(connection, "device_id", str(uuid.uuid4()))
    ensure_metadata(connection, "cloud_cursor", "0")
    connection.commit()
    return connection


def ensure_metadata(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute(
        "INSERT INTO metadata (key, value) VALUES (?, ?) ON CONFLICT(key) DO NOTHING",
        (key, value),
    )


def metadata(connection: sqlite3.Connection, key: str) -> str:
    row = connection.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
    if not row:
        raise RuntimeError(f"Missing metadata: {key}")
    return str(row["value"])


def record_event(connection: sqlite3.Connection, event: dict[str, Any], synced: bool = False) -> bool:
    validate_event(event)
    remote_cursor = event.get("cursor")
    cursor = connection.execute(
        """
        INSERT OR IGNORE INTO learning_events (
          event_id, device_id, event_type, subject_code, object_type, object_id,
          skill_codes_json, payload_json, schema_version, occurred_at, synced,
          remote_cursor, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event["eventId"],
            event["deviceId"],
            event["eventType"],
            event.get("subjectCode"),
            event.get("objectType"),
            event.get("objectId"),
            json.dumps(event.get("skillCodes", []), separators=(",", ":")),
            json.dumps(event.get("payload", {}), separators=(",", ":")),
            int(event.get("schemaVersion", EVENT_SCHEMA_VERSION)),
            iso_datetime(event.get("occurredAt")),
            1 if synced else 0,
            int(remote_cursor) if remote_cursor is not None else None,
            iso_datetime(),
        ),
    )
    inserted = cursor.rowcount == 1
    if not inserted and synced:
        connection.execute(
            """
            UPDATE learning_events
            SET synced = 1, remote_cursor = COALESCE(?, remote_cursor)
            WHERE event_id = ?
            """,
            (int(remote_cursor) if remote_cursor is not None else None, event["eventId"]),
        )
    connection.commit()
    return inserted


def validate_event(event: dict[str, Any]) -> None:
    required = ("eventId", "deviceId", "eventType", "schemaVersion", "occurredAt")
    missing = [field for field in required if field not in event]
    if missing:
        raise ValueError(f"Learning event is missing fields: {', '.join(missing)}")
    subject = event.get("subjectCode")
    if subject is not None and subject not in SUPPORTED_SUBJECTS:
        raise ValueError(f"Unknown subject code: {subject}")
    for skill_code in event.get("skillCodes", []):
        expected_subject = SKILL_SUBJECTS.get(skill_code)
        if expected_subject is None:
            raise ValueError(f"Unknown skill code: {skill_code}")
        if subject is not None and expected_subject != subject:
            raise ValueError(f"Skill code {skill_code} does not belong to subject {subject}")
    payload = event.get("payload", {})
    if not isinstance(payload, dict):
        raise ValueError("Learning event payload must be an object")
    evidence_type = payload.get("evidenceType")
    if evidence_type is not None:
        if subject is None or not event.get("skillCodes"):
            raise ValueError("Evidence events require a subject and at least one skill code")
        performance_value(payload)


def performance_value(payload: dict[str, Any]) -> float | None:
    evidence_type = payload.get("evidenceType")
    if evidence_type == "objective":
        correct = payload.get("correct")
        if not isinstance(correct, bool):
            raise ValueError("Objective evidence requires boolean payload.correct")
        return 1.0 if correct else 0.0
    if evidence_type == "rubric":
        performance = payload.get("performance")
        confidence = payload.get("confidence")
        if not isinstance(performance, (int, float)) or isinstance(performance, bool) or not 0 <= performance <= 1:
            raise ValueError("Rubric evidence requires payload.performance between 0 and 1")
        if confidence not in CONFIDENCE_LEVELS:
            raise ValueError("Rubric evidence requires confidence: low, medium, or high")
        return float(performance)
    if evidence_type == "retrieval":
        rating = payload.get("rating")
        if rating not in RATING_PERFORMANCE:
            raise ValueError("Retrieval evidence requires rating: again, hard, or good")
        return float(RATING_PERFORMANCE[rating])
    if evidence_type is None:
        return None
    raise ValueError(f"Unknown evidence type: {evidence_type}")


def new_event(connection: sqlite3.Connection, args: argparse.Namespace, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "eventId": args.event_id or str(uuid.uuid4()),
        "deviceId": metadata(connection, "device_id"),
        "eventType": args.event_type,
        "subjectCode": args.subject,
        "objectType": args.object_type,
        "objectId": args.object_id,
        "skillCodes": sorted(set(args.skill or [])),
        "payload": payload,
        "schemaVersion": EVENT_SCHEMA_VERSION,
        "occurredAt": iso_datetime(args.occurred_at),
    }


def load_events(connection: sqlite3.Connection, subject: str | None = None) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT * FROM learning_events
        WHERE (? IS NULL OR subject_code = ?)
        ORDER BY
          CASE WHEN remote_cursor IS NULL THEN 1 ELSE 0 END ASC,
          remote_cursor ASC,
          local_seq ASC
        """,
        (subject, subject),
    ).fetchall()
    return [row_to_event(row) for row in rows]


def row_to_event(row: sqlite3.Row) -> dict[str, Any]:
    event = {
        "eventId": row["event_id"],
        "deviceId": row["device_id"],
        "eventType": row["event_type"],
        "subjectCode": row["subject_code"],
        "objectType": row["object_type"],
        "objectId": row["object_id"],
        "skillCodes": json.loads(row["skill_codes_json"]),
        "payload": json.loads(row["payload_json"]),
        "schemaVersion": int(row["schema_version"]),
        "occurredAt": row["occurred_at"],
    }
    return {key: value for key, value in event.items() if value is not None}


def mastery_snapshot(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outcomes: dict[str, list[float]] = defaultdict(list)
    subjects: dict[str, str | None] = {}
    for event in events:
        performance = performance_value(event.get("payload", {}))
        if performance is None:
            continue
        for skill in event.get("skillCodes", []):
            outcomes[skill].append(performance)
            subjects[skill] = event.get("subjectCode")

    result = []
    for skill, history in outcomes.items():
        recent = history[-len(RECENCY_WEIGHTS) :]
        weights = RECENCY_WEIGHTS[-len(recent) :]
        mastery = sum(weight * performance for weight, performance in zip(weights, recent)) / sum(weights)
        result.append(
            {
                "skillCode": skill,
                "subjectCode": subjects[skill],
                "mastery": round(mastery, 4),
                "confidence": round(min(1.0, len(history) / 5), 4),
                "evidenceCount": len(history),
                "recentPerformance": round(sum(recent) / len(recent), 4),
                "recentEvidence": len(recent),
            }
        )
    return sorted(result, key=lambda item: (item["mastery"], -item["confidence"], item["skillCode"]))


def review_snapshot(events: list[dict[str, Any]], now: datetime | None = None) -> list[dict[str, Any]]:
    now = now or utc_now()
    histories: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        payload = event.get("payload", {})
        performance = performance_value(payload)
        reviewable = payload.get("reviewable", payload.get("evidenceType") in {"objective", "retrieval"})
        if performance is None or not reviewable or not event.get("objectType") or not event.get("objectId"):
            continue
        histories[(event["objectType"], event["objectId"])].append(event)

    reviews = []
    for (object_type, object_id), history in histories.items():
        latest = history[-1]
        latest_performance = performance_value(latest["payload"])
        latest_successful = latest_performance is not None and latest_performance >= 0.7
        correct_streak = 0
        for event in reversed(history):
            performance = performance_value(event["payload"])
            if performance is None or performance < 0.7:
                break
            correct_streak += 1
        if latest_successful:
            interval = REVIEW_INTERVAL_DAYS[min(correct_streak - 1, len(REVIEW_INTERVAL_DAYS) - 1)]
            due_at = parse_datetime(latest["occurredAt"]) + timedelta(days=interval)
        else:
            interval = 0
            due_at = parse_datetime(latest["occurredAt"])
        reviews.append(
            {
                "objectType": object_type,
                "objectId": object_id,
                "subjectCode": latest.get("subjectCode"),
                "skillCodes": latest.get("skillCodes", []),
                "dueAt": iso_datetime(due_at.isoformat()),
                "due": due_at <= now,
                "intervalDays": interval,
                "correctStreak": correct_streak,
            }
        )
    return sorted(reviews, key=lambda item: (not item["due"], item["dueAt"], item["objectId"]))


def snapshot(connection: sqlite3.Connection, subject: str | None = None) -> dict[str, Any]:
    events = load_events(connection, subject)
    reviews = review_snapshot(events)
    mastery = mastery_snapshot(events)
    return {
        "generatedAt": iso_datetime(),
        "cloudCursor": int(metadata(connection, "cloud_cursor")),
        "eventCount": len(events),
        "dueReviews": [item for item in reviews if item["due"]],
        "upcomingReviews": [item for item in reviews if not item["due"]][:20],
        "mastery": mastery,
    }


def next_activity(connection: sqlite3.Connection, subject: str | None = None) -> dict[str, Any]:
    state = snapshot(connection, subject)
    if state["dueReviews"]:
        review = state["dueReviews"][0]
        return {"activityType": "review", "reason": "due_review", "review": review}
    if state["mastery"]:
        skill = state["mastery"][0]
        if skill["confidence"] < 0.4:
            return {"activityType": "diagnostic_practice", "reason": "low_confidence", "skill": skill}
        return {"activityType": "targeted_practice", "reason": "lowest_mastery", "skill": skill}
    return {
        "activityType": "diagnostic_practice",
        "reason": "insufficient_evidence",
        "subjectCode": subject,
    }


def read_json_input(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def extract_remote_events(value: Any) -> tuple[list[dict[str, Any]], int | None]:
    if isinstance(value, list):
        return value, None
    if not isinstance(value, dict):
        raise ValueError("Import payload must be an event array or API response object")
    data = value.get("data", value)
    if not isinstance(data, dict) or not isinstance(data.get("events"), list):
        raise ValueError("Import payload does not contain events")
    cursor = data.get("nextCursor")
    return data["events"], int(cursor) if cursor is not None else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=default_db_path())
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init")
    for command in ("record-event", "record-attempt", "record-evidence"):
        child = subparsers.add_parser(command)
        child.add_argument("--event-id")
        child.add_argument("--subject", choices=SUPPORTED_SUBJECTS)
        child.add_argument("--object-type", required=True)
        child.add_argument("--object-id", required=True)
        child.add_argument("--skill", action="append", default=[])
        child.add_argument("--occurred-at")
    event_parser = subparsers.choices["record-event"]
    event_parser.add_argument("--type", dest="event_type", required=True)
    event_parser.add_argument("--payload-json", default="{}")
    attempt_parser = subparsers.choices["record-attempt"]
    attempt_parser.set_defaults(event_type="practice.attempted")
    attempt_parser.add_argument("--correct", choices=("true", "false"), required=True)
    attempt_parser.add_argument("--score", type=float)
    attempt_parser.add_argument("--session-id")
    evidence_parser = subparsers.choices["record-evidence"]
    evidence_parser.set_defaults(event_type="learning.evidence_recorded")
    evidence_parser.add_argument("--evidence-type", choices=("rubric", "retrieval"), required=True)
    evidence_parser.add_argument("--performance", type=float)
    evidence_parser.add_argument("--rating", choices=tuple(RATING_PERFORMANCE))
    evidence_parser.add_argument("--confidence", choices=CONFIDENCE_LEVELS)
    evidence_parser.add_argument("--reviewable", action="store_true")
    evidence_parser.add_argument("--details-json", default="{}")

    for command in ("snapshot", "next"):
        child = subparsers.add_parser(command)
        child.add_argument("--subject", choices=SUPPORTED_SUBJECTS)
    outbox = subparsers.add_parser("outbox")
    outbox.add_argument("--limit", type=int, default=100)
    ack = subparsers.add_parser("ack")
    ack.add_argument("--event-id", action="append", required=True)
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("--input", required=True)
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    connection = open_store(args.db)
    try:
        if args.command == "init":
            return {
                "database": str(args.db),
                "deviceId": metadata(connection, "device_id"),
                "storeSchemaVersion": STORE_SCHEMA_VERSION,
                "eventSchemaVersion": EVENT_SCHEMA_VERSION,
            }
        if args.command == "record-event":
            payload = json.loads(args.payload_json)
            if not isinstance(payload, dict):
                raise ValueError("payload-json must be a JSON object")
            event = new_event(connection, args, payload)
            record_event(connection, event)
            return {"recorded": True, "event": event}
        if args.command == "record-attempt":
            payload = {"evidenceType": "objective", "correct": args.correct == "true", "reviewable": True}
            if args.score is not None:
                payload["score"] = args.score
            if args.session_id:
                payload["sessionId"] = args.session_id
            event = new_event(connection, args, payload)
            record_event(connection, event)
            return {"recorded": True, "event": event}
        if args.command == "record-evidence":
            details = json.loads(args.details_json)
            if not isinstance(details, dict):
                raise ValueError("details-json must be a JSON object")
            reviewable = args.reviewable or args.evidence_type == "retrieval"
            payload = {**details, "evidenceType": args.evidence_type, "reviewable": reviewable}
            if args.evidence_type == "rubric":
                payload.update({"performance": args.performance, "confidence": args.confidence})
            else:
                payload["rating"] = args.rating
            event = new_event(connection, args, payload)
            record_event(connection, event)
            return {"recorded": True, "event": event}
        if args.command == "snapshot":
            return snapshot(connection, args.subject)
        if args.command == "next":
            return next_activity(connection, args.subject)
        if args.command == "outbox":
            limit = min(200, max(1, args.limit))
            rows = connection.execute(
                "SELECT * FROM learning_events WHERE synced = 0 ORDER BY local_seq ASC LIMIT ?",
                (limit,),
            ).fetchall()
            return {"events": [row_to_event(row) for row in rows]}
        if args.command == "ack":
            placeholders = ",".join("?" for _ in args.event_id)
            cursor = connection.execute(
                f"UPDATE learning_events SET synced = 1 WHERE event_id IN ({placeholders})",
                tuple(args.event_id),
            )
            connection.commit()
            return {"acknowledged": cursor.rowcount}
        if args.command == "import":
            events, cursor = extract_remote_events(read_json_input(args.input))
            imported = sum(record_event(connection, event, synced=True) for event in events)
            if cursor is not None:
                connection.execute(
                    "UPDATE metadata SET value = ? WHERE key = 'cloud_cursor'",
                    (str(cursor),),
                )
                connection.commit()
            return {"imported": imported, "duplicates": len(events) - imported, "cloudCursor": cursor}
        raise ValueError(f"Unknown command: {args.command}")
    finally:
        connection.close()


def main() -> None:
    try:
        print(json.dumps(run(build_parser().parse_args()), ensure_ascii=False, indent=2))
    except (ValueError, sqlite3.Error) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
