import numpy as np
from pettingzoo.test import parallel_api_test

from swarm_lab.config import ExperimentConfig
from swarm_lab.environment import SwarmParallelEnv


def test_parallel_api_contract():
    parallel_api_test(SwarmParallelEnv(ExperimentConfig(max_steps=20)), num_cycles=40)


def test_observations_are_fixed_shape_anonymous_and_bounded():
    env = SwarmParallelEnv(ExperimentConfig(n_agents=5, observation_radius=3))
    observations, _ = env.reset(seed=22)
    assert {obs.shape for obs in observations.values()} == {(3, 7, 7)}
    assert all(obs.dtype == np.float32 for obs in observations.values())
    assert all(env.observation_space(agent).contains(obs) for agent, obs in observations.items())


def test_local_credit_only_rewards_collector():
    env = SwarmParallelEnv(ExperimentConfig(n_agents=2, n_targets=1, alpha=0, step_cost=0, max_steps=5))
    env.reset(seed=1)
    env.world.positions[:] = [(0, 0), (4, 4)]
    env.world.targets = {(1, 0)}
    _, rewards, terminations, _, infos = env.step({"agent_0": 3, "agent_1": 4})
    assert rewards == {"agent_0": 1.0, "agent_1": 0.0}
    assert infos["agent_0"]["local_collections"] == 1
    assert all(terminations.values())
    assert env.agents == []


def test_global_credit_is_shared():
    env = SwarmParallelEnv(ExperimentConfig(n_agents=2, n_targets=1, alpha=1, step_cost=0, max_steps=5))
    env.reset(seed=1)
    env.world.positions[:] = [(0, 0), (4, 4)]
    env.world.targets = {(1, 0)}
    _, rewards, _, _, _ = env.step({"agent_0": 3, "agent_1": 4})
    assert rewards == {"agent_0": 1.0, "agent_1": 1.0}


def test_sparse_global_credit_only_appears_on_completion():
    config = ExperimentConfig(n_agents=2, n_targets=2, alpha=1, step_cost=0, max_steps=5, reward_scheme="sparse")
    env = SwarmParallelEnv(config)
    env.reset(seed=1)
    env.world.positions[:] = [(0, 0), (4, 4)]
    env.world.targets = {(1, 0), (3, 4)}
    _, first_rewards, _, _, _ = env.step({"agent_0": 3, "agent_1": 4})
    assert first_rewards == {"agent_0": 0.0, "agent_1": 0.0}
    _, final_rewards, terminations, _, _ = env.step({"agent_0": 4, "agent_1": 2})
    assert final_rewards == {"agent_0": 1.0, "agent_1": 1.0}
    assert all(terminations.values())
