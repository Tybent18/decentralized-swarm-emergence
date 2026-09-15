from swarm_lab.visualization import draw_world


class SwarmRenderer:
    """Compatibility renderer that returns a Pillow frame without display side effects."""

    def __init__(self, grid_size=20, window_size=600):
        self.grid_size = grid_size
        self.window_size = window_size

    def render(self, state):
        agents = state.get("agents", [])
        targets = state.get("targets", [])
        if isinstance(agents, dict):
            agents = list(agents.values())
        agents = [(a["x"], a["y"]) if isinstance(a, dict) else tuple(a) for a in agents]
        targets = [(t["x"], t["y"]) if isinstance(t, dict) else tuple(t) for t in targets]
        snapshot = {"agents": agents, "targets": targets, "step": state.get("step", 0)}
        return draw_world(snapshot, self.grid_size, (self.window_size, self.window_size))
