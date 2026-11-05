# Machine-readable benchmark results

Start with [index.json](index.json). Each dataset entry contains a relative
download URL, its repository source, byte count, SHA-256, and number of items.
Resolve download URLs relative to the index URL. No GitHub login is required
for files served by this website.

The exports are generated automatically on each website deployment from the
saved results used by the site. They are not live experiment status feeds and
do not rerun analyses or regrade answers. To regenerate or check locally:

```sh
python3 export_site_results.py
python3 export_site_results.py --check
```

## BixBench

- [Results JSON](../bixbench/data/results.json)
- Per-item runs: `items[].results[experiment_id][condition_id][]`.
- Use `status`, not the historical `raw_status`, for reviewed pass/fail results.
- Aggregate accuracy and per-replicate statistics are under
  `experiments[experiment_id].conditions[condition_id]`.
- Exclude experiments with `superseded` metadata from the main comparison.
  Their results are retained for historical inspection, not pooled with the
  replacement experiment. Other separately published supplements are not
  automatically included in this main-summary export.

## CompBioBench

- [Results JSON](../compbiobench/data/paper_results.json)
- Per-item runs: `items[question_id].runs[model_id][condition_id][]`.
- Per-replicate official scores are under
  `models[].conditions[condition_id].replicates[].official_score`, out of 100.
  `predicted_score`, where present instead, is a prediction, not an official
  score. A missing score must not be silently treated as zero.
- Per-item `match`/`different` statuses compare against the evidence-based
  reference answers. Replicate-level match counts are not exported; use
  `official_score` for accuracy.
  Main and supplemental model configurations must be selected to match the
  intended figure, rather than indiscriminately pooled.
- [Token usage TSV](../compbiobench/data/public_token_usage.tsv)
- [UDT usage TSV](../compbiobench/data/public_udt_usage.tsv)

## IWC

- [Results JSON](../iwc/data/results.json)
- Per-item runs: `items[].results[model_id][condition_id][]`.
- Numeric accuracy is `acc`; preserve `acc_status` and null values rather
  than converting missing or unevaluated results to zero. `step_score` is a
  separate workflow-step metric, not a substitute for `acc`.
- This is the ten-item workflow-generation dataset shown in the public IWC
  section, not the multi-step tasks below.
- [Token usage TSV](../iwc/data/token_usage.tsv)

## IWC multi-step tasks

- [Results JSON](../iwc/long-chain/data/results.json)
- Per-task runs: `items[].runs[]`, one per model, condition and replicate, with
  `status` (`scored`, `rerunning`, or a not-yet-scored state) and the official
  `score` (`passed`, `denominator`, `acc` = passed/denominator, the continuous
  `mean`, and every result's score, pass decision and failure reasons).
- A result passes at a score of at least `pass_mark` (0.80) only when it also
  meets the required content, method and output instructions.
- Runs listed in `held_reruns` are being rerun: their earlier answers carry no
  score, and they are left out of every average until the new answers are
  scored. A missing score must not be treated as zero.
- The site averages `acc` over the scored runs of each task, then over tasks.

These files contain the website's published result records, including answer
and reference fields. They are intended for reporting and plotting, not for
use as inputs to agents participating in the benchmark.
