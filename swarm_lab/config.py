from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    grid_size: int = 16
    n_agents: int = 6
    n_targets: int = 8
    observation_radius: int = 4
    max_steps: int = 180
    alpha: float = 0.5
    step_cost: float = 0.01
    seed: int = 7
    reward_scheme: str = "weak"
    neighbor_mode: str = "visible"

    def __post_init__(self):
        if self.grid_size < 5:
            raise ValueError("grid_size must be at least 5")
        if not 2 <= self.n_agents <= 100:
            raise ValueError("n_agents must be between 2 and 100")
        if not 1 <= self.n_targets < self.grid_size**2:
            raise ValueError("n_targets must fit within the world")
        if not 0 <= self.alpha <= 1:
            raise ValueError("alpha must be within [0, 1]")
        if self.observation_radius < 1 or self.max_steps < 1:
            raise ValueError("observation_radius and max_steps must be positive")
        if self.reward_scheme not in {"weak", "sparse"}:
            raise ValueError("reward_scheme must be 'weak' or 'sparse'")
        if self.neighbor_mode not in {"visible", "hidden", "shuffled"}:
            raise ValueError("neighbor_mode must be 'visible', 'hidden', or 'shuffled'")

    def to_dict(self):
        return asdict(self)
