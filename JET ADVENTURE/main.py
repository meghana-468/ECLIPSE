"""ECLIPSE launcher: runs Levels 1 -> 2 -> 3 -> 4 in sequence."""
import pygame

from levels.level1 import Level1
from levels.level2 import Level2
from levels.level3 import MarsAdventure
from levels.level4 import FinalAdventure

WIDTH, HEIGHT = 1100, 700
FPS = 60


def run_level1(screen):
    """Level 1 uses its own callback-based completion screen."""
    outcome = {"next": False, "quit": False}
    level = Level1(
        screen,
        on_complete=lambda: outcome.__setitem__("next", True),
        on_exit=lambda: outcome.__setitem__("quit", True),
    )
    clock = pygame.time.Clock()

    while not level.finished:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            level.handle_event(event)

        if level.finished:
            break
        level.update(dt)
        level.draw(screen)
        pygame.display.flip()

    return "continue" if outcome["next"] and not outcome["quit"] else "quit"


def run_level3(screen):
    """Level 3 signals completion/exit through its callbacks."""
    outcome = {"next": False, "quit": False}
    game = MarsAdventure(
        screen,
        on_complete=lambda: outcome.__setitem__("next", True),
        on_exit=lambda: outcome.__setitem__("quit", True),
    )
    game.run()
    return "continue" if outcome["next"] and not outcome["quit"] else "quit"


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ECLIPSE - Level 1: Earth to Moon")

    try:
        # LEVEL 1
        result = run_level1(screen)
        if result != "continue":
            return

        # LEVEL 2
        pygame.display.set_caption("ECLIPSE - Level 2: Moon Survival")
        result = Level2().run(screen)
        if result != "continue":
            return

        # LEVEL 3
        pygame.display.set_caption("ECLIPSE - Level 3: Mars Mystery")
        result = run_level3(screen)
        if result != "continue":
            return

        # LEVEL 4 (final level)
        pygame.display.set_caption("ECLIPSE - Level 4: The Temple of the Overlord")
        final_level = FinalAdventure(screen)
        final_level.run()
        if final_level.state == "success":
            print("ECLIPSE completed! All four levels finished.")

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
