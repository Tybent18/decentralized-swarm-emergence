"""Controlled learned-policy experiment for reward-topology effects."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from .config import ExperimentConfig
from .environment import SwarmParallelEnv
from .learning import PPOBudget, budget_dict, train_ppo
from .metrics import action_entropy, mean_pairwise_distance, role_differentiation, spatial_order


@dataclass(frozen=True)
class LearnedEpisode:
    architecture: str
    alpha: float
    train_seed: int
    evaluation_seed: int
    neighbor_mode: str
    success: int
    steps: int
    completion_rate: float
    total_distance: int
    coordination_efficiency: float
    attempted_collisions: int
    collision_rate: float
    action_entropy: float
    spatial_order: float
    mean_interagent_distance: float
    role_differentiation: float
    team_return: float


def evaluate_policy(config, system, seed):
    env = SwarmParallelEnv(config)
    observations, _ = env.reset(seed=seed)
    rng = np.random.default_rng(seed + 700_001)
    actions_taken, order_values, distance_values = [], [], []
    contributions = np.zeros(config.n_agents, dtype=int)
    movements = np.zeros(config.n_agents, dtype=int)
    total_reward = 0.0
    collisions = 0
    while env.agents:
        actions = {agent: system.act(agent, observations[agent], rng, deterministic=True)[0] for agent in env.agents}
        observations, rewards, _terminations, _truncations, infos = env.step(actions)
        actions_taken.extend(actions.values())
        total_reward += sum(rewards.values())
        any_info = next(iter(infos.values()))
        collisions += int(any_info["attempted_collisions"])
        for agent, info in infos.items():
            index = int(agent.rsplit("_", 1)[1])
            contributions[index] += int(info["local_collections"])
            movements[index] += int(info["moved"])
        order_values.append(spatial_order(env.world.trajectories))
        distance_values.append(mean_pairwise_distance(env.world.positions))
    total_distance = int(movements.sum())
    success = int(not env.world.targets)
    return {
        "success": success,
        "steps": env.world.step_count,
        "completion_rate": env.total_collected / config.n_targets,
        "total_distance": total_distance,
        "coordination_efficiency": success / max(total_distance, 1),
        "attempted_collisions": collisions,
        "collision_rate": collisions / max(config.n_agents * env.world.step_count, 1),
        "action_entropy": action_entropy(actions_taken),
        "spatial_order": float(np.mean(order_values)) if order_values else 0.0,
        "mean_interagent_distance": float(np.mean(distance_values)) if distance_values else 0.0,
        "role_differentiation": role_differentiation(contributions, movements),
        "team_return": float(total_reward),
    }


def _write_csv(path, rows):
    if not rows:
        return
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _bootstrap_difference(low, high, seed=19, draws=4000):
    low, high = np.asarray(low, dtype=float), np.asarray(high, dtype=float)
    rng = np.random.default_rng(seed)
    differences = np.empty(draws)
    for index in range(draws):
        differences[index] = (
            rng.choice(high, len(high), replace=True).mean() - rng.choice(low, len(low), replace=True).mean()
        )
    return float(np.quantile(differences, 0.025)), float(np.quantile(differences, 0.975))


def analyze(rows):
    analyses = []
    for architecture in sorted({row["architecture"] for row in rows}):
        visible = [row for row in rows if row["architecture"] == architecture and row["neighbor_mode"] == "visible"]
        alphas = sorted({float(row["alpha"]) for row in visible})
        for metric in ("completion_rate", "coordination_efficiency", "collision_rate"):
            # Trained policies are the independent units. Held-out episodes
            # characterize a policy; they do not create extra replicates.
            grouped = {}
            for row in visible:
                key = (float(row["alpha"]), int(row["train_seed"]))
                grouped.setdefault(key, []).append(float(row[metric]))
            policy_means = {key: float(np.mean(values)) for key, values in grouped.items()}
            low = [value for (alpha, _seed), value in policy_means.items() if alpha == min(alphas)]
            high = [value for (alpha, _seed), value in policy_means.items() if alpha == max(alphas)]
            low_mean, high_mean = np.mean(low), np.mean(high)
            if len(low) > 1 and len(high) > 1:
                pooled = np.sqrt(
                    ((len(low) - 1) * np.var(low, ddof=1) + (len(high) - 1) * np.var(high, ddof=1))
                    / (len(low) + len(high) - 2)
                )
            else:
                pooled = 0.0
            effect = float((high_mean - low_mean) / pooled) if pooled > 0 else 0.0
            if len(low) < 2 or len(high) < 2:
                welch_p = float("nan")
            elif np.isclose(np.std(low), 0.0) and np.isclose(np.std(high), 0.0):
                welch_p = 1.0 if low_mean == high_mean else 0.0
            else:
                welch_p = float(stats.ttest_ind(high, low, equal_var=False).pvalue)
            alpha_means = [
                np.mean([value for (row_alpha, _seed), value in policy_means.items() if row_alpha == alpha])
                for alpha in alphas
            ]
            if np.ptp(alpha_means) == 0:
                rho, rho_p = float("nan"), float("nan")
            else:
                rho, rho_p = stats.spearmanr(alphas, alpha_means)
            ci_low, ci_high = _bootstrap_difference(low, high)
            analyses.append(
                {
                    "architecture": architecture,
                    "metric": metric,
                    "replication_unit": "train_seed_policy_mean",
                    "n_low": len(low),
                    "n_high": len(high),
                    "alpha_low": min(alphas),
                    "alpha_high": max(alphas),
                    "low_mean": float(low_mean),
                    "high_mean": float(high_mean),
                    "difference": float(high_mean - low_mean),
                    "bootstrap_ci_low": ci_low,
                    "bootstrap_ci_high": ci_high,
                    "standardized_effect": effect,
                    "welch_p": welch_p,
                    "spearman_rho": float(rho) if np.isfinite(rho) else 0.0,
                    "spearman_p": float(rho_p) if np.isfinite(rho_p) else 1.0,
                }
            )
    return analyses


def export_chart(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    style = {
        "figure.facecolor": "#07111f",
        "axes.facecolor": "#0d1b2d",
        "axes.edgecolor": "#334155",
        "axes.labelcolor": "#cbd5e1",
        "xtick.color": "#94a3b8",
        "ytick.color": "#94a3b8",
        "text.color": "#e2e8f0",
    }
    visible = [row for row in rows if row["neighbor_mode"] == "visible"]
    with plt.rc_context(style):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
        for architecture, color in (("shared", "#38bdf8"), ("independent", "#a78bfa")):
            subset = [row for row in visible if row["architecture"] == architecture]
            alphas = sorted({float(row["alpha"]) for row in subset})
            for axis, metric in zip(axes, ("completion_rate", "coordination_efficiency")):
                means, errors = [], []
                for alpha in alphas:
                    values = np.asarray([float(row[metric]) for row in subset if float(row["alpha"]) == alpha])
                    means.append(values.mean())
                    errors.append(values.std(ddof=1) / np.sqrt(len(values)) if len(values) > 1 else 0.0)
                axis.errorbar(alphas, means, yerr=errors, marker="o", capsize=3, color=color, label=architecture)
        axes[0].set(
            title="Learned completion by reward topology", xlabel="alpha", ylabel="completion rate", ylim=(-0.03, 1.03)
        )
        axes[1].set(title="Learned coordination efficiency", xlabel="alpha", ylabel="success / movement")
        for axis in axes:
            axis.grid(alpha=0.35)
            axis.legend(frameon=False)
        fig.savefig(path, dpi=170)
        plt.close(fig)
    return path


class LearnedExperiment:
    def __init__(self, output_dir, progress=None):
        self.output_dir = Path(output_dir)
        self.progress = progress or (lambda *_: None)

    def run(
        self,
        alphas=(0.0, 0.25, 0.5, 0.75, 1.0),
        train_seeds=(0, 1, 2),
        evaluation_seeds=(100, 101, 102, 103, 104),
        architectures=("shared", "independent"),
        neighbor_modes=("visible",),
        base_config=None,
        budget=None,
    ):
        base_config = base_config or ExperimentConfig(
            grid_size=10, n_agents=6, n_targets=6, observation_radius=3, max_steps=100
        )
        budget = budget or PPOBudget()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_root = self.output_dir / "checkpoints"
        training_rows, evaluation_rows = [], []
        combinations = [
            (architecture, float(alpha), int(train_seed), neighbor_mode)
            for neighbor_mode in neighbor_modes
            for architecture in architectures
            for alpha in alphas
            for train_seed in train_seeds
        ]
        for combination_index, (architecture, alpha, train_seed, neighbor_mode) in enumerate(combinations, 1):
            config = ExperimentConfig(
                **{
                    **base_config.to_dict(),
                    "alpha": alpha,
                    "seed": train_seed,
                    "neighbor_mode": neighbor_mode,
                }
            )
            model, history = train_ppo(config, architecture, budget, train_seed)
            for record in history:
                training_rows.append(
                    {
                        "architecture": architecture,
                        "alpha": alpha,
                        "train_seed": train_seed,
                        "neighbor_mode": neighbor_mode,
                        **record,
                    }
                )
            checkpoint_dir = checkpoint_root / neighbor_mode / architecture / f"alpha_{alpha:g}" / f"seed_{train_seed}"
            model.save(checkpoint_dir)
            for evaluation_seed in evaluation_seeds:
                evaluation_config = ExperimentConfig(**{**config.to_dict(), "seed": int(evaluation_seed)})
                metrics = evaluate_policy(evaluation_config, model, int(evaluation_seed))
                evaluation_rows.append(
                    asdict(
                        LearnedEpisode(
                            architecture=architecture,
                            alpha=alpha,
                            train_seed=train_seed,
                            evaluation_seed=int(evaluation_seed),
                            neighbor_mode=neighbor_mode,
                            **metrics,
                        )
                    )
                )
            self.progress(
                f"{architecture} alpha={alpha:g} train_seed={train_seed} neighbors={neighbor_mode}",
                combination_index / len(combinations),
            )

        _write_csv(self.output_dir / "training.csv", training_rows)
        _write_csv(self.output_dir / "evaluations.csv", evaluation_rows)
        analysis_rows = analyze(evaluation_rows)
        _write_csv(self.output_dir / "analysis.csv", analysis_rows)
        chart = export_chart(evaluation_rows, self.output_dir / "charts" / "learned_reward_topology.png")
        files = [
            self.output_dir / "training.csv",
            self.output_dir / "evaluations.csv",
            self.output_dir / "analysis.csv",
            chart,
        ]
        manifest = {
            "schema_version": "learned-stage-one.1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "base_config": base_config.to_dict(),
            "ppo_budget": budget_dict(budget),
            "alphas": list(map(float, alphas)),
            "train_seeds": list(map(int, train_seeds)),
            "evaluation_seeds": list(map(int, evaluation_seeds)),
            "architectures": list(architectures),
            "neighbor_modes": list(neighbor_modes),
            "direct_communication": False,
            "claim_boundary": (
                "Learned-policy evidence. Coordination/emergence is supported only if "
                "preregistered effect, uncertainty, and robustness criteria are met."
            ),
            "files": [str(path.relative_to(self.output_dir)) for path in files],
            "checksums": {
                str(path.relative_to(self.output_dir)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files
            },
        }
        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return {
            "training": self.output_dir / "training.csv",
            "evaluations": self.output_dir / "evaluations.csv",
            "analysis": self.output_dir / "analysis.csv",
            "chart": chart,
            "manifest": manifest_path,
        }
