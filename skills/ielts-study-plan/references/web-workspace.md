# Web Workspace

Some IELTS Buddy capabilities are browser-first because their best execution surface is interactive UI, audio, timing, or a long-running session. They still need data access when a portable Agent can use MCP. This portable Skill does not use IELTS Buddy Web Workspace actions.

## Data And Link Rule

For browser-first capabilities, return both:

1. data from MCP or another documented IELTS Buddy interface, when available;
2. the stable IELTS Buddy route for the user to continue interactively.

Do not force the browser when data can answer the request. Do not force a local substitute when the request is about doing timed practice, playing audio, taking a mock test, or interacting with a web-only tool.

| Capability | Data interface | Browser route |
| --- | --- | --- |
| Learning center | `ielts_learning_route_read`, `ielts_learning_route_progress`, `ielts_learning_route_next`, `ielts_resources_search`, `ielts_resources_read`, `ielts_resources_related` | `https://ieltsbuddy.igocn.cn/learning-center` |
| Practice center | `ielts_practice_list_taxonomy`, `ielts_practice_search_parts`, `ielts_practice_read_part`, `ielts_practice_start_session`, `ielts_practice_recent_activity` | `https://ieltsbuddy.igocn.cn/practice` |
| Mock tests | `ielts_mock_list_papers`, `ielts_mock_recent_activity`, `ielts_practice_read_session`, objective-only `ielts_practice_submit_session`; writing/speaking review stays local | `https://ieltsbuddy.igocn.cn/mock` |
| Preparation information | `ielts_prep_search`, `ielts_prep_read_guide` | `https://ieltsbuddy.igocn.cn/prep-info` |
| Courses | `ielts_resources_search` with `types=["course"]`, then `ielts_resources_read` with the returned handle | `https://ieltsbuddy.igocn.cn/courses` |
| Learner profile and footprints | `ielts_learner_read_profile`, `ielts_footprints_list` | `https://ieltsbuddy.igocn.cn/footprints` |
| Study plans | `ielts_study_plans_list`, `ielts_study_plans_get`, `ielts_study_plans_next_actions`, `ielts_study_plans_create`, `ielts_study_plans_update`, `ielts_study_plans_update_task`, `ielts_study_plans_delete`; local Agent drafts and reviews plan content using `planning.md` | `https://ieltsbuddy.igocn.cn/plans` |
| Toolbox index | Capability manifest, then the specific tool route below | `https://ieltsbuddy.igocn.cn/ai-apps` |
| Reading vocabulary extraction | Local `ielts-reading-lexicon` workflow for DOCX output; `ielts_vocabulary_personal_add` only for optional saving to My Vocabulary Book | `https://ieltsbuddy.igocn.cn/ai-apps/reading-lexicon` |
| Listening dictation | Intentionally browser-owned for player, replay, typed dictation, and answer reveal; use the route rather than exposing transcript-level data | `https://ieltsbuddy.igocn.cn/ai-apps/listening-dictation` |
| Vocabulary practice | Personal: `ielts_vocabulary_personal_list`, `ielts_vocabulary_personal_progress`, `ielts_vocabulary_personal_prepare_cards`, `ielts_vocabulary_personal_record_review`, `ielts_vocabulary_personal_update`; built-in: `ielts_vocabulary_builtin_progress`, `ielts_vocabulary_builtin_prepare_cards`, `ielts_vocabulary_builtin_record_review` | `https://ieltsbuddy.igocn.cn/ai-apps/vocabulary-practice` |
| Speaking topic weaving | Use the installed `$ielts-speaking-coach` Skill; `ielts_speaking_materials_list`, data-only `ielts_speaking_materials_create`, data-only `ielts_speaking_materials_update`, `ielts_speaking_materials_archive`, `ielts_speaking_materials_start_practice`; create/update must include exact question links chosen locally | `https://ieltsbuddy.igocn.cn/ai-apps/speaking-topic-weaver` |
| Band score calculator | Browser-only calculator; no portable data tool | `https://ieltsbuddy.igocn.cn/ai-apps/band-score-calculator` |

When a row says the portable data interface is incomplete, state the limitation and provide the route. Do not imply the local Agent completed the interactive web operation.

For browser-owned attempts that produce results, transcripts, answers, or notes, continue with the relevant installed Skill instead of rebuilding the browser UI: `$ielts-listening-review`, `$ielts-reading-review`, or `$ielts-speaking-coach`.
