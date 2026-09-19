# Research roadmap

The long-range research space is `E(α,b,N)`: reward topology, communication bandwidth, and swarm scale. Claims advance only when the corresponding implementation, frozen data, and statistical test exist.

**Current status:** see [Current Research State & Experimental Transition](current-research-state.md) for the bridge between frozen heuristic evidence, the implemented learned-policy runner, and the active α experiment.

## True Stage One - experimental foundation (implemented)

- deterministic world physics and seeded layouts;
- fixed-shape anonymous local observations;
- PettingZoo Parallel API contract;
- literal local, global, and hybrid α reward credit;
- random, greedy, flocking, and oracle baselines;
- performance and behavioral metrics;
- trajectory overlays, heatmaps, charts, raw CSV, summaries, and manifests;
- live simulation, safe cancellation, one-click collection, and read-only GitHub evidence export;
- correctness and reproducibility tests.

Stage One establishes instrumentation and baseline separation. It does not demonstrate learned emergence.

## Stage Two - learning baselines (runner implemented; evidence collection active)

- single-agent training sanity check;
- Independent PPO;
- shared-policy PPO;
- identical training budgets and environment distributions;
- checkpoint provenance and evaluation-only seeds;
- optional hidden and spatially shuffled neighbor-information controls.

The executable learned-policy runner is implemented. Pilot execution validates the pipeline but does not satisfy the exit criterion.

Exit criterion: reproducible learned-policy checkpoints that outperform or meaningfully differ from frozen heuristic baselines.

## Stage Three - emergence experiment

- pre-registered α grid and seed count;
- multiple-comparison-aware statistical testing;
- emergence curve with confidence intervals;
- behavioral structure analysis and reward-exploitation checks;
- estimate α* only if the registered criterion is met.

Exit criterion: evidence supporting or rejecting an α-dependent coordination transition.

## Stage Four - communication bandwidth

- no-message control;
- scalar and bounded-vector messages;
- local and broadcast topologies;
- information-cost accounting.

Exit criterion: measured effect of bandwidth `b` on efficiency and convergence.

## Stage Five - scale and resilience

- registered agent counts beyond the 5–10 agent capstone setting;
- 10–30% randomized failure interventions;
- observation noise and latency;
- compute/memory/runtime profiling.

Exit criterion: bounded claims about robustness and scaling, not an assumed “100-agent” victory lap.

## Stage Six - unified phase space

Combine validated axes into empirical `E(α,b,N)` diagrams. Critical thresholds and phase-transition language remain hypotheses until supported by repeatable evidence.

> Guiding rule: no new complexity without instrumentation, and no result claim without frozen evidence.
