import pygame

def run_level2(screen, clock):
    """Level 2: Survive on the Moon and repair the jet."""
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

        screen.fill((35, 35, 50))

        font = pygame.font.Font(None, 38)
        text = font.render("LEVEL 2: MOON SURVIVAL", True, (255, 255, 255))
        screen.blit(text, (260, 270))

        pygame.display.flip()
        clock.tick(60)

    return "LEVEL_COMPLETE"
