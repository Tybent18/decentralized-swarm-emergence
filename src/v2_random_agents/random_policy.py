import pygame


# Initialize pygame
pygame.init()


# Window settings
WINDOW_SIZE = 600
GRID_SIZE = 20
CELL_SIZE = WINDOW_SIZE // GRID_SIZE


# Colors
BACKGROUND_COLOR = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
AGENT_COLOR = (0, 200, 255)


# Create window
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Emergent Swarm Simulation")


# Clock for controlling frame rate
clock = pygame.time.Clock()


# Agent starting position
import random


NUM_AGENTS = 5


agents = []


for i in range(NUM_AGENTS):
    agents.append({
        "x": random.randint(0, GRID_SIZE - 1),
        "y": random.randint(0, GRID_SIZE - 1)
    })


# Main loop
running = True


while running:


    # Limit FPS
    clock.tick(10)


    # Event handling
        # Random movement for all agents
    for agent in agents:


        move = random.choice([
            "up",
            "down",
            "left",
            "right",
            "stay"
        ])


        if move == "up" and agent["y"] > 0:
            agent["y"] -= 1


        elif move == "down" and agent["y"] < GRID_SIZE - 1:
            agent["y"] += 1


        elif move == "left" and agent["x"] > 0:
            agent["x"] -= 1


        elif move == "right" and agent["x"] < GRID_SIZE - 1:
            agent["x"] += 1


    # Fill background
    screen.fill(BACKGROUND_COLOR)


    # Draw grid lines
    for x in range(0, WINDOW_SIZE, CELL_SIZE):
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (x, 0),
            (x, WINDOW_SIZE)
        )


    for y in range(0, WINDOW_SIZE, CELL_SIZE):
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (0, y),
            (WINDOW_SIZE, y)
        )


    # Draw all agents
    for agent in agents:


        pygame.draw.rect(
            screen,
            AGENT_COLOR,
            (
                agent["x"] * CELL_SIZE,
                agent["y"] * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
        )    


    # Update display
    pygame.display.flip()


# Quit pygame
pygame.quit()