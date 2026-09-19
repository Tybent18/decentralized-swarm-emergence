from dataclasses import replace

import numpy as np

from swarm_lab.config import ExperimentConfig
from swarm_lab.environment import SwarmParallelEnv
from swarm_lab.learned_experiment import LearnedExperiment
from swarm_lab.learning import PPOBudget, PPOSystem, train_ppo


def small_config(**changes):
    base = ExperimentConfig(grid_size=7, n_agents=3, n_targets=2, observation_radius=2, max_steps=18)
    return replace(base, **changes)


def test_shared_and_independent_parameterization():
    budget = PPOBudget(updates=1, episodes_per_update=1, epochs=1, hidden_size=8)
    assert len(PPOSystem(small_config(), "shared", budget, 1).models) == 1
    assert len(PPOSystem(small_config(), "independent", budget, 1).models) == 3


def test_training_updates_policy_parameters():
    config = small_config()
    budget = PPOBudget(updates=2, episodes_per_update=2, epochs=2, hidden_size=12)
    initial = PPOSystem(config, "shared", budget, 9).models[0].parameters["wp"].copy()
    trained, history = train_ppo(config, "shared", budget, 9)
    assert len(history) == 2
    assert not np.allclose(initial, trained.models[0].parameters["wp"])


def test_training_is_seed_reproducible():
    config = small_config()
    budget = PPOBudget(updates=1, episodes_per_update=2, epochs=1, hidden_size=8)
    first, first_history = train_ppo(config, "shared", budget, 17)
    second, second_history = train_ppo(config, "shared", budget, 17)
    assert first_history == second_history
    for name in first.models[0].parameters:
        assert np.array_equal(first.models[0].parameters[name], second.models[0].parameters[name])


def test_neighbor_controls_preserve_shape_and_change_channel():
    visible = SwarmParallelEnv(small_config(neighbor_mode="visible"))
    hidden = SwarmParallelEnv(small_config(neighbor_mode="hidden"))
    visible_obs, _ = visible.reset(seed=4)
    hidden_obs, _ = hidden.reset(seed=4)
    assert visible_obs["agent_0"].shape == hidden_obs["agent_0"].shape
    assert hidden_obs["agent_0"][1].sum() == 0


def test_learned_experiment_exports_evidence(tmp_path):
    budget = PPOBudget(updates=1, episodes_per_update=1, epochs=1, hidden_size=8)
    outputs = LearnedExperiment(tmp_path).run(
        alphas=(0.0, 1.0),
        train_seeds=(0,),
        evaluation_seeds=(100, 101),
        architectures=("shared",),
        base_config=small_config(),
        budget=budget,
    )
    assert all(path.exists() and path.stat().st_size > 0 for path in outputs.values())
    assert (tmp_path / "checkpoints" / "visible" / "shared" / "alpha_0" / "seed_0" / "policy_0.npz").exists()
