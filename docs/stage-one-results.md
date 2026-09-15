# Frozen Stage One baseline results

## Dataset

The frozen dataset records 200 policy/reward conditions: four policies, five α settings, and ten seeds. Because each heuristic policy is reward-independent, the ten seeds at one α provide the distinct behavioral samples for between-policy comparisons; repeated α conditions validate reward accounting.

## Observed baseline separation

| Policy | Success rate | Completion rate | Steps | Total distance | Collision rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Random | 0.10 | 0.70 | 174.8 | 787.7 | 0.0086 |
| Greedy | 1.00 | 1.00 | 13.5 | 81.0 | 0.0659 |
| Flocking | 1.00 | 1.00 | 16.5 | 90.9 | 0.1109 |
| Distributed-greedy oracle | 1.00 | 1.00 | 34.9 | 87.4 | 0.0637 |

Across ten independent seeds at α=0.5, greedy completion exceeded random completion in a Welch comparison (`t=-4.609`, `p=0.00127`). This shows that the task and measurement stack discriminate structured heuristics from the stochastic control. It does not show learned coordination or emergence.

## What the results support

- The environment runs repeatably across independent seeds.
- The baseline policies create measurably different task behavior.
- The collector exports complete performance and behavioral telemetry.
- Reward topology changes recorded return without silently altering fixed-policy trajectories.
- The platform is ready to receive shared-policy and Independent PPO baselines.

## What the results do not support

- No trained PPO policy has been evaluated.
- No α-dependent behavioral transition has been measured.
- No critical threshold α* has been estimated.
- No learned communication or bandwidth threshold has been evaluated.
- No large-swarm or agent-failure robustness claim is made.

These exclusions are research controls, not missing footnotes. The next paper-grade result must compare learned policies against these frozen baselines under identical training budgets.
