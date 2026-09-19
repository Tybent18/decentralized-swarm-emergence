# Learned Stage One: reward topology experiment

## Question

Does changing the balance between individual and team reward change learned decentralized coordination when agents cannot send messages?

## Experimental conditions

- Shared-policy PPO: every anonymous agent uses one parameter set.
- Independent PPO: each agent has its own parameter set.
- Reward α: `0`, `0.25`, `0.5`, `0.75`, and `1`.
- Direct communication: absent in every Stage One condition.
- Training and evaluation seeds: disjoint.
- Training updates, episodes per update, network size, optimizer, environment, and evaluation budget: matched.

The NumPy PPO implementation is intentionally compact and inspectable. It uses a one-hidden-layer actor-critic, clipped policy objective, generalized advantage estimation, value loss, entropy regularization, Adam, and gradient clipping.

## Confound controls

The normal `visible` condition contains radius-limited anonymous neighbor occupancy. Two optional controls test whether apparent coordination depends on infrastructure-provided neighbor geometry:

- `hidden`: removes the neighbor channel.
- `shuffled`: preserves neighbor count but deterministically corrupts its spatial arrangement.

These controls do not create a communication experiment. Stage Two will add explicit bounded messages as a new independent variable.

## Outcomes and decision rule

Primary outcomes are completion rate and coordination efficiency. The analysis also reports collision rate, steps, action entropy, spatial order, inter-agent distance, role differentiation, and return.

The hypothesis is unsupported if reward manipulation produces no meaningful coordination discrepancy. Support requires directional primary-outcome improvement, uncertainty that is inconsistent with zero for at least one primary outcome, a positive dose-response pattern, and robustness across training and evaluation seeds.

The initial five-point sweep cannot establish a critical α*, phase transition, learned language, or real-world emergence.

## Commands

Fast pipeline validation:

```bash
python main.py learn --pilot --output results/learned_pilot
```

Full registered sweep:

```bash
python main.py learn --updates 30 --episodes-per-update 4 \
  --train-seeds 3 --evaluation-seeds 5 \
  --output results/learned_stage_one
```

Add neighbor-information controls:

```bash
python main.py learn --neighbor-controls --output results/learned_with_controls
```

The manual **Learned Stage One Experiment** GitHub Actions workflow exposes the same budget and seed counts, then preserves the complete result directory as a downloadable artifact.

Inferential statistics use the mean held-out performance of each independently trained seed as one replicate. Individual evaluation episodes do not inflate the sample size.

Every run exports training curves, held-out evaluations, statistical analysis, a chart, model checkpoints, checksums, configuration, seeds, and an explicit claim boundary.
