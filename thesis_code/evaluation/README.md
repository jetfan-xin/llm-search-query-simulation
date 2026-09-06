# Record-level evaluation workspace

The thesis scripts write full score arrays here. The public `results/` directory contains checked aggregates; this workspace is intentionally empty apart from documentation because per-query arrays preserve ordering and can be linked back to participant/task/query steps.

- `jaccard/` contains within-set, cross-set, query-to-task and paired generated/reference Jaccard arrays.
- `bleu/` contains per-task, first-query and later-query BLEU arrays.
- `bert/` contains the equivalent BERTScore arrays and summaries using `bert-base-chinese`.
- `new/` contains long-form CSV tables used to draw the nested ablation boxplots (`name`, query-position group and metric value).

Do not commit restored files without a separate disclosure review. The folder-specific README files list the expected artifact families.
