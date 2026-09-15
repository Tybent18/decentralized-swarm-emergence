from collections import Counter

import numpy as np


def action_entropy(actions):
    counts = np.asarray(list(Counter(actions).values()), dtype=float)
    probabilities = counts / counts.sum()
    return float(-(probabilities * np.log2(probabilities)).sum())


def mean_pairwise_distance(positions):
    positions = np.asarray(positions, dtype=float)
    if len(positions) < 2:
        return 0.0
    distances = []
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            distances.append(np.linalg.norm(positions[i] - positions[j]))
    return float(np.mean(distances))


def spatial_order(trajectories):
    headings = []
    for trajectory in trajectories:
        if len(trajectory) > 1:
            delta = np.asarray(trajectory[-1], dtype=float) - np.asarray(trajectory[-2], dtype=float)
            norm = np.linalg.norm(delta)
            if norm:
                headings.append(delta / norm)
    if not headings:
        return 0.0
    return float(np.linalg.norm(np.mean(headings, axis=0)))


def role_differentiation(contributions, movements):
    contribution = np.asarray(contributions, dtype=float)
    movement = np.asarray(movements, dtype=float)
    features = contribution + movement / max(float(movement.max()), 1.0)
    return float(np.std(features) / max(np.mean(features), 1e-9))
