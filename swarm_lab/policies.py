import numpy as np

from .world import MOVES


def _toward(source, target, rng):
    delta = np.asarray(target) - np.asarray(source)
    choices = []
    if delta[1] < 0:
        choices.append(0)
    if delta[1] > 0:
        choices.append(1)
    if delta[0] < 0:
        choices.append(2)
    if delta[0] > 0:
        choices.append(3)
    return int(rng.choice(choices)) if choices else 4


def random_policy(world, rng):
    return {i: int(rng.integers(0, 5)) for i in range(world.n_agents)}


def greedy_policy(world, rng):
    if not world.targets:
        return {i: 4 for i in range(world.n_agents)}
    targets = list(world.targets)
    return {
        i: _toward(pos, min(targets, key=lambda t: abs(t[0] - pos[0]) + abs(t[1] - pos[1])), rng)
        for i, pos in enumerate(world.positions)
    }


def distributed_greedy_policy(world, rng):
    """Deterministic oracle baseline that prevents duplicate target pursuit."""
    available = set(world.targets)
    actions = {}
    order = sorted(range(world.n_agents), key=lambda i: (int(world.positions[i][0]), int(world.positions[i][1])))
    for i in order:
        if not available:
            actions[i] = 4
            continue
        pos = world.positions[i]
        target = min(available, key=lambda t: (abs(t[0] - pos[0]) + abs(t[1] - pos[1]), t))
        available.remove(target)
        actions[i] = _toward(pos, target, rng)
    return actions


def flocking_policy(world, rng):
    """Rule-based cohesion/separation baseline with target attraction."""
    if not world.targets:
        return {i: 4 for i in range(world.n_agents)}
    actions = {}
    for i, pos in enumerate(world.positions):
        distances = np.abs(world.positions - pos).sum(axis=1)
        crowded = [j for j, d in enumerate(distances) if j != i and d <= 1]
        if crowded:
            center = world.positions[crowded].mean(axis=0)
            delta = pos - center
            scores = MOVES @ delta
            actions[i] = int(np.argmax(scores[:4]))
        else:
            target = min(world.targets, key=lambda t: abs(t[0] - pos[0]) + abs(t[1] - pos[1]))
            actions[i] = _toward(pos, target, rng)
    return actions


POLICIES = {
    "random": random_policy,
    "greedy": greedy_policy,
    "flocking": flocking_policy,
    "distributed-greedy": distributed_greedy_policy,
}
