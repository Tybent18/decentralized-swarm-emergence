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
agent_x = 5
agent_y = 5

# Main loop
running = True

while running:

    # Limit FPS
    clock.tick(10)

    # Event handling
    for event in pygame.event.get():

        # Quit window
        if event.type == pygame.QUIT:
            running = False

        # Key press handling
        if event.type == pygame.KEYDOWN:

            # Move up
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                if agent_y > 0:
                    agent_y -= 1

            # Move down
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if agent_y < GRID_SIZE - 1:
                    agent_y += 1

            # Move left
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if agent_x > 0:
                    agent_x -= 1

            # Move right
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if agent_x < GRID_SIZE - 1:
                    agent_x += 1

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

    # Draw agent
    pygame.draw.rect(
        screen,
        AGENT_COLOR,
        (
            agent_x * CELL_SIZE,
            agent_y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
    )

    # Update display
    pygame.display.flip()

# Quit pygame
pygame.quit()