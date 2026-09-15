# True Stage One methods

## Purpose

True Stage One creates the trustworthy experimental substrate required by the capstone. It measures deterministic heuristic and stochastic control policies before any reinforcement-learning results are introduced.

## Environment

- Discrete 16×16 grid by default.
- Six agents and eight targets by default; agent count is configurable.
- Simultaneous five-action movement: north, south, west, east, or stay.
- Unique seeded spawn cells prevent initialization overlap.
- An episode terminates when every target is collected and truncates at the configured step budget.
- Multiple agents may occupy a cell; attempted co-location is measured as collision pressure.

## Observation contract

Each agent receives an anonymous tensor with shape `(3, 2r+1, 2r+1)`: ego location at the tensor center, nearby-agent occupancy, and nearby-target occupancy. No absolute position or agent identifier appears in the observation. The fixed shape allows later shared-policy training without padding ambiguity.

## Reward topology

The environment supports both capstone global conditions: `weak` supplies per-target team credit and `sparse` supplies one terminal team credit only when every target is collected. For agent `i`, the hybrid reward is:

`r_i = α(global_signal - step_cost) + (1-α)(local_collections_i - step_cost)`

At `α=0`, only the collecting agent receives collection credit. At `α=1`, collection credit is shared. This corrects the legacy implementation, where every local agent received the step-level team collection count.

## Baselines

- **Random:** stochastic control.
- **Greedy:** every agent pursues its nearest target independently.
- **Flocking:** target attraction with a local separation rule.
- **Distributed-greedy oracle:** globally assigns distinct targets and provides a reference baseline. It is explicitly labeled an oracle, not a decentralized learned policy.

## Metrics

Every episode records success, steps, targets collected, completion rate, total distance, distance per target, coordination efficiency, attempted collisions, collision rate, action entropy, spatial order, mean inter-agent distance, role differentiation, and team return.

Coordination efficiency follows the capstone definition as binary task success divided by total movement cost. Completion rate and distance per target remain informative when an episode fails.

## Reproducibility

World generation and policy randomness use separate NumPy generators derived from the recorded seed. The collector stores raw rows, aggregated means and sample standard deviations, environment metadata, seed coverage, and an explicit claim boundary in `manifest.json`.

## Interpretation boundary

Heuristic policy actions do not update from reward. Therefore changing α should change calculated return but not behavior for the same policy and seed. The α-dependent emergence curve must be measured only after learned policies are trained under controlled budgets. Stage One does not estimate α*.
