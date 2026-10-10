import pygame

def run_level4(screen, clock):
    """Level 4: Find the alien treasure on Mars and return to Earth."""
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

        screen.fill((90, 25, 15))

        font = pygame.font.Font(None, 38)
        text = font.render("LEVEL 4: MARS TREASURE", True, (255, 255, 255))
        screen.blit(text, (280, 270))

        pygame.display.flip()
        clock.tick(60)

    return "LEVEL_COMPLETE"
