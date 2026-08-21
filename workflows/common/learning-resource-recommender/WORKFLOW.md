# Learning Resource Recommender

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

## Core Rule

Recommend resources as a learning decision, not a link dump. Use IELTS Buddy state and the learner's current weakness first, then choose a small number of external resources that fit the skill, level, time budget, and learning mode.

The learning-resource catalog is bundled in this Skill and maintained by the repository developer. Do not depend on external local paths or ask the learner to provide the catalog.

## Inputs

Use any available combination:

- IELTS Buddy route progress, weak skills, vocabulary progress, or recent practice errors.
- User goal: IELTS band, CEFR level, target skill, accent preference, topic interest, available minutes.
- The curated catalog at `references/resources.json`.
- Direct resource candidates supplied in chat.

## Workflow

1. Identify the learner's current need:
   - listening input;
   - pronunciation/speaking;
   - reading input;
   - writing support;
   - vocabulary;
   - grammar;
   - exam-specific IELTS practice;
   - background immersion.
2. Run `../../../scripts/workflows/learning-resource-recommender/extract_learning_resource_catalog.py` to read the bundled catalog. Prefer entries reviewed recently enough for the current request; verify unstable availability before making a high-cost recommendation.
3. Filter candidates by:
   - target skill;
   - level or difficulty cues;
   - IELTS relevance;
   - availability of transcripts/subtitles/exercises;
   - cognitive load and time budget;
   - whether the learner needs input, output, or review.
4. Recommend 3-7 resources only.
5. For each resource, explain:
   - why this resource fits the current need;
   - how to use it this week;
   - what output or review artifact to bring back to the Agent.
6. Prefer official, stable, learner-friendly resources when choices are close.
7. If a resource is entertainment-first, label it as immersion, not IELTS practice.

## Default Output

Use concise chat for quick recommendations. When the user asks for a study pack, weekly resource plan, or printable recommendation list, deliver a validated `.docx`.

1. Build a recommendation plan.
2. Generate the DOCX with `../../../scripts/workflows/learning-resource-recommender/create_resource_recommendations_docx.py`.
3. Validate it with `../../../scripts/workflows/learning-resource-recommender/validate_resource_recommendations_docx.py`.
4. Return the absolute path to the final DOCX.

## Bundled Resources

- `../../../scripts/workflows/learning-resource-recommender/extract_learning_resource_catalog.py`: parse a Markdown resource catalog into JSON candidates with title, URL, description, and heading path.
- `../../../scripts/workflows/learning-resource-recommender/create_resource_recommendations_docx.py`: create a recommendation DOCX with ranked resources and a weekly usage plan.
- `../../../scripts/workflows/learning-resource-recommender/validate_resource_recommendations_docx.py`: verify required sections, tables, Times New Roman, and plan content.
- `references/resources.json`: structured, general-audience resource catalog with skill, level, access, transcript, exercise, provider, and review metadata.

## JSON Recommendation Plan

```json
{
  "learner_goal": "IELTS Listening Band 7.0",
  "focus": "listening",
  "level": "B1-B2",
  "time_budget": "30 minutes/day",
  "rationale": "The learner needs transcript-supported listening and paraphrase review.",
  "recommendations": [
    {
      "rank": 1,
      "title": "BBC 6 Minute English",
      "url": "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english",
      "category": "听力学习 / 播客资源",
      "fit": "Short episodes with learner-friendly topics and transcripts.",
      "how_to_use": "Listen once without transcript, then mark 5 paraphrases from the transcript.",
      "bring_back": "Three new phrases and one sentence you failed to catch."
    }
  ],
  "weekly_plan": [
    "Day 1-2: BBC 6 Minute English transcript listening.",
    "Day 3-4: One IELTS listening section and error notebook."
  ]
}
```

```bash
python ../../../scripts/workflows/learning-resource-recommender/extract_learning_resource_catalog.py --skill listening --level B2 --limit 12
python ../../../scripts/workflows/learning-resource-recommender/create_resource_recommendations_docx.py resource_recommendation_plan.json
python ../../../scripts/workflows/learning-resource-recommender/validate_resource_recommendations_docx.py ~/Desktop/IELTS_Resource_Recommendations_YYYYMMDD_HHMM.docx --plan-json resource_recommendation_plan.json
```

## Quality Bar

- Do not recommend more than seven resources at once.
- Do not treat general English resources as IELTS materials unless they train a concrete IELTS subskill.
- Include a use method, not just a URL.
- Use only catalog entries that satisfy its general-audience policy. Browse to verify availability when the resource is time-sensitive, paid, region-dependent, or likely to have changed since `lastReviewed`.
