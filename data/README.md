# Experimental data catalog

Every committed dataset is organized by experiment family and then by an immutable dated run ID:

```text
data/<experiment_id>/runs/YYYY-MM-DD_<condition>-vN/
```

Dates are UTC collection dates taken from each generated manifest. A run directory is never reused for a later collection. Replications, ablations, and changed protocols receive new run IDs.

| UTC date | Run ID | Experiment | Condition | Status | Evidence |
|---|---|---|---|---|---|
| 2026-09-15 | `2026-09-15_baseline-v1` | Stage One heuristic baseline | Four fixed policies; weak reward accounting | Frozen baseline | [Open run](stage_one_baseline/runs/2026-09-15_baseline-v1/) |
| 2026-09-19 | `2026-09-19_visible-reward-topology-v1` | Learned Stage One | Visible neighbors; α sweep; shared and independent PPO | Completed; positive-direction hypothesis unsupported | [Open run](learned_stage_one/runs/2026-09-19_visible-reward-topology-v1/) |

Each run contains a manifest with its run ID, exact generation timestamp, protocol/schema version, configuration, seeds, evidence status, and claim boundary. Derived charts live inside the same dated run as their source CSV files.

Scratch runs, pilots, and incomplete jobs remain under ignored `results/` paths and are not part of this evidence catalog.
