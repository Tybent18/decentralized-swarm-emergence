# Frozen baseline dataset

Run ID: `2026-09-15_baseline-v1`  
Generated: `2026-09-15T02:53:14.992859+00:00`  
Status: frozen heuristic baseline

Generated with:

```bash
python main.py collect --seeds 10 --output results/stage_one_baseline
```

The dataset contains 200 weakly shaped reward conditions spanning four fixed policies, five reward-mixing values, and ten seeds. The same seed intentionally repeats across α because heuristic actions do not learn from reward; this makes trajectory invariance an accounting control. Sparse terminal rewards are implemented and tested but reserved for the learned-policy experiment.

- `episodes.csv`: append-only episode evidence.
- `summary.csv`: means and sample standard deviations by policy and α.
- `manifest.json`: schema, environment, seed coverage, and claim boundary.
- `charts/`: regenerated visual summaries.

This is heuristic baseline evidence. It is not learned-policy or emergence evidence.
