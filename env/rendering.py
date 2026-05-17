# envs/rendering.py

import pygame


class SwarmRenderer:
    def __init__(self, grid_size=20, window_size=600):
        self.grid_size = grid_size
        self.window_size = window_size
        self.cell_size = window_size // grid_size

        pygame.init()
        self.screen = pygame.display.set_mode((window_size, window_size))
        pygame.display.set_caption("Swarm Emergence Simulation")

        self.clock = pygame.time.Clock()

        # colors (pure presentation layer)
        self.bg = (30, 30, 30)
        self.grid = (50, 50, 50)
        self.agent_color = (0, 200, 255)
        self.target_color = (0, 255, 100)

    def draw_grid(self):
        for x in range(0, self.window_size, self.cell_size):
            pygame.draw.line(self.screen, self.grid, (x, 0), (x, self.window_size))
        for y in range(0, self.window_size, self.cell_size):
            pygame.draw.line(self.screen, self.grid, (0, y), (self.window_size, y))

    def draw_agents(self, agents):
        for a in agents:
            pygame.draw.rect(
                self.screen,
                self.agent_color,
                (
                    a["x"] * self.cell_size,
                    a["y"] * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
            )

    def draw_targets(self, targets):
        for t in targets:
            pygame.draw.rect(
                self.screen,
                self.target_color,
                (
                    t["x"] * self.cell_size,
                    t["y"] * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
            )

    def render(self, state):
        """
        state = {
            "agents": [...],
            "targets": [...],
        }
        """

        self.screen.fill(self.bg)

        self.draw_grid()
        self.draw_targets(state["targets"])
        self.draw_agents(state["agents"])

        pygame.display.flip()
        self.clock.tick(10)