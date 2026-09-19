"""Minimal NumPy PPO implementation for the no-communication Stage One experiment.

The implementation is deliberately small and inspectable. It supports a shared policy
across anonymous agents or one independent policy per agent under identical budgets.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .environment import SwarmParallelEnv


@dataclass(frozen=True)
class PPOBudget:
    updates: int = 30
    episodes_per_update: int = 4
    epochs: int = 4
    hidden_size: int = 48
    learning_rate: float = 3e-3
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_ratio: float = 0.2
    value_coefficient: float = 0.5
    entropy_coefficient: float = 0.01
    max_grad_norm: float = 0.7

    def __post_init__(self):
        if min(self.updates, self.episodes_per_update, self.epochs, self.hidden_size) < 1:
            raise ValueError("PPO counts and hidden_size must be positive")
        if not 0 < self.learning_rate or not 0 <= self.clip_ratio < 1:
            raise ValueError("invalid PPO learning parameters")


class Adam:
    def __init__(self, parameters, learning_rate):
        self.parameters = parameters
        self.learning_rate = learning_rate
        self.m = {name: np.zeros_like(value) for name, value in parameters.items()}
        self.v = {name: np.zeros_like(value) for name, value in parameters.items()}
        self.step_count = 0

    def step(self, gradients):
        self.step_count += 1
        for name, gradient in gradients.items():
            self.m[name] = 0.9 * self.m[name] + 0.1 * gradient
            self.v[name] = 0.999 * self.v[name] + 0.001 * gradient**2
            m_hat = self.m[name] / (1 - 0.9**self.step_count)
            v_hat = self.v[name] / (1 - 0.999**self.step_count)
            self.parameters[name] -= self.learning_rate * m_hat / (np.sqrt(v_hat) + 1e-8)


class PPOModel:
    def __init__(self, observation_size, action_count, hidden_size, seed, learning_rate):
        rng = np.random.default_rng(seed)
        self.parameters = {
            "w1": rng.normal(0, np.sqrt(2 / observation_size), (observation_size, hidden_size)),
            "b1": np.zeros(hidden_size),
            "wp": rng.normal(0, 0.08, (hidden_size, action_count)),
            "bp": np.zeros(action_count),
            "wv": rng.normal(0, 0.08, hidden_size),
            "bv": np.zeros(1),
        }
        self.optimizer = Adam(self.parameters, learning_rate)

    def forward(self, observations):
        hidden = np.tanh(observations @ self.parameters["w1"] + self.parameters["b1"])
        logits = hidden @ self.parameters["wp"] + self.parameters["bp"]
        logits -= logits.max(axis=-1, keepdims=True)
        probabilities = np.exp(logits)
        probabilities /= probabilities.sum(axis=-1, keepdims=True)
        values = hidden @ self.parameters["wv"] + self.parameters["bv"][0]
        return hidden, probabilities, values

    def act(self, observation, rng, deterministic=False):
        flat = np.asarray(observation, dtype=np.float64).reshape(1, -1)
        _, probabilities, values = self.forward(flat)
        if deterministic:
            action = int(np.argmax(probabilities[0]))
        else:
            action = int(rng.choice(len(probabilities[0]), p=probabilities[0]))
        return action, float(np.log(probabilities[0, action] + 1e-12)), float(values[0])

    def update(self, batch, budget):
        observations, actions, old_log_probs, advantages, returns = batch
        if not len(observations):
            return {"policy_loss": 0.0, "value_loss": 0.0, "entropy": 0.0}
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        last_metrics = {}
        for _ in range(budget.epochs):
            hidden, probabilities, values = self.forward(observations)
            selected = probabilities[np.arange(len(actions)), actions]
            log_probs = np.log(selected + 1e-12)
            ratios = np.exp(log_probs - old_log_probs)
            unclipped = ratios * advantages
            clipped = np.clip(ratios, 1 - budget.clip_ratio, 1 + budget.clip_ratio) * advantages
            choose_unclipped = unclipped <= clipped
            policy_coeff = np.where(choose_unclipped, -advantages * ratios, 0.0) / len(actions)

            one_hot = np.zeros_like(probabilities)
            one_hot[np.arange(len(actions)), actions] = 1.0
            grad_logits = policy_coeff[:, None] * (one_hot - probabilities)

            # Entropy regularization: dH/dz = -p * (log(p) + H).
            entropy_each = -np.sum(probabilities * np.log(probabilities + 1e-12), axis=1)
            grad_logits += (
                budget.entropy_coefficient
                * probabilities
                * (np.log(probabilities + 1e-12) + entropy_each[:, None])
                / len(actions)
            )

            value_error = values - returns
            grad_values = budget.value_coefficient * 2 * value_error / len(actions)
            gradients = {
                "wp": hidden.T @ grad_logits,
                "bp": grad_logits.sum(axis=0),
                "wv": hidden.T @ grad_values,
                "bv": np.asarray([grad_values.sum()]),
            }
            grad_hidden = grad_logits @ self.parameters["wp"].T + grad_values[:, None] * self.parameters["wv"][None, :]
            grad_pre = grad_hidden * (1 - hidden**2)
            gradients["w1"] = observations.T @ grad_pre
            gradients["b1"] = grad_pre.sum(axis=0)

            norm = np.sqrt(sum(float(np.sum(gradient**2)) for gradient in gradients.values()))
            if norm > budget.max_grad_norm:
                gradients = {
                    name: gradient * budget.max_grad_norm / (norm + 1e-12) for name, gradient in gradients.items()
                }
            self.optimizer.step(gradients)
            last_metrics = {
                "policy_loss": float(-np.mean(np.minimum(unclipped, clipped))),
                "value_loss": float(np.mean(value_error**2)),
                "entropy": float(np.mean(entropy_each)),
            }
        return last_metrics

    def save(self, path):
        np.savez_compressed(path, **self.parameters)


class PPOSystem:
    def __init__(self, config, architecture, budget, seed):
        if architecture not in {"shared", "independent"}:
            raise ValueError("architecture must be 'shared' or 'independent'")
        self.architecture = architecture
        observation_size = 3 * (2 * config.observation_radius + 1) ** 2
        count = 1 if architecture == "shared" else config.n_agents
        self.models = [
            PPOModel(observation_size, 5, budget.hidden_size, seed + index * 997, budget.learning_rate)
            for index in range(count)
        ]

    def model_index(self, agent_name):
        return 0 if self.architecture == "shared" else int(agent_name.rsplit("_", 1)[1])

    def act(self, agent_name, observation, rng, deterministic=False):
        return self.models[self.model_index(agent_name)].act(observation, rng, deterministic)

    def save(self, directory):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        for index, model in enumerate(self.models):
            model.save(directory / f"policy_{index}.npz")


def _advantages(trajectory, gamma, gae_lambda):
    advantages = np.zeros(len(trajectory), dtype=np.float64)
    gae = 0.0
    next_value = 0.0
    for index in range(len(trajectory) - 1, -1, -1):
        transition = trajectory[index]
        delta = transition[3] + gamma * next_value * (1 - transition[4]) - transition[2]
        gae = delta + gamma * gae_lambda * (1 - transition[4]) * gae
        advantages[index] = gae
        next_value = transition[2]
    returns = advantages + np.asarray([transition[2] for transition in trajectory])
    return advantages, returns


def collect_training_episode(config, system, seed, deterministic=False):
    env = SwarmParallelEnv(config)
    observations, _ = env.reset(seed=seed)
    rng = np.random.default_rng(seed + 50_000)
    trajectories = {agent: [] for agent in env.possible_agents}
    total_reward = 0.0
    collisions = 0
    while env.agents:
        actions, metadata = {}, {}
        for agent in env.agents:
            action, log_prob, value = system.act(agent, observations[agent], rng, deterministic)
            actions[agent] = action
            metadata[agent] = (observations[agent].reshape(-1).astype(np.float64), action, value, log_prob)
        next_observations, rewards, terminations, truncations, infos = env.step(actions)
        for agent in metadata:
            observation, action, value, log_prob = metadata[agent]
            done = bool(terminations[agent] or truncations[agent])
            trajectories[agent].append((observation, action, value, float(rewards[agent]), done, log_prob))
            total_reward += float(rewards[agent])
            collisions += int(infos[agent]["attempted_collisions"])
        observations = next_observations
    return trajectories, {
        "success": int(not env.world.targets),
        "steps": env.world.step_count,
        "completion_rate": env.total_collected / config.n_targets,
        "team_return": total_reward,
        "attempted_collisions": collisions // max(config.n_agents, 1),
    }


def train_ppo(config, architecture, budget, train_seed, progress=None):
    system = PPOSystem(config, architecture, budget, train_seed)
    progress = progress or (lambda *_: None)
    history = []
    for update in range(budget.updates):
        grouped = [[] for _ in system.models]
        episode_metrics = []
        for episode in range(budget.episodes_per_update):
            seed = train_seed * 1_000_003 + update * budget.episodes_per_update + episode
            trajectories, metrics = collect_training_episode(config, system, seed)
            episode_metrics.append(metrics)
            for agent, trajectory in trajectories.items():
                advantages, returns = _advantages(trajectory, budget.gamma, budget.gae_lambda)
                model_index = system.model_index(agent)
                for transition, advantage, return_value in zip(trajectory, advantages, returns):
                    grouped[model_index].append((transition[0], transition[1], transition[5], advantage, return_value))
        losses = []
        for model, records in zip(system.models, grouped):
            arrays = tuple(np.asarray(values) for values in zip(*records))
            losses.append(model.update(arrays, budget))
        record = {
            "update": update + 1,
            "mean_success": float(np.mean([item["success"] for item in episode_metrics])),
            "mean_completion": float(np.mean([item["completion_rate"] for item in episode_metrics])),
            "mean_steps": float(np.mean([item["steps"] for item in episode_metrics])),
            "mean_return": float(np.mean([item["team_return"] for item in episode_metrics])),
            "policy_loss": float(np.mean([item["policy_loss"] for item in losses])),
            "value_loss": float(np.mean([item["value_loss"] for item in losses])),
            "entropy": float(np.mean([item["entropy"] for item in losses])),
        }
        history.append(record)
        progress(record, (update + 1) / budget.updates)
    return system, history


def budget_dict(budget):
    return asdict(budget)
