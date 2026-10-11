
import pygame
import sys


class Level2:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill((5, 5, 25))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()


def main():
    pygame.init()

    screen = pygame.display.set_mode((1100, 700))
    pygame.display.set_caption("ECLIPSE - Level 2")

    level = Level2(screen)
    level.run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
