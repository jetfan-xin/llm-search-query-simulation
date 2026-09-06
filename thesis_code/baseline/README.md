# Baseline workspace

This directory mirrors the baseline workspace used by the thesis. `stopwords.txt` is retained because the lexical pipeline reads it directly. The numbered subdirectories hold two term-sampling configurations; their `corpus/` and `output/` contents remain private.

Corpus JSON maps each of the ten task IDs to token lists derived from task descriptions, search-result titles, snippets and OCR/page content. Although it is not a participant table, it can reproduce collected page text and remain linkable to research sessions, so only the schema is public.

Baseline output JSON stores ten sampled-query runs per task. CSV files record searched mixture weights (`alpha`, `beta`, `gamma`, `delta`) and BLEU values. These are generated artifacts rather than required source code.
