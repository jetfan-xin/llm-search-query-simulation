# Prompt design

## Purpose

The prompt asks a model to behave as a search-engine user and formulate the next query for a specified information need. Its historical language is Chinese. This guide explains the design in English; it is not a replacement experimental prompt or a claim that an English-language study was conducted.

## Prompt components

| Component | Information supplied | Experimental question |
| --- | --- | --- |
| Role and task | Search-user role, task background and target | Can the model formulate a query rather than answer the task directly? |
| Profile | Demographic/background fields, search experience and pre-task ratings | Does user context improve query matching? |
| Prior queries | Queries from steps earlier than the target step | Can the model adapt the next query to the recorded search trajectory? |
| Recorded rationales | Verbal reasons given before earlier queries | Does access to these reports improve next-query simulation? |
| Observations | Titles and snippets of pages clicked in earlier steps | Does observed information help the next query? |
| Feedback | Satisfaction ratings and verbal feedback for earlier queries | Does expressed dissatisfaction or satisfaction help? |
| Demonstration | A separate example session | Does an example clarify behaviour or distract from the task? |
| Output contract | Query-only JSON or rationale-plus-query JSON | Does requiring an explicit rationale improve the resulting query? |

Verbal reports are participant-provided research observations, not direct measurements of internal cognition. Generated rationale text likewise is not proof that the model reproduces human thought processes.

## English structural illustration

```text
Role: Simulate a search-engine user gathering information.
Task: [background and information goal]
Profile: [optional user context and pre-task ratings]
History: [recorded interactions strictly before the target query]
Example: [optional, separately authorised demonstration]
Instruction: Formulate the query for step t.
Output: A structured query response, or a rationale-and-query response.
```

The illustration deliberately contains no real participant history or copied demonstration. Original embedded demonstrations were removed from the public code because their provenance and participant-release status could not be established. Consequently, the published prompt modules alone do not reproduce the exact historical few-shot condition.

## Retained naming conventions

- `prompt_library_s.py`: query-only standard prompt.
- `prompt_library_tol.py`: rationale-plus-query output.
- `wo_thought`, `wo_feedback`, `wo_observation`: remove corresponding historical context components; “thought” here refers to the recorded pre-query rationale.
- `wo_charactor*`: remove user-profile presentation; the historical spelling is preserved.
- `wo_guidance*`: remove the demonstration.
- Combined suffixes represent combined ablations. The `_s` forms belong to query-only variants where applicable.

## Important configuration issue

The archived simulator imports one prompt module statically while separately accepting a `prompt_type` label. Its saved entry point and imported module do not agree. Changing only the label therefore does not reliably switch the complete prompt condition.

The **2026 offline preview utility** uses an explicit variant-to-template mapping to keep these choices consistent during inspection. That mapping is a maintenance aid, not evidence of the original run configuration. A live replication should record the exact template hash, history-selection settings, model, temperature, output format and example version for every run.

## Why Chinese remains in the source

Translating the executable prompts would alter the experimental input. English explanations support recruiter and developer review, while retaining the original task/prompt wording preserves the inspectable implementation. The preview fixture and its replacement demonstration are synthetic and clearly labelled; they must not be scored or cited as historical research observations.
