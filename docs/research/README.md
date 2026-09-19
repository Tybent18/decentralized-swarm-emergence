# Swarm research library

[← Project home](../../README.md) · **[Current research state](../current-research-state.md)** · [Stage One results](../stage-one-results.md) · [Learned Stage One](../learned-stage-one.md) · [Methods](../stage-one-methods.md) · [Roadmap](../roadmap.md)

This library separates implemented evidence from future research scope. Start with the **[Current Research State & Experimental Transition](../current-research-state.md)** for the shortest accurate explanation of where the program stands, then read the Stage One report for measured results, the learned-policy protocol for the active registered experiment, and the three-tier sequence for the expanding research agenda.

## Evidence and next experiment

| Document | Role | Evidence status |
| --- | --- | --- |
| [Current Research State & Experimental Transition](../current-research-state.md) | Bridge from frozen heuristic evidence to the learned α experiment and later `b`/`N` stages | Living status/navigation document; makes no new empirical claim |
| [True Stage One Technical Report](stage-one-technical-report.pdf) | Frozen report for the implemented environment, heuristic baselines, instrumentation, and 200-condition dataset | Measured Stage One evidence |
| [Pre-Registered Experimental Protocol](experimental-protocol.pdf) | Shared-policy PPO versus Independent PPO across the reward-topology sweep | Planned confirmatory experiment; no learned-policy result claimed |
| [Learned Stage One protocol](../learned-stage-one.md) | Executable reward-topology experiment, controls, outcomes, and decision rule | Runner implemented; confirmatory evidence pending frozen sweep |

## Research progression

| Tier | Document | Scope |
| --- | --- | --- |
| 1 | [Capstone: Emergent Intelligence in Decentralized Swarms](tier-1-capstone.pdf) | Reward topology, partial observability, and learned coordination |
| 2 | [Master's: Minimal Communication Protocols](tier-2-masters.pdf) | Information budgets, topology, and emergent communication |
| 3 | [Doctoral Agenda: Formal Models and Scalable Intelligence](tier-3-doctoral-agenda.pdf) | Information flow, robustness, control architecture, and scaling limits |

## Claim boundary

The current repository validates environment semantics, observation constraints, reward accounting, heuristic baseline separation, repeatability, and evidence export. It also contains the shared-policy and Independent PPO experimental runner and neighbor-information controls. Those implementations make the learned reward-topology hypothesis testable; they do not yet establish learned emergence, a critical reward threshold, learned communication, or large-swarm robustness.

The older V1–V3 papers remain available in [`docs/papers`](../papers/) as historical project artifacts. These revised documents are the current research packet aligned with True Stage One.

