# Visible reward-topology sweep v1

Run ID: `2026-09-19_visible-reward-topology-v1`  
Generated: `2026-09-19T22:09:31.712795+00:00`  
Protocol: `experiments/stage_one_learned.json`  
Status: completed; preregistered positive-direction hypothesis unsupported

## Scope

- 2 architectures: shared PPO and Independent PPO
- 5 reward weights: α = 0, 0.25, 0.5, 0.75, and 1
- 3 independent training seeds per condition
- 30 updates × 4 training episodes per policy
- 5 held-out evaluation seeds per trained policy
- 30 trained policies and 150 evaluation episodes
- visible anonymous neighbor channel; no direct communication

## Files

- `training.csv`: 900 update-level training records
- `evaluations.csv`: 150 held-out evaluation episodes
- `analysis.csv`: policy-seed-level inference
- `manifest.json`: exact configuration, seeds, timestamps, checksums, and claim boundary
- `charts/learned_reward_topology.png`: primary-outcome visualization

See [`docs/learned-stage-one-results.md`](../../../../docs/learned-stage-one-results.md) for the interpretation and limitations.
