
import pygame
import sys


class Level2:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.running = True
        # Player position
        self.player_x = self.width // 2
        self.player_y = int(self.height * 0.75)

        # Player movement speed
        self.player_speed = 220

        # Keyboard state
        self.keys = set()


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt):
        keys = pygame.key.get_pressed()

        # Horizontal movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player_x -= self.player_speed * dt

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player_x += self.player_speed * dt

        # Vertical movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player_y -= self.player_speed * dt

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player_y += self.player_speed * dt

        # Keep player within the screen
        self.player_x = max(20, min(self.width - 20, self.player_x))
        self.player_y = max(
            int(self.height * 0.65),
            min(self.height - 30, self.player_y)
        )

    
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

        for x, y, size in rocks:
            pygame.draw.ellipse(
            self.screen,
            (40, 40, 39),
            (x - size, y-size//3, size*2,size//2))
            # Irregular rock outline 
            points = [ (x - size, y), 
                      (x - size * 0.8, y - size * 0.7), 
                      (x - size * 0.3, y - size), 
                      (x + size * 0.4, y - size * 0.8), 
                      (x + size, y - size * 0.2), 
                      (x + size * 0.7, y + size * 0.3), 
                      (x - size * 0.5, y + size * 0.3), 
                      ]
            pygame.draw.polygon( self.screen, 
                                (91, 90, 86), 
                                points )
            # Lit upper-left surface 
            highlight = [ (x - size * 0.8, y - size * 0.7), 
                        (x - size * 0.3, y - size), 
                        (x + size * 0.1, y - size * 0.6), 
                        (x - size * 0.2, y - size * 0.3), 
                        ]
            pygame.draw.polygon( 
                           self.screen, 
                            (132, 130, 124), 
                            highlight )
            #Dark side to suggest depth
            dark_side = [ 
                (x + size * 0.1, y - size * 0.6), 
                (x + size, y - size * 0.2), 
                (x + size * 0.7, y + size * 0.3), 
                (x - size * 0.2, y - size * 0.3), 
                ] 
            pygame.draw.polygon( 
                self.screen, (63, 63, 61), 
                dark_side )
                
    # Draw astronaut body
        pygame.draw.ellipse(
            self.screen,
            (190, 192, 195),
            (self.player_x - 10, self.player_y - 5, 20, 25)
        )

    # Draw helmet
        pygame.draw.circle(
            self.screen,
            (210, 215, 220),
            (int(self.player_x), int(self.player_y - 12)),
            10
        )

    # Helmet visor
        pygame.draw.ellipse(
            self.screen,
            (35, 85, 115),
            (self.player_x - 7, self.player_y - 17, 14, 10)
        )

    # Backpack
        pygame.draw.rect(
            self.screen,
            (115, 118, 123),
            (self.player_x + 8, self.player_y, 7, 15)
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
