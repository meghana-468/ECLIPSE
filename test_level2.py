import pygame
import settings as S
from settings import (
    BLACK,
    WHITE,
    CYAN,
    GOLD,
    RED,
    GREEN,
    DARK,
    PANEL,
    MOON,
    MOON_LIGHT,
    MOON_DARK,
)
from level2 import Level2


def main():
    pygame.init()

    screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
    pygame.display.set_caption("ECLIPSE - Level 2: Moon Survival")

    level = Level2()
    result = level.run(screen)

    print("Level 2 result:", result)

    pygame.quit()


if __name__ == "__main__":
    main()