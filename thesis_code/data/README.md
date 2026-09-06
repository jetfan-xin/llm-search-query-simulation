# Private research data

This directory is the location expected by the thesis scripts. Its actual contents are excluded from the public repository and ignored by Git.

The archived directory contains several related data families:

- `data_update0302.json` is the 737-query reference export used by baseline preparation and descriptive checks.
- `data0405.json` is the 713-query / 290-session input used by the retained standard simulation and evaluation path.
- `extracted_original_data_*.json` files contain indexed reference queries, optionally with pre-query rationales.
- `output_data_*.json` files contain raw LLM responses organised by user, task and query step.
- `cleaned_*.json` files contain parsed generated queries and, for applicable conditions, generated rationale text.
- `regenerated.json` lists user/task/step keys whose saved responses could not be parsed and required another generation attempt.
- `db.sqlite3` and OCR/page-content directories support corpus construction and connect search-result identifiers with collected page text.

The main JSON input is a list of user records. Each record includes a study identifier and profile attributes such as gender, age bracket/age, academic field and search experience. Its `task` mapping contains pre-task knowledge, interest and difficulty ratings plus an ordered `content` mapping. Query events contain the human query, optional pre-query verbal report, search-result titles/snippets and click flags, and optional satisfaction rating/feedback.

These files may contain direct identifiers, linkable demographic combinations, verbatim queries and verbal reports, browsing traces, collected page text and model outputs derived from them. They must not be committed without a separate consent and de-identification review. The public [`examples/synthetic_session.json`](../../examples/synthetic_session.json) documents the shape without reproducing a participant.
