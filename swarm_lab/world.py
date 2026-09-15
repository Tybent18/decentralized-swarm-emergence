from dataclasses import dataclass

import numpy as np

MOVES = np.asarray(((0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)), dtype=np.int16)


@dataclass(frozen=True)
class StepEvent:
    collectors: dict[int, int]
    attempted_collisions: int
    moved: dict[int, int]


class SwarmWorld:
    """Deterministic grid physics shared by the UI and PettingZoo adapter."""

    def __init__(self, grid_size=16, n_agents=6, n_targets=8, seed=7):
        self.grid_size = int(grid_size)
        self.n_agents = int(n_agents)
        self.n_targets = int(n_targets)
        self.rng = np.random.default_rng(seed)
        self.positions = np.zeros((n_agents, 2), dtype=np.int16)
        self.targets: set[tuple[int, int]] = set()
        self.trajectories: list[list[tuple[int, int]]] = []
        self.step_count = 0
        self.reset(seed)

    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        cells = self.rng.choice(self.grid_size**2, self.n_agents + self.n_targets, replace=False)
        xy = np.column_stack((cells % self.grid_size, cells // self.grid_size)).astype(np.int16)
        self.positions = xy[: self.n_agents]
        self.targets = {tuple(map(int, p)) for p in xy[self.n_agents :]}
        self.trajectories = [[tuple(map(int, p))] for p in self.positions]
        self.step_count = 0
        return self.snapshot()

    def step(self, actions: dict[int, int]):
        self.step_count += 1
        old = self.positions.copy()
        proposed = old.copy()
        for idx in range(self.n_agents):
            action = int(actions.get(idx, 4))
            if not 0 <= action < len(MOVES):
                raise ValueError(f"invalid action {action} for agent {idx}")
            proposed[idx] = np.clip(old[idx] + MOVES[action], 0, self.grid_size - 1)

        _, counts = np.unique(proposed, axis=0, return_counts=True)
        attempted_collisions = int(np.maximum(counts - 1, 0).sum())
        self.positions = proposed
        moved = {idx: int(np.any(old[idx] != proposed[idx])) for idx in range(self.n_agents)}
        collectors = {idx: 0 for idx in range(self.n_agents)}
        remaining = set(self.targets)
        for idx, pos in enumerate(self.positions):
            point = tuple(map(int, pos))
            if point in remaining:
                collectors[idx] += 1
                remaining.remove(point)
        self.targets = remaining
        for idx, pos in enumerate(self.positions):
            self.trajectories[idx].append(tuple(map(int, pos)))
        return StepEvent(collectors, attempted_collisions, moved)

    def snapshot(self):
        return {
            "agents": [tuple(map(int, p)) for p in self.positions],
            "targets": sorted(self.targets),
            "step": self.step_count,
        }
