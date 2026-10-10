
import pygame


def run_level2(screen, clock):
    """Level 2: Survive on the Moon and repair the jet."""

    running = True

    # Astronaut position
    player_x = 100
    player_y = 390
    player_speed = 5

    # Astronaut dimensions
    player_width = 30
    player_height = 50

    # Colors
    moon_color = (120, 120, 120)
    helmet_color = (220, 220, 220)
    body_color = (50, 150, 255)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

        # Detect keyboard input
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player_x -= player_speed

        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        # Keep astronaut inside the screen
        player_x = max(0, min(player_x, screen.get_width() - player_width))

        # Draw Moon surface
        screen.fill((25, 25, 35))
        pygame.draw.rect(
            screen,
            moon_color,
            (0, 450, screen.get_width(), 150)
        )

        # Draw astronaut helmet
        pygame.draw.circle(
            screen,
            helmet_color,
            (player_x + player_width // 2, player_y + 10),
            10
        )

        # Draw astronaut body
        pygame.draw.rect(
            screen,
            body_color,
            (player_x, player_y + 20, player_width, 30)
        )

        # Draw astronaut legs
        pygame.draw.rect(
            screen,
            helmet_color,
            (player_x + 3, player_y + 45, 9, 10)
        )
        pygame.draw.rect(
            screen,
            helmet_color,
            (player_x + 18, player_y + 45, 9, 10)
        )

        # Display level title
        font = pygame.font.Font(None, 32)
        text = font.render(
            "LEVEL 2: MOON SURVIVAL",
            True,
            (255, 255, 255)
        )
        screen.blit(text, (20, 20))

        pygame.display.flip()
        clock.tick(60)

    return "LEVEL_COMPLETE"
