# Daily Study Loop

## Core Rule

The Agent chooses the learning move. IELTS Buddy supplies state, materials, and links. Do not ask the server for a generic recommendation when local evidence and the route data are enough.

## Inputs

Read only the data needed for the current session:

1. Learning snapshot or cloud events from `../../references/learning-loop.md`.
2. Course route progress from `../../references/course-route.md` when the user asks what to learn.
3. Vocabulary due/new/weak counts from `../../references/vocabulary.md` when words are likely part of the session.
4. Practice availability and browser links from `../../references/practice.md` or `../../references/web-workspace.md` when the next task needs actual question interaction.

## Session Policy

1. Start with due review if there is an overdue or failed item.
2. Otherwise continue an in-progress course route item.
3. Otherwise target the weakest supported IELTS skill with evidence.
4. With no evidence, read `../diagnostic-baseline/WORKFLOW.md` and run the smallest useful baseline.
5. 当前对话已有刷题复盘、口语覆盖图、写作提纲/批改或词汇复习结果时，先读 [证据到下一步](../evidence-to-next-action/WORKFLOW.md)，不要丢失刚产生的证据。
6. Give one task at a time.
7. Use hint-before-answer for stored answers.
8. Record the outcome after objective grading or local Agent review.
9. End with exactly one next action unless the user asks for a full plan.

## Adaptive Mix

For a 20-30 minute self-study block:

1. Warm-up: one easy retrieval item or 3-5 vocabulary cards.
2. Main task: one route lesson, practice part, writing paragraph, or speaking answer.
3. Error repair: classify the most important mistake and create a micro-drill.
4. Review scheduling: record the outcome and set the next due item.

Keep the block small. Do not build a dashboard when the learner needs to study.

## Response Shape

Use this shape:

```text
今天先做：<task title>
原因：<one evidence-based reason>
做法：<one concise instruction>
链接：<browser URL only if the task is browser-owned or the user asked for it>
完成后告诉我：<what result the user should bring back>
```

If the Agent can run the task locally, do not provide a browser link by default.

## Course Route Workbook

When the user asks for the full IELTS self-study route, a printable route, or a course checklist, deliver a validated Course Route Workbook `.docx`.

1. Read route data with `ielts_learning_route_read`.
2. Read progress with `ielts_learning_route_progress`.
3. Read next actions with `ielts_learning_route_next` when the learner asks what to do first.
4. Build a workbook plan with subjects, units, course IDs, status, success criteria, and browser URLs.
5. Generate the DOCX with `scripts/create_course_route_workbook_docx.py`.
6. Validate it with `scripts/validate_course_route_workbook_docx.py`.
7. Return the absolute path to the final DOCX.

## Bundled Resources

- `scripts/create_course_route_workbook_docx.py`: create a course route workbook with next actions, route checklist, and study checkpoints.
- `scripts/validate_course_route_workbook_docx.py`: verify required sections, route tables, Times New Roman, and plan content.

## JSON Route Workbook Plan

```json
{
  "route_title": "IELTS Full-Course Route",
  "learner_goal": "Reach Band 7.0 in 10 weeks",
  "timeframe": "10 weeks",
  "next_actions": [
    {
      "priority": "1",
      "title": "Reading paraphrase basics",
      "reason": "Lowest recent mastery",
      "browser_url": "https://ieltsbuddy.igocn.cn/learning-center?course=reading-paraphrase"
    }
  ],
  "subjects": [
    {
      "subject": "reading",
      "units": [
        {
          "title": "Paraphrase and evidence",
          "courses": [
            {
              "course_id": "reading-paraphrase",
              "title": "Reading paraphrase basics",
              "status": "in_progress",
              "success_criteria": ["Finish the lesson", "Review 3 wrong answers with evidence map"]
            }
          ]
        }
      ]
    }
  ],
  "checkpoints": ["After each practice, record one error type and one next action."]
}
```

```bash
python scripts/create_course_route_workbook_docx.py route_workbook_plan.json
python scripts/validate_course_route_workbook_docx.py ~/Desktop/IELTS_Course_Route_Workbook_YYYYMMDD_HHMM.docx --plan-json route_workbook_plan.json
```

## Borrowed Pattern

This workflow adapts the session orchestration pattern from MIT-licensed language-learning Skills such as Fluent, but removes gamified UI and replaces JSON databases with IELTS Buddy events plus the local mirror.
