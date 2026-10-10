import pygame

def run_level1(screen, clock):
    """
    Level 1: Launch from Earth and travel toward the Moon.
    """
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

        screen.fill((5, 5, 30))

        font = pygame.font.Font(None, 42)
        text = font.render("LEVEL 1: EARTH TO MOON", True, (255, 255, 255))
        screen.blit(text, (250, 270))

        pygame.display.flip()
        clock.tick(60)

    return "LEVEL_COMPLETE"
