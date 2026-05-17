# Terminology — Decentralized Swarm Emergence

This document defines all core variables, metrics, and conceptual constructs used across the swarm emergence research system.

All definitions are fixed across experiments unless explicitly versioned.

---

## 1. Core System Variables

### α — Reward Mixing Parameter
Controls the balance between global and local reward signals.

- α = 0 → fully local/self-interested behavior
- α = 1 → fully global coordination objective
- 0 < α < 1 → hybrid reward shaping regime

Used to study how incentive structure affects emergent coordination.

---

### b — Communication Bandwidth
Represents the maximum information exchange capacity between agents.

Defined as a constrained communication channel:

- message dimensionality
- quantization level
- or token budget per timestep

Lower b → higher information restriction  
Higher b → richer coordination signaling

---

### N — System Scale
Number of agents in the environment.

- Small N → limited interaction graph
- Large N → high-dimensional coordination dynamics

Used to study scalability and robustness of emergence.

---

## 2. Environment Terms

### Episode
A single rollout of the environment from initialization to termination condition.

Termination occurs when:
- all targets are collected, or
- maximum timestep is reached

---

### Target
A discrete spatial objective that agents must collect.

Properties:
- static per timestep
- removed upon collection
- respawned only at episode reset (in baseline versions)

---

### Agent
A decentralized decision-making entity with:

- local observation only
- shared or independent policy
- no global state access

Agents are homogeneous unless otherwise specified.

---

### Grid World
Discrete 2D spatial environment:

- size: typically 20×20
- movement: cardinal directions (N, S, E, W)
- optional: obstacle layers (future extensions)

---

## 3. Observation & Action Space

### Observation Tensor
Local spatial representation of environment state.

Typical shape:
```
(C, k, k)
```

Where:
- C = number of feature channels
- k = local observation window size

Includes:
- nearby agents
- nearby targets
- optional obstacle layer

No global coordinates or agent IDs are permitted.

---

### Action Space
Discrete control set:

- North
- South
- East
- West
- Stay (optional)

Continuous variants are not used in baseline experiments.

---

## 4. Reward System

### Global Reward
Shared reward signal across all agents.

Example:
- +1 if all targets are collected
- 0 otherwise

Encodes full-system success objective.

---

### Local Reward
Per-agent reward signal.

Example:
- +1 when agent collects a target

Encodes self-interested behavior.

---

### Hybrid Reward
Weighted combination of global and local signals:

- α controls mixing ratio
- enables continuous transition between coordination regimes

---

### Reward Topology
The structural design of reward distribution across agents.

Key research variable determining coordination emergence.

---

## 5. Coordination Metrics

### Coordination Efficiency
Primary performance metric.

Defined as:

- task success normalized by total movement cost

Captures both:
- effectiveness (success)
- efficiency (energy / motion cost)

---

### Emergence
A system exhibits emergence when:

- coordinated behavior appears
- without explicit coordination mechanisms
- and significantly outperforms baseline heuristics (p < 0.05)

---

### Emergence Curve
Function describing coordination efficiency as a function of α:

E(α)

Used to identify phase-transition-like behavior.

---

### Critical Threshold (α*)
Smallest α such that:

- coordination > baseline
- statistically significant across runs

Represents transition point from disorder → coordination.

---

## 6. Communication Terms

### Message
Information emitted by an agent to other agents.

Constraints:
- may be continuous or discrete
- subject to bandwidth limit b

---

### Communication Topology
Structure defining how agents exchange messages:

- broadcast (fully connected)
- local (neighborhood-based)
- graph-based (dynamic connectivity)

---

### Bandwidth Threshold (b*)
Minimum communication capacity required for:

- statistically significant improvement over no-communication baseline

---

## 7. Emergence & Analysis Terms

### Role Differentiation
Degree to which agents spontaneously specialize.

Measured via:
- behavioral clustering
- trajectory similarity
- task contribution variance

---

### Spatial Order Parameter
Quantifies structure in agent motion.

Captures:
- alignment
- clustering
- dispersion

---

### Policy Entropy
Measures randomness vs convergence in policy outputs.

High entropy → exploration  
Low entropy → convergence

---

### Phase Transition
Abrupt qualitative change in system behavior caused by continuous parameter variation (α, b, or N).

---

## 8. System-Level Model

### Unified Emergence Function

```
E = f(α, b, N)
```

Where:
- α = reward structure
- b = communication constraint
- N = system scale

This defines the full experimental search space.

---

## 9. Statistical Definitions

### Statistical Significance
All claims of emergence require:

- p < 0.05
- across multiple independent seeds (≥ 5–10 runs)

---

### Baseline Comparison
Performance must exceed:

- greedy heuristic
- random policy
- simple rule-based swarm

---

## Guiding Principle

If a concept is not defined here, it should not appear in:

- code
- experiments
- analysis
- claims