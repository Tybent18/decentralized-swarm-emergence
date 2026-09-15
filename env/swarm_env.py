from swarm_lab.config import ExperimentConfig
from swarm_lab.environment import SwarmParallelEnv


class SwarmEnv(SwarmParallelEnv):
    """Backward-compatible constructor for the corrected Stage One environment."""

    def __init__(
        self,
        grid_size=20,
        n_agents=5,
        n_targets=5,
        obs_radius=3,
        max_steps=200,
        reward_mode="hybrid",
        alpha=1.0,
        seed=0,
    ):
        if reward_mode == "global":
            alpha = 1.0
        elif reward_mode == "local":
            alpha = 0.0
        super().__init__(ExperimentConfig(grid_size, n_agents, n_targets, obs_radius, max_steps, alpha, seed=seed or 0))
