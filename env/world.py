import numpy as np


class SwarmWorld:
    """
    Pure simulation state engine.

    No RL. No PettingZoo. No rendering.

    Just physics of a discrete swarm world.
    """

    def __init__(self, grid_size=20, n_agents=5, n_targets=5, seed=None):
        self.grid_size = grid_size
        self.n_agents = n_agents
        self.n_targets = n_targets

        self.rng = np.random.default_rng(seed)

        self.agent_positions = {}
        self.target_positions = []

        self.step_count = 0

    # -------------------------
    # INITIALIZATION
    # -------------------------
    def reset(self):
        self.step_count = 0

        self.agent_positions = {
            i: self._random_pos() for i in range(self.n_agents)
        }

        self.target_positions = [
            self._random_pos() for _ in range(self.n_targets)
        ]

        return self.get_state()

    # -------------------------
    # STATE ACCESS
    # -------------------------
    def get_state(self):
        return {
            "agents": self.agent_positions.copy(),
            "targets": self.target_positions.copy(),
            "step": self.step_count
        }

    # -------------------------
    # STEP FUNCTION
    # -------------------------
    def step(self, actions):
        """
        actions: dict {agent_id: int}
        """

        self.step_count += 1

        # 1. move all agents
        for agent_id, action in actions.items():
            self._move(agent_id, action)

        # 2. resolve interactions
        collected = self._resolve_targets()

        # 3. return updated state + interaction results
        return self.get_state(), collected

    # -------------------------
    # MOVEMENT LOGIC
    # -------------------------
    def _move(self, agent_id, action):
        x, y = self.agent_positions[agent_id]

        # 0 up
        # 1 down
        # 2 left
        # 3 right
        # 4 stay

        if action == 0:
            y -= 1
        elif action == 1:
            y += 1
        elif action == 2:
            x -= 1
        elif action == 3:
            x += 1
        elif action == 4:
            pass

        x = np.clip(x, 0, self.grid_size - 1)
        y = np.clip(y, 0, self.grid_size - 1)

        self.agent_positions[agent_id] = (int(x), int(y))

    # -------------------------
    # INTERACTIONS
    # -------------------------
    def _resolve_targets(self):
        """
        Returns number of collected targets this step.
        """

        collected = []

        for t in self.target_positions:
            for a in self.agent_positions.values():
                if a == t:
                    collected.append(t)
                    break

        for t in collected:
            self.target_positions.remove(t)

        return len(collected)

    # -------------------------
    # UTIL
    # -------------------------
    def _random_pos(self):
        return (
            int(self.rng.integers(0, self.grid_size)),
            int(self.rng.integers(0, self.grid_size))
        )