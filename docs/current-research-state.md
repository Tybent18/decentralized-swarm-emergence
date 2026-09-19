# Current research state and experimental transition

[← Project home](../README.md) · [Stage One results](stage-one-results.md) · [Learned Stage One protocol](learned-stage-one.md) · [Methods](stage-one-methods.md) · [Roadmap](roadmap.md) · [Research library](research/README.md)

## Purpose

This document is the bridge between the frozen heuristic Stage One evidence and the learned-policy reward-topology experiment. It answers one question: **where is the research now, what has actually been established, and what experiment comes next?**

The long-range program studies an empirical coordination space (E(α,b,N)), where (α) controls reward topology, (b) controls explicit communication bandwidth, and (N) controls swarm scale. Those axes are introduced sequentially so that a later result cannot be used to retroactively rescue an earlier hypothesis.

## 1. Current research question

The present capstone-stage question is:

> **Does changing the balance between individual and team reward change learned decentralized coordination when agents have only radius-limited anonymous observations and no explicit messaging channel?**

Stage One isolates reward topology (α). Communication bandwidth (b) and large-scale robustness (N) remain later experiments.

## 2. What the frozen heuristic baseline established

The committed Stage One baseline contains 200 recorded conditions: four fixed policies × five α values × ten seeds.

It supports the following bounded claims:

- the environment executes repeatably across independent seeds;
- anonymous local observations and PettingZoo parallel semantics are implemented and tested;
- local, global, and hybrid reward attribution is instrumented correctly;
- random, greedy, flocking, and distributed-greedy-oracle policies produce discriminable behavior;
- the collector exports performance, behavioral, trajectory, heatmap, summary, and provenance evidence;
- at α=0.5, greedy completion differs from the random control in the reported Welch comparison (`t=-4.609`, `p=0.00127`).

That comparison demonstrates that the task and measurement stack can distinguish structured heuristic behavior from a stochastic control. It does **not** demonstrate learned coordination or emergence.

## 3. Why the heuristic α sweep does not test the central hypothesis

The frozen heuristic policies do not update their actions from reward. For a fixed policy and seed, changing α therefore changes recorded return but should not change the trajectory.

Conceptually:

[
α \rightarrow \text{reward accounting}
]

is already tested, while the capstone hypothesis requires:

[
α \rightarrow \text{learning} \rightarrow \text{behavior}
]

The repeated α conditions in the heuristic baseline are therefore a reward-accounting invariant and experimental control, not evidence of an α-dependent coordination transition.

## 4. Experimental transition now implemented

The repository now contains a learned-policy runner for:

- **shared-policy PPO**, where anonymous agents use one parameter set;
- **Independent PPO**, where agents use separate parameter sets;
- α ∈ {0, 0.25, 0.5, 0.75, 1};
- matched training budgets and environment distributions;
- disjoint training and evaluation seeds;
- checkpoint provenance and exported evidence;
- optional visible, hidden, and spatially shuffled neighbor-information controls.

This implementation makes the central reward-topology hypothesis experimentally addressable. **Implementation is not itself confirmatory evidence.** The registered sweep must be collected, frozen, and interpreted under its declared decision criteria before a learned-emergence claim is considered.

See [Learned Stage One](learned-stage-one.md) and the machine-readable criteria in [`experiments/stage_one_learned.json`](../experiments/stage_one_learned.json).

## 5. What counts as coordination evidence

Higher reward alone is not treated as coordination. Primary learned-policy outcomes are:

- completion rate;
- coordination efficiency.

Supporting diagnostics include:

- collision rate;
- steps;
- action entropy;
- spatial order;
- mean inter-agent distance;
- role differentiation;
- return.

The inferential unit is an independently trained policy seed. Held-out evaluation episodes are averaged within that unit rather than counted as independent replicates.

The registered learned-policy hypothesis is unsupported if reward manipulation produces no meaningful coordination discrepancy. The current decision rule requires directional primary-outcome improvement, uncertainty inconsistent with zero for at least one primary outcome, a positive dose-response pattern, and robustness across training and evaluation seeds.

## 6. Distinguishing interaction from correlated behavior

Even an α-dependent behavioral change would not automatically prove that agents are coordinating *with one another*. Agents can respond similarly to shared incentives or environmental structure without meaningful inter-agent dependence.

The optional neighbor controls provide an initial intervention:

| Condition | Information available | Interpretation |
| --- | --- | --- |
| Visible | Normal anonymous local neighbor geometry | Reference learned condition |
| Hidden | Neighbor channel removed | Tests dependence on observable neighbors |
| Shuffled | Neighbor count preserved but spatial arrangement corrupted | Tests dependence on meaningful neighbor geometry |

If a coordination-like effect survives destruction of meaningful neighbor information, the result may be better explained by shared reward/environmental adaptation than by interaction-dependent coordination.

These controls are **not** an explicit communication experiment.

## 7. Falsification and claim boundary

The capstone reward-topology hypothesis is not protected from a negative result.

It fails to receive support under the registered experiment if α does not produce the predefined meaningful learned-policy coordination discrepancy across controlled training and held-out evaluation seeds.

A later communication result cannot retroactively make the α hypothesis successful. Likewise, an observed α effect does not establish:

- a universal critical threshold α*;
- a thermodynamic-style phase transition;
- learned language;
- explicit message semantics;
- real-world swarm behavior;
- robustness at large (N).

The five-point learned sweep can support or reject a bounded α-dependent coordination effect under the implemented conditions. Stronger threshold language requires denser registered sampling and replication.

## 8. Why communication comes later

After the no-message reward-topology experiment is characterized, the next research axis is explicit communication bandwidth (b).

The communication stage will compare conditions such as:

- no-message control;
- scalar or bounded-vector messages;
- local versus broadcast topology;
- information-cost accounting.

If learned messages later appear behaviorally meaningful, causal interventions can distinguish message presence from message function—for example suppression, shuffled authentic messages, matched random messages, replay in altered states, and cross-run transfer. Until those tests exist, the appropriate term is **emergent communication protocol**, not learned language.

## 9. Scaling and resilience come after communication

The (N) axis asks whether observed mechanisms survive changes in swarm size and operating conditions. Planned tests include larger registered agent counts, randomized agent failures, observation noise, latency, and compute/memory/runtime profiling.

The objective is not to assume that a mechanism scales. It is to identify where it stops working and under what conditions.

## 10. Research flow

```text
TRUE STAGE ONE SUBSTRATE
environment + observations + reward accounting + frozen heuristics
                         │
                         ▼
LEARNED REWARD-TOPOLOGY EXPERIMENT (α)
Does incentive structure change learned decentralized coordination?
                         │
                         ▼
COMMUNICATION BANDWIDTH (b)
How much explicit information exchange changes coordination?
                         │
                         ▼
SCALE + RESILIENCE (N)
Do the observed mechanisms survive growth, noise, and failure?
                         │
                         ▼
EMPIRICAL PHASE SPACE E(α,b,N)
Only axes supported by frozen evidence are combined.
```

## 11. Current status at a glance

| Component | Status | What may currently be claimed |
| --- | --- | --- |
| Environment / observation semantics | Implemented and tested | Experimental substrate is reproducible |
| Heuristic baselines | Frozen evidence | Structured heuristics are discriminable from stochastic control |
| α reward accounting | Frozen evidence | Reward topology is implemented without silently changing fixed-policy trajectories |
| Shared-policy / Independent PPO runner | Implemented | Learned experiment can be executed under matched budgets |
| Registered learned α sweep | Collection/confirmatory evidence pending | No α-dependent learned-emergence result yet |
| Neighbor-information controls | Implemented option | Can test dependence on meaningful neighbor geometry when collected |
| Explicit communication bandwidth (b) | Future stage | No communication or language claim |
| Scaling/resilience (N) | Future stage | No large-swarm robustness claim |
| (E(α,b,N)) | Long-range synthesis | Research scaffold, not an established phase diagram |

## 12. Reading order

For the shortest accurate path through the repository:

1. **This document** — current state and transition.
2. [Frozen Stage One results](stage-one-results.md) — what has actually been measured.
3. [Learned Stage One protocol](learned-stage-one.md) — the experiment that tests the capstone hypothesis.
4. [Research roadmap](roadmap.md) — later (b), (N), and (E(α,b,N)) stages.
5. [Research library](research/README.md) — formal reports and Capstone → Master's → Doctoral progression.

> **Guiding rule:** implementation makes a hypothesis testable; frozen evidence makes a result claimable.
