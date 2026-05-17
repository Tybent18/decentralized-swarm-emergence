from metrics.logger import EpisodeLogger
import pygame
import random

# =========================
# Initialize pygame
# =========================
pygame.init()

# =========================
# Window settings
# =========================
WINDOW_SIZE = 600
GRID_SIZE = 20
CELL_SIZE = WINDOW_SIZE // GRID_SIZE

# =========================
# Simulation settings
# =========================
NUM_AGENTS = 5
NUM_TARGETS = 5
MAX_STEPS = 200

# =========================
# Colors
# =========================
BACKGROUND_COLOR = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
AGENT_COLOR = (0, 200, 255)
TARGET_COLOR = (0, 255, 100)

# =========================
# Create window
# =========================
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Emergent Swarm Simulation")

# =========================
# Clock
# =========================
clock = pygame.time.Clock()

# =========================
# Episode tracking
# =========================
step_count = 0
episode_count = 1

logger = EpisodeLogger()

# =========================
# Create agents
# =========================
agents = []

for i in range(NUM_AGENTS):
    agents.append({
        "x": random.randint(0, GRID_SIZE - 1),
        "y": random.randint(0, GRID_SIZE - 1),
        "distance": 0
    })

# =========================
# Create targets
# =========================
targets = []

for i in range(NUM_TARGETS):
    targets.append({
        "x": random.randint(0, GRID_SIZE - 1),
        "y": random.randint(0, GRID_SIZE - 1)
    })

# =========================
# Main loop
# =========================
running = True

while running:

    # =========================
    # FPS limit
    # =========================
    clock.tick(10)

    # =========================
    # Event handling
    # =========================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # =========================
    # Random movement
    # =========================
    for agent in agents:

        move = random.choice([
            "up",
            "down",
            "left",
            "right",
            "stay"
        ])

        # Move up
        if move == "up" and agent["y"] > 0:
            agent["y"] -= 1
            agent["distance"] += 1

        # Move down
        elif move == "down" and agent["y"] < GRID_SIZE - 1:
            agent["y"] += 1
            agent["distance"] += 1

        # Move left
        elif move == "left" and agent["x"] > 0:
            agent["x"] -= 1
            agent["distance"] += 1

        # Move right
        elif move == "right" and agent["x"] < GRID_SIZE - 1:
            agent["x"] += 1
            agent["distance"] += 1

    # =========================
    # Check target collection
    # =========================
    collected_targets = []

    for target in targets:

        for agent in agents:

            if (
                agent["x"] == target["x"]
                and
                agent["y"] == target["y"]
            ):
                collected_targets.append(target)
                break

    # Remove collected targets
    for target in collected_targets:
        if target in targets:
            targets.remove(target)

    # =========================
    # Increase timestep
    # =========================
    step_count += 1

    # =========================
    # Episode success condition
    # =========================
    if len(targets) == 0:

        total_distance = 0

        for agent in agents:
            total_distance += agent["distance"]

        print("\n====================")
        print(f"Episode {episode_count} COMPLETE")
        print(f"Steps: {step_count}")
        print(f"Total Distance: {total_distance}")
        print("====================")

        logger.log_episode(
            episode=episode_count,
            success=True,
            steps=step_count,
            total_distance=total_distance,
            targets_collected=NUM_TARGETS
        )
        # Reset counters
        step_count = 0
        episode_count += 1

        # Reset agents
        agents = []

        for i in range(NUM_AGENTS):
            agents.append({
                "x": random.randint(0, GRID_SIZE - 1),
                "y": random.randint(0, GRID_SIZE - 1),
                "distance": 0
            })

        # Reset targets
        targets = []

        for i in range(NUM_TARGETS):
            targets.append({
                "x": random.randint(0, GRID_SIZE - 1),
                "y": random.randint(0, GRID_SIZE - 1)
            })

    # =========================
    # Episode failure condition
    # =========================
    if step_count >= MAX_STEPS:

        print("\n====================")
        print(f"Episode {episode_count} FAILED")
        print("Maximum steps reached")
        print("====================")

        total_distance = 0

        for agent in agents:
            total_distance += agent["distance"]

        logger.log_episode(
            episode=episode_count,
            success=False,
            steps=step_count,
            total_distance=total_distance,
            targets_collected=NUM_TARGETS - len(targets)
        )

        # Reset counters
        step_count = 0
        episode_count += 1

        # Reset agents
        agents = []

        for i in range(NUM_AGENTS):
            agents.append({
                "x": random.randint(0, GRID_SIZE - 1),
                "y": random.randint(0, GRID_SIZE - 1),
                "distance": 0
            })

        # Reset targets
        targets = []

        for i in range(NUM_TARGETS):
            targets.append({
                "x": random.randint(0, GRID_SIZE - 1),
                "y": random.randint(0, GRID_SIZE - 1)
            })

    # =========================
    # Render background
    # =========================
    screen.fill(BACKGROUND_COLOR)

    # =========================
    # Draw grid
    # =========================
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

    # =========================
    # Draw targets
    # =========================
    for target in targets:

        pygame.draw.rect(
            screen,
            TARGET_COLOR,
            (
                target["x"] * CELL_SIZE,
                target["y"] * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
        )

    # =========================
    # Draw agents
    # =========================
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

    # =========================
    # Update display
    # =========================
    pygame.display.flip()

# =========================
# Quit pygame
# =========================
pygame.quit()