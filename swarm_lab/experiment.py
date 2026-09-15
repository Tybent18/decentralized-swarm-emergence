import csv
import hashlib
import json
import platform
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .config import ExperimentConfig
from .metrics import action_entropy, mean_pairwise_distance, role_differentiation, spatial_order
from .policies import POLICIES
from .world import SwarmWorld


@dataclass(frozen=True)
class EpisodeResult:
    run_id: str
    timestamp_utc: str
    policy: str
    reward_scheme: str
    alpha: float
    seed: int
    n_agents: int
    n_targets: int
    success: int
    steps: int
    targets_collected: int
    completion_rate: float
    total_distance: int
    distance_per_target: float
    coordination_efficiency: float
    attempted_collisions: int
    collision_rate: float
    action_entropy: float
    spatial_order: float
    mean_interagent_distance: float
    role_differentiation: float
    team_return: float


def run_episode(config, policy_name="random", frame_callback=None, cancel_event=None):
    if policy_name not in POLICIES:
        raise ValueError(f"unknown policy: {policy_name}")
    world = SwarmWorld(config.grid_size, config.n_agents, config.n_targets, config.seed)
    rng = np.random.default_rng(config.seed + 10_000)
    initial_targets = config.n_targets
    distance = collisions = 0
    contributions = np.zeros(config.n_agents, dtype=int)
    movements = np.zeros(config.n_agents, dtype=int)
    actions_taken = []
    order_values, distance_values = [], []
    team_return = 0.0
    if frame_callback:
        frame_callback(world.snapshot(), None)
    while world.targets and world.step_count < config.max_steps:
        if cancel_event and cancel_event.is_set():
            raise InterruptedError("experiment cancelled")
        actions = POLICIES[policy_name](world, rng)
        event = world.step(actions)
        collected = sum(event.collectors.values())
        complete = not world.targets
        global_signal = float(complete) if config.reward_scheme == "sparse" else float(collected)
        team_return += config.alpha * (global_signal - config.step_cost) + (1 - config.alpha) * (
            np.mean(list(event.collectors.values())) - config.step_cost
        )
        collisions += event.attempted_collisions
        for i in range(config.n_agents):
            contributions[i] += event.collectors[i]
            movements[i] += event.moved[i]
        distance += sum(event.moved.values())
        actions_taken.extend(actions.values())
        order_values.append(spatial_order(world.trajectories))
        distance_values.append(mean_pairwise_distance(world.positions))
        if frame_callback:
            frame_callback(world.snapshot(), event)
    collected_total = initial_targets - len(world.targets)
    success = int(not world.targets)
    timestamp = datetime.now(timezone.utc).isoformat()
    identity = f"{policy_name}:{config.alpha}:{config.seed}:{timestamp}"
    return EpisodeResult(
        run_id=hashlib.sha256(identity.encode()).hexdigest()[:12],
        timestamp_utc=timestamp,
        policy=policy_name,
        reward_scheme=config.reward_scheme,
        alpha=config.alpha,
        seed=config.seed,
        n_agents=config.n_agents,
        n_targets=config.n_targets,
        success=success,
        steps=world.step_count,
        targets_collected=collected_total,
        completion_rate=collected_total / initial_targets,
        total_distance=distance,
        distance_per_target=distance / max(collected_total, 1),
        coordination_efficiency=success / max(distance, 1),
        attempted_collisions=collisions,
        collision_rate=collisions / max(config.n_agents * world.step_count, 1),
        action_entropy=action_entropy(actions_taken),
        spatial_order=float(np.mean(order_values)) if order_values else 0.0,
        mean_interagent_distance=float(np.mean(distance_values)) if distance_values else 0.0,
        role_differentiation=role_differentiation(contributions, movements),
        team_return=float(team_return),
    )


class ExperimentCollector:
    """One-command collector that appends raw evidence and rebuilds every export."""

    def __init__(self, output_dir="results", progress=None, cancel_event=None):
        self.output_dir = Path(output_dir)
        self.progress = progress or (lambda *_: None)
        self.cancel_event = cancel_event or threading.Event()

    def collect(self, seeds, alphas, policies, base_config=None):
        base = base_config or ExperimentConfig()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        combinations = [(p, float(a), int(s)) for p in policies for a in alphas for s in seeds]
        rows = []
        for index, (policy, alpha, seed) in enumerate(combinations, 1):
            config = ExperimentConfig(**{**base.to_dict(), "alpha": alpha, "seed": seed})
            rows.append(run_episode(config, policy, cancel_event=self.cancel_event))
            self.progress(f"{policy} | alpha={alpha:g} | seed={seed}", index / len(combinations))
        raw_path = self.output_dir / "episodes.csv"
        self._append_csv(raw_path, rows)
        all_rows = self._read_csv(raw_path)
        from .visualization import export_charts, export_reference_visuals

        summary_path = self._write_summary(all_rows)
        chart_paths = export_charts(all_rows, self.output_dir / "charts")
        snapshots = []
        reference = ExperimentConfig(**{**base.to_dict(), "alpha": 0.5, "seed": 7})
        run_episode(reference, "distributed-greedy", lambda snapshot, _event: snapshots.append(snapshot))
        chart_paths.append(export_reference_visuals(snapshots, self.output_dir / "charts"))
        manifest = {
            "schema_version": "stage-one.1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "base_config": base.to_dict(),
            "episode_count": len(all_rows),
            "new_episode_count": len(rows),
            "policies": sorted({r["policy"] for r in all_rows}),
            "alphas": sorted({float(r["alpha"]) for r in all_rows}),
            "seeds": sorted({int(r["seed"]) for r in all_rows}),
            "claim_boundary": "Heuristic baseline evidence only; no learned-policy emergence claim.",
            "files": [raw_path.name, summary_path.name, *[str(p.relative_to(self.output_dir)) for p in chart_paths]],
        }
        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return {"raw": raw_path, "summary": summary_path, "charts": chart_paths, "manifest": manifest_path}

    @staticmethod
    def _append_csv(path, rows):
        fields = list(asdict(rows[0])) if rows else []
        exists = path.exists()
        with path.open("a", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            if not exists:
                writer.writeheader()
            writer.writerows(asdict(row) for row in rows)

    @staticmethod
    def _read_csv(path):
        with path.open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))

    def _write_summary(self, rows):
        numeric = [
            "success",
            "steps",
            "completion_rate",
            "total_distance",
            "distance_per_target",
            "coordination_efficiency",
            "collision_rate",
            "action_entropy",
            "spatial_order",
            "mean_interagent_distance",
            "role_differentiation",
            "team_return",
        ]
        groups = {}
        for row in rows:
            groups.setdefault((row["policy"], row["reward_scheme"], row["alpha"]), []).append(row)
        path = self.output_dir / "summary.csv"
        fields = [
            "policy",
            "reward_scheme",
            "alpha",
            "episodes",
            *[f"{m}_mean" for m in numeric],
            *[f"{m}_std" for m in numeric],
        ]
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            for (policy, reward_scheme, alpha), group in sorted(groups.items()):
                record = {
                    "policy": policy,
                    "reward_scheme": reward_scheme,
                    "alpha": alpha,
                    "episodes": len(group),
                }
                for metric in numeric:
                    values = np.asarray([float(r[metric]) for r in group])
                    record[f"{metric}_mean"] = float(values.mean())
                    record[f"{metric}_std"] = float(values.std(ddof=1)) if len(values) > 1 else 0.0
                writer.writerow(record)
        return path
