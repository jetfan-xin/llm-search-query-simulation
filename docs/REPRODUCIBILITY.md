# Reproducibility and known issues

## Supported review path

Python 3.10 or later is sufficient for the new offline utilities; they were tested locally with Python 3.13. No dependency installation is needed:

```bash
python3 -B tools/preview_prompt.py --variant standard --step 2
python3 -B tools/preview_prompt.py --variant no-feedback --step 2 --show-prompt
python3 -B -m unittest discover -s tests -v
python3 -B tools/verify_repository.py
```

The preview uses a fictional session and an explicitly synthetic replacement example. It loads only the historical `get_history` and `compose_prompt` methods, plus literal template definitions. It does not execute the historical constructor, SDK configuration, model requests or analysis entry points.

Tests cover nine preview variants, three query positions, omission of current/future queries, clicked-result selection and the relevant ablations. Passing them validates these narrow behaviours, **not the thesis's scientific conclusions or a live-generation run**.

## Historical environment

The thesis reports Python 3.8, an OpenAI Python client and the model `gpt-3.5-turbo-0125`. Imports establish use of jieba, NLTK, SciPy, pandas, PyTorch and BERTScore. Some preparation scripts also use SQLite. Exact package versions and a complete working environment were not preserved in the selected source.

[`thesis_code/requirements.txt`](../thesis_code/requirements.txt) is an explicitly reconstructed compatibility list, not an exact historical lockfile. It constrains `openai<1` because the original `openai.ChatCompletion` interface is intentionally retained. Current provider/model availability has not been tested, and no API requests were made during this review. The public code uses `OPENAI_API_KEY` and optional `OPENAI_API_BASE` configuration instead of recovered credentials.

## Repairs applied to the publication copy

The original source is traceable through [source-manifest.json](../source-manifest.json). The 2026 copy restores its comments and structure while fixing the following observed defects:

- prompt-module selection and the ablation/output label are configured together;
- missing output files initialise a resumable user/task structure;
- project data, baseline and evaluation paths resolve from `thesis_code/`;
- query-only extraction retains the query field;
- saved responses are parsed as JSON first, with the historical regular expression retained as a fallback;
- LLM and baseline cross-set Jaccard calculations enumerate the intended generated/reference pairs;
- baseline character-length sampling handles terms as strings, CSV ranking no longer skips a row, and `DataFrame.append` is replaced with `concat`.

These are maintenance repairs, not a rerun. Existing aggregate files and thesis tables continue to report the historical outputs.

## Remaining implementation and replication issues

| Area | Observed in retained source | Consequence |
| --- | --- | --- |
| Input versions | Reference data has 737 queries; standard simulation has 713 | Exact run cohorts must be recorded rather than inferred from the thesis total |
| Feedback timing | The collection protocol asks for query satisfaction and reasons retrospectively after the task | Earlier event records may contain hindsight; their annotations are not necessarily available at that point in a live session |
| Response processing | The JSON-first parser has not been validated against every retained private response | Unusual malformed layouts may still require manual review or regeneration |
| Baseline sampling | Integer corpus-list replication and a shifted Poisson are used | The code is more specific than the thesis's abstract mixture/Poisson description |
| Baseline parameter search | Retained loops fix the content weight to zero and truncate candidate settings | Do not describe this snapshot as exhaustive search across all four weights |
| Analysis entry points | Several modules perform data access or model initialisation at top level | Importing every historical module is not a safe smoke test |
| Historical provider/model | The pre-1.0 OpenAI client interface and `gpt-3.5-turbo-0125` identifier are retained | A live run depends on current provider-side compatibility and availability |

Remaining issues are documented rather than silently normalised. Publication repairs are recorded in the provenance/source manifests, and the 2026 preview remains separate from the thesis implementation.

## Metric interpretation

The original Jaccard routine tokenises Chinese text with jieba, removes stopwords, then retains tokens matching a Chinese-character pattern. A future evaluation must preserve or intentionally change that preprocessing and state which it uses.

The retained BLEU function passes raw strings. NLTK expects token sequences, so this call effectively evaluates character sequences; a word-tokenised replication would be a different configuration. See the official [NLTK BLEU API](https://www.nltk.org/api/nltk.translate.bleu_score.html).

BERTScore compares aligned candidate/reference texts using contextual token representations. The retained scripts use `bert-base-chinese`. Batch size controls processing batches, not set matching; model/tokenizer configuration must be recorded to compare results. See the official [BERTScore implementation and documentation](https://github.com/Tiiiger/bert_score).

These references were consulted for the 2026 review, not used to infer unrecorded historical software versions.

## Optional private-source audit

The archive owner can check original fingerprints and recompute the included aggregates with a local source map. Keep the map **outside** the repository:

```bash
python3 -B tools/audit_private_sources.py --source-map /local/path/to/private-source-index.json
```

The map is a JSON object containing `sources`, which maps the evidence IDs to absolute local file paths. The utility reads the specified files only and prints aggregate pass/fail checks, not participant rows. It writes no data and makes no network requests.

## What a later replication would require

1. Establish permission to use the participant data, examples and collected page content.
2. Freeze one input cohort and identify every included user/task/query step without exposing identifiers publicly.
3. Create a deterministic run configuration linking each prompt module, history-ablation setting, example, model and temperature.
4. Validate response parsing and record indexing/order against the authorised private files.
5. Resolve the remaining metric and baseline design issues above; document corrections as a **later replication**, preserving original reported results separately.
6. Evaluate all conditions on the same query set, separate tuning from evaluation, repeat stochastic runs and quantify uncertainty at appropriate session/participant levels.
7. Record dependency versions, model/tokenizer identifiers, data and prompt hashes, failure counts and exclusion rules.

Live provider calls, model downloads and an end-to-end rerun on private data remain outside this publication review.
