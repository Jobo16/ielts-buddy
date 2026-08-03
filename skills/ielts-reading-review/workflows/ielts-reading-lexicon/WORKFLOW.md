# IELTS Reading Lexicon

Default learner-facing notes, comments, section titles, and review prompts are Simplified Chinese. Keep extracted phrases, source sentences, and IELTS-style example sentences in English.

## Core Rule

Treat the source reading passage as the authority. Extract phrases that appear verbatim in the DOCX passage, then explain why they matter for IELTS Reading and academic English. Do not use Markdown as the deliverable.

## Default Deliverable

Deliver a validated `.docx` by default. The DOCX is the primary local Agent output, not an optional export.

1. Run `scripts/extract_reading_docx.py` on the input DOCX.
2. Build a concise lexicon plan from the extracted passage text.
3. Generate the annotated DOCX with `scripts/create_reading_lexicon_docx.py`.
4. Validate it with `scripts/validate_reading_lexicon_docx.py`.
5. Return the absolute path to the final DOCX. Do not stop after presenting a word list or JSON.
6. If validation fails, fix the lexicon plan and rerun generation plus validation.

## IELTS Buddy Web Or MCP Hand-off

This workflow is local-first and does not require MCP. When IELTS Buddy MCP tools are available and the user explicitly wants selected terms saved to their personal vocabulary, use `ielts_vocabulary_personal_add` after the DOCX is validated. Vocabulary sync must not block local DOCX creation.

## Workflow

1. Identify the reading passage.
   - Normal input is a `.docx` reading passage or lesson document.
   - First run `scripts/extract_reading_docx.py Source.docx`.
   - Use `article_text` and `passage_paragraph_indices` from the extraction result.
   - If the DOCX also contains questions, answer choices, or notes, extract vocabulary from the passage section only unless the user asks otherwise.
2. Select 8-18 high-value items.
   - Prefer academic phrases, collocations, lexical chunks, discourse language, topic nouns, and precise verbs/adjectives.
   - Avoid basic single words unless the passage uses them in a high-value IELTS way.
   - Keep phrases verbatim, including spelling and inflection from the passage.
   - Deduplicate near-equivalent items and keep the strongest form.
3. Write learner notes.
   - `meaning`: short Chinese explanation, with enough precision for the passage context.
   - `usage`: how the phrase works in the source sentence and why it is useful.
   - `expansion`: 1-3 related forms, collocations, or reusable chunks.
   - `example`: one natural IELTS-style sentence using the phrase or a close reusable form.
   - `source_sentence`: the sentence from the passage that contains the phrase.
4. Generate a polished DOCX.
   - For input `Article.docx`, output `Article(lexicon).docx` in the same folder unless the user specifies another path.
   - Copy the original DOCX first and anchor Word comments to the selected phrases in the source passage.
   - Append a vocabulary handout after the passage: summary table, usage notes, and review prompts.
   - Use Times New Roman for generated text and `Cyber Esme` as the Word comment author.
   - Never overwrite the original DOCX unless explicitly requested.
5. Clean temporary files after successful validation.
   - Prefer creating lexicon plans in `/private/tmp`.
   - Delete temporary `lexicon_plan_*.json` files after validation.
   - Do not delete source DOCX files or final lexicon DOCX files.

## Bundled Resources

- `scripts/extract_reading_docx.py`: extract readable paragraphs, likely passage text, and paragraph indices from a DOCX.
- `scripts/create_reading_lexicon_docx.py`: create a polished Reading lexicon DOCX from a JSON plan; with DOCX input it copies the original, adds anchored comments, and appends the handout.
- `scripts/validate_reading_lexicon_docx.py`: verify required sections, verbatim phrase presence, Word comments, author, font, page break, and namespace safety.

## JSON Lexicon Plan For DOCX Creation

Create a JSON file with this shape:

```json
{
  "title": "雅思阅读词汇手册",
  "source_title": "The title of the reading passage",
  "passage_paragraph_indices": [1, 2, 3, 4, 5],
  "terms": [
    {
      "phrase": "verbatim phrase from the passage",
      "part_of_speech": "noun phrase",
      "category": "academic phrase",
      "band_value": "high",
      "meaning": "中文释义，贴合原文语境",
      "usage": "说明它在原句中的作用，以及为什么适合雅思阅读积累。",
      "expansion": ["相关形式", "可复用搭配"],
      "example": "A natural IELTS-style example sentence.",
      "source_sentence": "The full source sentence containing the phrase."
    }
  ],
  "review_prompts": [
    "用其中一个词组复述原文里的因果关系。"
  ]
}
```

Then run:

```bash
python scripts/create_reading_lexicon_docx.py lexicon_plan.json --input-docx Source.docx
python scripts/validate_reading_lexicon_docx.py "Source(lexicon).docx" --input-docx Source.docx --plan-json lexicon_plan.json
```

For pasted text only, still produce a DOCX:

```bash
python scripts/create_reading_lexicon_docx.py lexicon_plan.json
python scripts/validate_reading_lexicon_docx.py ~/Desktop/IELTS_Reading_Lexicon_YYYYMMDD_HHMM.docx --plan-json lexicon_plan.json
```

## Quality Bar

- The final answer must include the validated DOCX path.
- The output must be a polished Word document, not Markdown.
- Every selected `phrase` must appear in the source passage text.
- DOCX input should produce real Word comments anchored to the phrase, not bracketed inline notes.
- Notes must be concise and learnable, closer to a teacher's handout than a dictionary export.
- Examples must be natural IELTS/academic sentences and should not merely copy the source sentence.
- Review prompts must help the learner recall and reuse the selected phrases.
