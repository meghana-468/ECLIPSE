import pygame

def run_level3(screen, clock):
    """Level 3: Fight aliens while travelling to Mars."""
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

        screen.fill((20, 5, 35))

        font = pygame.font.Font(None, 38)
        text = font.render("LEVEL 3: MOON TO MARS", True, (255, 255, 255))
        screen.blit(text, (280, 270))

        pygame.display.flip()
        clock.tick(60)

    return "LEVEL_COMPLETE"
