import numpy as np
from pettingzoo.utils import ParallelEnv


class SwarmEnv(ParallelEnv):
    """
    Decentralized swarm coordination environment.

    Key idea:
    - agents act independently
    - observations are local
    - reward structure is configurable (α-driven later)
    """

    metadata = {"render_modes": ["human"], "name": "swarm_v0"}

    def __init__(self,
                 grid_size=20,
                 n_agents=5,
                 n_targets=5,
                 obs_radius=3,
                 max_steps=200,
                 reward_mode="global",
                 alpha=1.0,
                 seed=None):

        self.grid_size = grid_size
        self.n_agents = n_agents
        self.n_targets = n_targets
        self.obs_radius = obs_radius
        self.max_steps = max_steps

        self.reward_mode = reward_mode
        self.alpha = alpha

        self.seed_value = seed
        self.rng = np.random.default_rng(seed)

        self.possible_agents = [f"agent_{i}" for i in range(n_agents)]

        self.agents = None
        self.agent_positions = {}
        self.target_positions = []

        self.steps = 0

    # -------------------------
    # RESET
    # -------------------------
    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        self.agents = self.possible_agents[:]
        self.steps = 0

        self.agent_positions = {
            a: self._random_pos() for a in self.agents
        }

        self.target_positions = [
            self._random_pos() for _ in range(self.n_targets)
        ]

        observations = {
            a: self._observe(a) for a in self.agents
        }

        infos = {a: {} for a in self.agents}

        return observations, infos

    # -------------------------
    # STEP
    # -------------------------
    def step(self, actions):
        """
        actions: dict {agent_id: action}
        """

        self.steps += 1

        rewards = {a: 0.0 for a in self.agents}

        # 1. move agents
        for a, action in actions.items():
            self._move(a, action)

        # 2. check target collection
        collected = self._resolve_targets()

        # 3. reward computation
        rewards = self._compute_rewards(collected)

        # 4. termination
        terminations = {a: False for a in self.agents}
        truncations = {a: self.steps >= self.max_steps for a in self.agents}

        observations = {a: self._observe(a) for a in self.agents}
        infos = {a: {} for a in self.agents}

        return observations, rewards, terminations, truncations, infos

    # -------------------------
    # MOVEMENT
    # -------------------------
    def _move(self, agent, action):
        x, y = self.agent_positions[agent]

        if action == 0:   # up
            y -= 1
        elif action == 1: # down
            y += 1
        elif action == 2: # left
            x -= 1
        elif action == 3: # right
            x += 1
        elif action == 4: # stay
            pass

        x = np.clip(x, 0, self.grid_size - 1)
        y = np.clip(y, 0, self.grid_size - 1)

        self.agent_positions[agent] = (x, y)

    # -------------------------
    # TARGET LOGIC
    # -------------------------
    def _resolve_targets(self):
        collected = []

        for t in self.target_positions:
            for a in self.agents:
                if self.agent_positions[a] == t:
                    collected.append(t)
                    break

        for t in collected:
            self.target_positions.remove(t)

        return len(collected)

    # -------------------------
    # REWARD SYSTEM (CORE RESEARCH KNOB)
    # -------------------------
    def _compute_rewards(self, collected):
        rewards = {}

        if self.reward_mode == "global":
            r = 1.0 if len(self.target_positions) == 0 else 0.0
            for a in self.agents:
                rewards[a] = r

        elif self.reward_mode == "local":
            for a in self.agents:
                rewards[a] = float(collected)

        elif self.reward_mode == "hybrid":
            global_r = 1.0 if len(self.target_positions) == 0 else 0.0
            local_r = float(collected)

            for a in self.agents:
                rewards[a] = self.alpha * global_r + (1 - self.alpha) * local_r

        return rewards

    # -------------------------
    # OBSERVATION (LOCAL ONLY)
    # -------------------------
    def _observe(self, agent):
        ax, ay = self.agent_positions[agent]

        obs = []

        # nearby agents
        for other in self.agents:
            ox, oy = self.agent_positions[other]
            if abs(ox - ax) <= self.obs_radius and abs(oy - ay) <= self.obs_radius:
                obs.append((ox - ax, oy - ay))

        # nearby targets
        for tx, ty in self.target_positions:
            if abs(tx - ax) <= self.obs_radius and abs(ty - ay) <= self.obs_radius:
                obs.append((tx - ax, ty - ay))

        return np.array(obs, dtype=np.float32)

    # -------------------------
    # UTIL
    # -------------------------
    def _random_pos(self):
        return (
            self.rng.integers(0, self.grid_size),
            self.rng.integers(0, self.grid_size)
        )