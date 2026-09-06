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

The illustration deliberately contains no real participant history. The thesis-era embedded demonstrations are retained in `thesis_code/` because they were part of the prompt configuration, but specific age, programme and related profile fields were replaced with `[REDACTED]` to reduce re-identification risk. The separate offline preview overrides them with an entirely synthetic demonstration.

## Retained naming conventions

- `prompt_library_s.py`: query-only standard prompt.
- `prompt_library_tol.py`: rationale-plus-query output.
- `wo_thought`, `wo_feedback`, `wo_observation`: remove corresponding historical context components; “thought” here refers to the recorded pre-query rationale.
- `wo_charactor*`: remove user-profile presentation; the historical spelling is preserved.
- `wo_guidance*`: remove the demonstration.
- Combined suffixes represent combined ablations. The `_s` forms belong to query-only variants where applicable.

## Historical configuration issue and repair

The original simulator imported one prompt module statically while separately accepting a `prompt_type` label. Its saved entry point and imported module did not agree, so changing only the label did not reliably switch the complete condition.

The publication copy fixes this with an explicit variant-to-template mapping in `simulator.py`; the **2026 offline preview utility** maintains its own equivalent mapping so it can run without importing the SDK. This repair is not evidence of the exact historical run configuration. A live replication should still record the template hash, history-selection settings, model, temperature, output format and example version for every run.

## Why Chinese remains in the source

Translating the executable prompts would alter the experimental input. English explanations support recruiter and developer review, while retaining the original task/prompt wording preserves the inspectable implementation. Only the profile fields marked `[REDACTED]` differ for privacy. The preview fixture and its replacement demonstration are synthetic and clearly labelled; they must not be scored or cited as historical research observations.
