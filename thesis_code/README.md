# 2024 thesis implementation

This directory is a **sanitised copy of the original thesis implementation**. It is the project's research code, not a deprecated predecessor to another simulator in this repository. Original filenames, Chinese prompts, comments and the working-directory layout are retained wherever disclosure permits.

## What changed for publication

- Hardcoded API keys and a private API base URL were replaced by `OPENAI_API_KEY` and optional `OPENAI_API_BASE` environment variables. The historical `openai.ChatCompletion` / `openai.Completion` calls remain unchanged.
- Specific age, programme and related profile fields in embedded demonstrations were replaced with `[REDACTED]`. The prompt structure, demonstration interactions and task text remain available.
- Notebook outputs, execution counters and machine-specific absolute paths were removed; code cells remain.
- `utils/crawler.py` is represented by an attribution note rather than copied because the archived file is byte-identical to the adjacent third-party WebAgentFSM project.
- Participant/session exports, collected pages, SQLite data and record-level metric arrays are represented by documented directories instead of public records.

## Repairs made in 2026

The publication copy fixes several concrete defects while retaining the thesis-era design:

- `simulator.py` now selects a prompt module and history-ablation label together, initialises or resumes its output structure, and resolves its `data/` directory from the script location.
- `simulator2.py` imports the surviving standard prompt module and also resolves `data/` from the script location.
- `extract_query.py` now writes the query field in query-only mode.
- `clean_answers.py` first parses the requested JSON format, falls back to the historical regular expression for malformed saved responses, and writes output once after processing.
- Cross-set Jaccard calculations now enumerate the complete generated-by-reference Cartesian product; the LLM cross-query routine no longer compares the generated set with itself.
- The character-length baseline uses string terms rather than one-item lists, no longer relies on removed `DataFrame.append`, and no longer skips a CSV row while ranking.

These repairs are publication-era maintenance, not a claim that the 2024 experiments were rerun. Metric definitions and historical result tables remain unchanged.

## Directory layout

```text
thesis_code/
├── simulator.py                 # main history-conditioned LLM simulator
├── prompt_library_*.py          # standard prompt and ablation variants
├── baseline_corpus_extractor.py # corpus preparation
├── baseline_simulator_simplified.py
├── extract_query.py / clean_answers.py
├── evaluation_*.py              # lexical and semantic evaluation
├── *.ipynb                      # output-free plotting/review notebooks
├── data/                        # private inputs and saved model responses
├── baseline/                    # stopwords, private corpora and baseline outputs
├── evaluation/                  # private record-level metric outputs
└── utils/                       # additional analysis scripts and attribution
```

Each private-data directory contains a README describing its expected files, schema and disclosure status. Copy authorised files into those locations without committing them; `.gitignore` protects their contents.

## Historical environment and invocation

The thesis reports Python 3.8 and `gpt-3.5-turbo-0125`. Exact package versions were not archived. [`requirements.txt`](requirements.txt) therefore lists compatibility constraints rather than pretending to be an exact historical lockfile. The legacy OpenAI API requires the pre-1.0 Python client.

```bash
python3.8 -m venv .venv
source .venv/bin/activate
pip install -r thesis_code/requirements.txt
export OPENAI_API_KEY=your_key
# Optional when using a compatible proxy:
# export OPENAI_API_BASE=https://your-authorised-endpoint.example/v1

python thesis_code/simulator.py
```

`simulator.py` defaults to `thesis_code/data/data0405.json`; set `THESIS_INPUT_FILE` to another filename placed in that directory. A live call may still depend on provider-side availability of the historical model. Run the dependency-free synthetic review path from the repository root before using private data:

```bash
python3 -B tools/preview_prompt.py --variant standard --step 2
python3 -B -m unittest discover -s tests -v
python3 -B tools/verify_repository.py
```
