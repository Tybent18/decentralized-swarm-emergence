from functools import lru_cache

import gymnasium.spaces as spaces
import numpy as np
from pettingzoo.utils import ParallelEnv

from .config import ExperimentConfig
from .world import SwarmWorld


class SwarmParallelEnv(ParallelEnv):
    """PettingZoo environment with anonymous, fixed-shape local observations."""

    metadata = {"name": "decentralized_swarm_stage_one_v1", "render_modes": []}

    def __init__(self, config=None):
        self.config = config or ExperimentConfig()
        self.possible_agents = [f"agent_{i}" for i in range(self.config.n_agents)]
        self.agents = []
        self.world = SwarmWorld(self.config.grid_size, self.config.n_agents, self.config.n_targets, self.config.seed)
        self.total_collected = 0

    @lru_cache(maxsize=None)
    def observation_space(self, _agent):
        side = 2 * self.config.observation_radius + 1
        return spaces.Box(0, 1, shape=(3, side, side), dtype=np.float32)

    @lru_cache(maxsize=None)
    def action_space(self, _agent):
        return spaces.Discrete(5)

    def reset(self, seed=None, options=None):
        del options
        self.agents = self.possible_agents[:]
        self.world.reset(self.config.seed if seed is None else seed)
        self.total_collected = 0
        return {a: self._observe(i) for i, a in enumerate(self.agents)}, {a: {} for a in self.agents}

    def step(self, actions):
        if not self.agents:
            raise RuntimeError("step called after episode ended; call reset")
        live_agents = self.agents[:]
        event = self.world.step({i: actions.get(a, 4) for i, a in enumerate(live_agents)})
        collected = sum(event.collectors.values())
        self.total_collected += collected
        complete = not self.world.targets
        truncated = self.world.step_count >= self.config.max_steps and not complete
        global_signal = float(complete) if self.config.reward_scheme == "sparse" else float(collected)
        team_reward = global_signal - self.config.step_cost
        rewards, infos = {}, {}
        for i, agent in enumerate(live_agents):
            local_reward = float(event.collectors[i]) - self.config.step_cost
            rewards[agent] = self.config.alpha * team_reward + (1 - self.config.alpha) * local_reward
            infos[agent] = {
                "local_collections": event.collectors[i],
                "team_collections": collected,
                "attempted_collisions": event.attempted_collisions,
                "moved": event.moved[i],
                "reward_scheme": self.config.reward_scheme,
            }
        terminations = {a: complete for a in live_agents}
        truncations = {a: truncated for a in live_agents}
        observations = {a: self._observe(i) for i, a in enumerate(live_agents)}
        if complete or truncated:
            self.agents = []
        return observations, rewards, terminations, truncations, infos

    def _observe(self, agent_index):
        radius = self.config.observation_radius
        side = 2 * radius + 1
        obs = np.zeros((3, side, side), dtype=np.float32)
        center = self.world.positions[agent_index]
        obs[0, radius, radius] = 1.0
        for other_index, pos in enumerate(self.world.positions):
            if other_index == agent_index:
                continue
            dx, dy = pos - center
            if abs(dx) <= radius and abs(dy) <= radius:
                obs[1, int(dy + radius), int(dx + radius)] = 1.0
        if self.config.neighbor_mode == "hidden":
            obs[1] = 0.0
        elif self.config.neighbor_mode == "shuffled":
            # Deterministic spatial corruption preserves neighbor count but destroys geometry.
            shift = 1 + ((self.world.step_count + agent_index + self.config.seed) % max(side - 1, 1))
            obs[1] = np.roll(obs[1], shift=shift, axis=(0, 1))
        for tx, ty in self.world.targets:
            dx, dy = tx - int(center[0]), ty - int(center[1])
            if abs(dx) <= radius and abs(dy) <= radius:
                obs[2, dy + radius, dx + radius] = 1.0
        return obs
