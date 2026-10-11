
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
        # 1. Space background
        self.screen.fill((3, 4, 12))

    # 2. Stars
        import random

        random.seed(10)

        for _ in range(150):
           x = random.randint(0, self.width)
           y = random.randint(0, int(self.height * 0.65))
           brightness = random.randint(100, 220)

           pygame.draw.circle(
            self.screen,
            (brightness, brightness, brightness),
            (x, y),
            1
           )

    # 3. Earth in the sky
        earth_x = int(self.width * 0.78)
        earth_y = int(self.height * 0.22)
        earth_radius = 48

        pygame.draw.circle(
           self.screen,
           (35, 100, 190),
           (earth_x, earth_y),
           earth_radius
        )

        pygame.draw.circle(
        self.screen,
        (100, 170, 210),
        (earth_x - 12, earth_y - 15),
        17
        )

        pygame.draw.circle(
        self.screen,
        (70, 150, 95),
        (earth_x + 12, earth_y + 5),
        13
        )

    # 4. Moon horizon
        horizon_y = int(self.height * 0.65)

        pygame.draw.ellipse(
        self.screen,
        (80, 80, 83),
        (-self.width * 0.2, horizon_y - 70,
         self.width * 1.4, self.height)
         )

    # 5. Lunar surface
        pygame.draw.rect(
        self.screen,
        (92, 91, 87),
        (0, horizon_y + 30, self.width, self.height)
        )

    # 6. Surface craters
        craters = [
        (120, 610, 65, 20),
        (320, 650, 90, 27),
        (580, 590, 55, 18),
        (820, 660, 100, 30),
        (1000, 600, 70, 22),
        ]  

        for x, y, width, height in craters:
            pygame.draw.ellipse( self.screen, (55, 55, 54), (x - width // 2, y - height // 2, width, height) ) 
            pygame.draw.arc( self.screen, (135, 133, 127), (x - width // 2, y - height // 2, width, height), 0, 3.14, 3 )

    # 7. Rocks on the surface
        rocks = [
        (170, 650, 12),
        (410, 620, 9),
        (720, 665, 15),
        (930, 635, 11),
        ]

        for x, y, radius in rocks:
            pygame.draw.circle(
            self.screen,
            (65, 64, 61),
            (x, y),
            radius
            )

            pygame.draw.circle(
            self.screen,
            (120, 117, 110),
            (x - 3, y - 4),
            radius // 2
            )

    # 8. Display the frame
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
