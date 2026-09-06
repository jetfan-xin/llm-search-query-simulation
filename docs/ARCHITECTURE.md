# Architecture and code map

## Research objective

The simulator predicts the query at position `t` from a task, a user profile and the recorded interactions preceding `t`. A fresh model request is constructed for each position. Earlier context comes from the human record, not from a rollout of earlier model-generated queries. This distinction is explicit in thesis section 4.2.1 and in `GenerateQuery.get_history`.

The design is inspired by ReAct's combination of language and action, but the retained experiment is narrower than an autonomous tool-using agent. It generates queries; it does not independently simulate clicks, stopping decisions or real-time browsing.

## Data flow

1. **Prepare the research records.** Organise participant/task/session JSON, check missing annotations and extract indexed queries.
2. **Construct the context for one query.** Convert profile scales to text and select only earlier query steps. For each earlier step, the builder can include a verbal rationale, the query, clicked-page titles/snippets and satisfaction feedback.
3. **Assemble the prompt.** Combine the task, optional profile, optional demonstration and history with the output-format instruction.
4. **Generate and process the response.** Request an LLM completion and extract query text from the saved response.
5. **Evaluate.** Compare generated and recorded queries, analyse within-task diversity and task-description similarity, and inspect initial versus later queries.

The corpus extractor separately prepares baseline inputs from task descriptions, search-result titles, snippets and OCR-derived page text, using SQLite query identifiers to connect records to OCR folders.

## Implementation map

| Component | Historical file | Responsibility |
| --- | --- | --- |
| Main simulator | [`simulator.py`](../thesis_code/simulator.py) | History selection, prompt assembly, provider call and saved-output logic |
| Prompt variants | [`prompt_library_s.py`](../thesis_code/prompt_library_s.py) and related modules | Task definitions, profile/history fields and ablated output instructions |
| Corpus preparation | [`baseline_corpus_extractor.py`](../thesis_code/baseline_corpus_extractor.py) | Build task-description, title, snippet and OCR-content term corpora |
| Probabilistic baselines | [`baseline_simulator_simplified.py`](../thesis_code/baseline_simulator_simplified.py) | Sample terms and query lengths; search corpus-weight settings |
| Record checks | [`check_completion.py`](../thesis_code/check_completion.py) | Count available rationale/feedback annotations and clicked pages |
| Query extraction | [`extract_query.py`](../thesis_code/extract_query.py) | Convert research records to indexed query structures |
| Response processing | [`clean_answers.py`](../thesis_code/clean_answers.py) | Extract generated query/rationale fields and record problematic steps |
| Lexical evaluation | [`evaluation_jaccard.py`](../thesis_code/evaluation_jaccard.py), [`evaluation_bleu.py`](../thesis_code/evaluation_bleu.py) | Overlap comparisons and short-text BLEU |
| Semantic evaluation | [`evaluation_bert_2.py`](../thesis_code/evaluation_bert_2.py) | BERTScore with a Chinese encoder, including first/later-query breakdowns |
| Additional analysis | Other `evaluation_bert*`, `evaluation_bl`, `statastic_information`, `user_for_query_times` modules | Alternative evaluation routines and descriptive analysis |

The names and alternative scripts are retained to make archive tracing possible; they are not an assertion that every script is part of a single polished package.

## Data shape

The original simulator consumes a list of user records, each with profile fields and a `task` mapping. Each task includes pre-task ratings and a `content` mapping of recorded query events. Relevant event fields are:

- `query`: the observed human query.
- `thought`: a transcribed pre-query verbal report, when available.
- `SERP`: result items, including title, snippet and a click indicator.
- `satisfaction` and `satisfaction_thought`: post-query rating and verbal feedback, when available.

The actual exports also contain direct identifiers. They are not included. The public [synthetic fixture](../examples/synthetic_session.json) omits identifiers such as names, email addresses and student numbers and is not a participant record.

Selecting earlier event records does not establish that every annotation was available at that time. In the collection protocol, satisfaction feedback was elicited retrospectively after task completion, so it may reflect hindsight. The offline tests check record selection, not the causal timing of human annotations.

## Research code versus review utilities

`thesis_code/` is a sanitised copy of the original 2024 implementation and retains its data, baseline, evaluation, utility and notebook topology. Empty documented directories show where the excluded private inputs and record-level outputs belong. Privacy and correctness changes are fingerprinted in the manifest and summarised in the directory README. `tools/` and `tests/` were added in 2026 and remain separate. The preview utility bypasses file-dependent initialisation and all provider calls; it is a narrow behavioural check, not a replacement simulator claimed as the thesis experiment.
