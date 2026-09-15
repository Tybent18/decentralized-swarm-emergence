import csv
import json
import threading
from dataclasses import asdict

import pytest

from swarm_lab.config import ExperimentConfig
from swarm_lab.experiment import ExperimentCollector, run_episode


def stable_fields(result):
    values = asdict(result)
    values.pop("run_id")
    values.pop("timestamp_utc")
    return values


def test_seeded_episode_is_reproducible():
    config = ExperimentConfig(seed=31, max_steps=60)
    assert stable_fields(run_episode(config, "greedy")) == stable_fields(run_episode(config, "greedy"))


def test_collector_exports_raw_summary_charts_and_manifest(tmp_path):
    outputs = ExperimentCollector(tmp_path).collect(
        range(2), (0, 1), ("random", "greedy"), ExperimentConfig(max_steps=30)
    )
    assert all(path.exists() for path in (outputs["raw"], outputs["summary"], outputs["manifest"]))
    assert all(path.exists() and path.stat().st_size > 1000 for path in outputs["charts"])
    with outputs["raw"].open(newline="", encoding="utf-8") as stream:
        assert len(list(csv.DictReader(stream))) == 8
    manifest = json.loads(outputs["manifest"].read_text(encoding="utf-8"))
    assert manifest["episode_count"] == 8
    assert "no learned-policy emergence claim" in manifest["claim_boundary"].lower()


def test_cancelled_episode_stops_at_safe_step():
    flag = threading.Event()
    flag.set()
    with pytest.raises(InterruptedError):
        run_episode(ExperimentConfig(), "random", cancel_event=flag)
