

import math

import random

import sys

import pygame


# Reused Level 1 artwork: the rocket and the astronaut.
def ip(x, y):
    return (int(x), int(y))


def draw_ship(surf, ox, oy, s, flame=0.0, hatch=1.0, pilot=False):
    """Classic straight rocket ship, upright with nose at the top.

    (ox, oy) is the centre x and the bottom of the engine nozzle.
    s is the pixels-per-model-unit scale. `hatch` is retained so existing
    Level 1 boarding/launch logic continues to work.
    """
    def X(u):
        return ox + u * s

    def Y(z):
        return oy - (z + 0.4) * s

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [ip(X(u), Y(z)) for u, z in pts])

    line_w = max(2, int(0.16 * s))

    # Bright engine flame below the rocket.
    if flame > 0.0:
        length = 3.4 * flame
        poly((255, 105, 25), [(-0.62, -0.4), (0.62, -0.4),
                              (0.0, -0.4 - length)])
        poly((255, 225, 80), [(-0.32, -0.4), (0.32, -0.4),
                              (0.0, -0.4 - length * 0.68)])

    # Side fins and engine bell.
    poly((190, 48, 55), [(-0.72, 1.35), (-1.75, -0.25),
                         (-0.48, 0.05), (-0.35, 1.5)])
    poly((190, 48, 55), [(0.72, 1.35), (1.75, -0.25),
                         (0.48, 0.05), (0.35, 1.5)])
    poly((55, 60, 78), [(-0.48, 0.45), (0.48, 0.45),
                        (0.38, -0.4), (-0.38, -0.4)])

    # Long, straight rocket body with a pointed nose.
    poly((205, 211, 222), [(-0.52, 1.0), (-0.52, 6.9),
                           (0.0, 8.9), (0.52, 6.9), (0.52, 1.0)])
    poly((135, 145, 164), [(-0.52, 1.0), (-0.52, 6.9),
                           (0.0, 8.9), (0.0, 1.0)])
    poly((240, 242, 248), [(-0.14, 1.2), (-0.14, 6.8),
                           (0.0, 7.7), (0.0, 1.2)])

    # Cockpit window. Once the astronaut has boarded, show their helmet and
    # shoulders INSIDE the glass (rather than standing beside the rocket).
    window = pygame.Rect(int(X(-0.31)), int(Y(6.35)),
                         max(3, int(0.62 * s)), max(3, int(1.05 * s)))
    pygame.draw.ellipse(surf, (16, 42, 82), window)
    if pilot:
        # Draw the suit/shoulders first, then the helmet and visor.
        shoulders = pygame.Rect(0, 0, max(3, int(0.43 * s)), max(3, int(0.30 * s)))
        shoulders.center = (int(X(0.0)), int(window.top + 0.88 * s))
        pygame.draw.ellipse(surf, (225, 230, 241), shoulders)
        pygame.draw.ellipse(surf, (150, 160, 180), shoulders, max(1, int(0.04 * s)))
        helmet = pygame.Rect(0, 0, max(3, int(0.38 * s)), max(3, int(0.43 * s)))
        helmet.center = (int(X(0.0)), int(window.top + 0.36 * s))
        pygame.draw.ellipse(surf, (240, 242, 248), helmet)
        visor = pygame.Rect(0, 0, max(2, int(0.25 * s)), max(2, int(0.20 * s)))
        visor.center = (int(X(0.0)), int(window.top + 0.38 * s))
        pygame.draw.ellipse(surf, (240, 188, 65), visor)
        pygame.draw.ellipse(surf, (255, 232, 145), visor, max(1, int(0.035 * s)))
    pygame.draw.ellipse(surf, (115, 220, 255), window, max(1, int(0.08 * s)))
    pygame.draw.line(surf, (220, 248, 255),
                     ip(X(-0.16), Y(6.95)), ip(X(0.02), Y(6.55)),
                     max(1, int(0.07 * s)))

    # Thin body bands and small side details.
    pygame.draw.line(surf, (245, 155, 55), ip(X(-0.5), Y(2.2)),
                     ip(X(0.5), Y(2.2)), max(2, int(0.12 * s)))
    pygame.draw.line(surf, (245, 155, 55), ip(X(-0.5), Y(2.45)),
                     ip(X(0.5), Y(2.45)), max(1, int(0.06 * s)))
    for z in (3.0, 4.2):
        pygame.draw.circle(surf, (80, 190, 220),
                           ip(X(-0.36), Y(z)), max(1, int(0.09 * s)))
        pygame.draw.circle(surf, (80, 190, 220),
                           ip(X(0.36), Y(z)), max(1, int(0.09 * s)))

    # Small top panel detail.
    pygame.draw.line(surf, (255, 255, 255), ip(X(-0.2), Y(7.7)),
                     ip(X(0.2), Y(7.7)), max(1, int(0.07 * s)))

def draw_astronaut(surf, x, y, sc=0.68, phase=0.0, face=1):
    """Astronaut in a white suit with a gold visor. (x, y) = feet. face = +1/-1."""
    suit = (238, 238, 245)
    shade = (178, 182, 198)
    dark = (70, 66, 64)
    gold = (236, 184, 60)
    swing = math.sin(phase)

    def P(dx, dy):
        return (int(x + face * dx * sc), int(y + dy * sc))

    def limb(origin, angle_deg, length, width, color, tip):
        a = math.radians(angle_deg)
        ox, oy = origin
        ex, ey = ox + math.sin(a) * length, oy + math.cos(a) * length
        w = max(2, int(width * sc))
        pygame.draw.line(surf, color, P(ox, oy), P(ex, ey), w)
        pygame.draw.circle(surf, color, P(ox, oy), max(1, w // 2))
        pygame.draw.circle(surf, tip, P(ex, ey), max(2, int(width * 0.55 * sc)))

    pack = pygame.Rect(0, 0, max(3, int(11 * sc)), max(3, int(22 * sc)))
    pack.center = P(-13, -40)
    pygame.draw.rect(surf, (212, 214, 224), pack, border_radius=3)
    limb((0, -27), -swing * 35, 24, 9, shade, dark)           # far leg
    limb((0, -46), swing * 30, 19, 7, shade, dark)            # far arm
    torso = pygame.Rect(0, 0, max(4, int(20 * sc)), max(4, int(24 * sc)))
    torso.center = P(0, -39)
    pygame.draw.rect(surf, suit, torso, border_radius=max(2, int(6 * sc)))
    chest = pygame.Rect(0, 0, max(2, int(8 * sc)), max(2, int(7 * sc)))
    chest.center = P(5, -40)
    pygame.draw.rect(surf, (150, 154, 168), chest)
    limb((0, -27), swing * 35, 24, 9, suit, dark)             # near leg
    pygame.draw.circle(surf, suit, P(1, -57), max(3, int(10 * sc)))   # helmet
    visor = pygame.Rect(0, 0, max(3, int(9 * sc)), max(3, int(11 * sc)))
    visor.center = P(6, -57)
    pygame.draw.ellipse(surf, gold, visor)
    pygame.draw.circle(surf, (255, 240, 200), P(7, -60), max(1, int(2 * sc)))
    limb((0, -46), -swing * 30, 19, 7, suit, dark)





# ECLIPSE - LEVEL 3: MARS MYSTERY
# Standalone Level 3. Uses the original astronaut and spaceship artwork above.

class MarsAdventure:
    WIDTH = 1100
    HEIGHT = 700

    def __init__(self, screen, on_complete=None, on_exit=None):
        self.screen = screen
        self.on_complete = on_complete
        self.on_exit = on_exit
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 58)
        self.font_title = pygame.font.Font(None, 40)
        self.running = True
        self.state = "briefing"
        self.paused = False
        self.reset_mission()
        self.stars = [
            (random.randrange(self.WIDTH), random.randrange(25, 430), random.choice((1, 1, 2)))
            for _ in range(120)
        ]
        self.mountains_far = [
            (0, 455), (100, 390), (230, 450), (360, 375), (490, 448),
            (650, 385), (780, 445), (930, 380), (1100, 450)
        ]
        self.mountains_near = [
            (0, 490), (150, 445), (260, 485), (420, 435), (570, 488),
            (740, 442), (890, 485), (1010, 440), (1100, 475)
        ]

    def reset_mission(self):
        self.player_x = 70.0
        self.player_y = 590.0
        self.facing = 1
        self.walk_phase = 0.0
        self.diamonds_found = 0
        self.lives = 3
        self.laser_phase = 0.0
        self.invulnerable = 0.0
        self.message = "Collect the three diamonds. Watch the laser timing!"
        self.message_timer = 4.0
        self.stage = "diamonds"  # diamonds -> door -> key -> escape
        self.door_open = False
        self.has_key = False
        self.console_flash = 0.0
        self.diamonds = [
            pygame.Rect(225, 548, 28, 28),
            pygame.Rect(465, 575, 28, 28),
            pygame.Rect(705, 535, 28, 28),
        ]
        self.lasers = [
            pygame.Rect(335, 500, 18, 118),
            pygame.Rect(575, 500, 18, 118),
            pygame.Rect(790, 500, 18, 118),
        ]
        # Start with a Moon-to-Mars space journey, then enter the Mars mission.
        self.state = "launch"
        self.paused = False
        self.phase_time = 0.0
        self.flight_time = 0.0
        self.flight_duration = 22.0
        self.ship_x = 155.0
        self.ship_y = 515.0
        self.flight_lives = 3
        self.flight_invulnerable = 0.0
        self.flight_message = "ENGINES IGNITING — MOON TO MARS"
        self.flight_asteroids = []
        self.next_asteroid = 1.3
        self.shield_active = False
        self.flight_stars = [
            (random.randrange(self.WIDTH), random.randrange(self.HEIGHT), random.choice((1, 1, 2)))
            for _ in range(110)
        ]

    def _text(self, text, y, font=None, color=(240, 245, 255), x=None):
        font = font or self.font_medium
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(self.WIDTH // 2 if x is None else x, y))
        self.screen.blit(surf, rect)

    def _button(self, rect, label, primary=True):
        fill = (0, 92, 190) if primary else (15, 28, 48)
        edge = (100, 225, 255) if primary else (100, 160, 190)
        pygame.draw.rect(self.screen, fill, rect, border_radius=9)
        pygame.draw.rect(self.screen, edge, rect, 2, border_radius=9)
        label_surface = self.font_small.render(label, True, (245, 250, 255))
        self.screen.blit(label_surface, label_surface.get_rect(center=rect.center))

    def _near(self, x, distance=65):
        return abs(self.player_x - x) <= distance

    def _say(self, message, duration=2.5):
        self.message = message
        self.message_timer = duration

    def _hit_laser(self):
        if self.invulnerable > 0:
            return
        self.lives -= 1
        self.invulnerable = 1.4
        self.player_x = max(40, self.player_x - 55)
        self._say("LASER HIT! You lost a life. Wait for the beam to switch off.", 2.3)
        if self.lives <= 0:
            self.state = "game_over"

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            if self.on_exit:
                self.on_exit()
            return

        if event.type == pygame.KEYDOWN:
            if self.state == "flight_over" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_mission()
                return
            if self.state in ("launch", "flight", "landing") and event.key == pygame.K_ESCAPE:
                self.running = False
                if self.on_exit:
                    self.on_exit()
                return
            if self.state == "flight_over" and event.key == pygame.K_ESCAPE:
                self.running = False
                if self.on_exit:
                    self.on_exit()
                return
            if self.state == "briefing" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.state = "playing"
                self._say("Mission started! Find all three diamonds.", 2.5)
            elif self.state == "playing":
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    if self.on_exit:
                        self.on_exit()
                elif event.key == pygame.K_e:
                    self._interact()
            elif self.state == "success" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.running = False
                if self.on_complete:
                    self.on_complete()
            elif self.state == "game_over" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_mission()
                self.state = "playing"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "briefing" and pygame.Rect(385, 555, 330, 55).collidepoint(event.pos):
                self.state = "playing"
                self._say("Mission started! Find all three diamonds.", 2.5)
            elif self.state == "success":
                if pygame.Rect(300, 490, 245, 54).collidepoint(event.pos):
                    self.running = False
                    if self.on_complete:
                        self.on_complete()
                elif pygame.Rect(565, 490, 235, 54).collidepoint(event.pos):
                    self.running = False
                    if self.on_exit:
                        self.on_exit()
            elif self.state == "game_over":
                if pygame.Rect(385, 490, 330, 54).collidepoint(event.pos):
                    self.reset_mission()
                    self.state = "playing"
                elif pygame.Rect(565, 555, 235, 54).collidepoint(event.pos):
                    self.running = False
                    if self.on_exit:
                        self.on_exit()

    def _interact(self):
        if self.stage == "door" and self._near(875, 95):
            self.door_open = True
            self.stage = "key"
            self._say("The three diamonds unlock the giant door! A golden key is inside.", 4.0)
        elif self.stage == "key" and self._near(920, 100):
            self.has_key = True
            self.stage = "escape"
            self._say("BIG KEY COLLECTED! Return to your spaceship to finish Level 3.", 4.0)
        elif self.stage == "diamonds":
            self._say(f"Find the diamonds first: {self.diamonds_found}/3 collected.", 2.0)
        elif self.stage == "door":
            self._say("Move close to the giant door and press E to place the diamonds.", 2.5)
        elif self.stage == "key":
            self._say("Move close to the golden key and press E to pick it up.", 2.5)
        elif self.stage == "escape":
            self._say("Carry the key to your spaceship on the right.", 2.5)

    def update(self, dt):
        if self.state in ("launch", "flight", "landing"):
            self.update_flight(dt)
            return
        if self.state != "playing" or self.paused:
            return
        self.laser_phase += dt
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.message_timer = max(0.0, self.message_timer - dt)
        self.console_flash += dt

        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.player_x += dx * 235 * dt
        self.player_y += dy * 165 * dt
        self.player_x = max(25, min(1060, self.player_x))
        self.player_y = max(475, min(620, self.player_y))
        if dx:
            self.facing = 1 if dx > 0 else -1
        if dx or dy:
            self.walk_phase += dt * 8

        player_rect = pygame.Rect(int(self.player_x - 14), int(self.player_y - 58), 28, 58)

        if self.stage == "diamonds":
            for i, diamond in enumerate(self.diamonds):
                if diamond is not None and player_rect.colliderect(diamond):
                    self.diamonds[i] = None
                    self.diamonds_found += 1
                    self._say(f"DIAMOND COLLECTED: {self.diamonds_found}/3", 1.8)
            if self.diamonds_found == 3:
                self.stage = "door"
                self._say("All diamonds collected! Find the giant door and press E.", 4.0)

        # Lasers cycle on and off. The player can wait for a safe opening.
        laser_on = (self.laser_phase % 2.8) < 1.65
        if laser_on and self.stage in ("diamonds", "door"):
            for laser in self.lasers:
                if player_rect.colliderect(laser):
                    self._hit_laser()
                    break

        if self.stage == "escape" and self.has_key and self.player_x >= 1010:
            self.state = "success"

    def update_flight(self, dt):
        """Launch from the Moon, travel diagonally toward Mars, then land."""
        self.phase_time += dt
        self.flight_invulnerable = max(0.0, self.flight_invulnerable - dt)
        keys = pygame.key.get_pressed()

        if self.state == "launch":
            progress = min(1.0, self.phase_time / 3.2)
            self.ship_x = 150 + progress * 70
            self.ship_y = 520 - progress * 48
            if self.phase_time >= 3.2:
                self.state = "flight"
                self.phase_time = 0.0
                self.flight_time = 0.0
                self.ship_x, self.ship_y = 220.0, 470.0
                self.flight_message = "FLIGHT: steer around asteroids; hold SPACE for shield."
            return

        if self.state == "landing":
            progress = min(1.0, self.phase_time / 4.0)
            self.ship_x = 900 + progress * 45
            self.ship_y = 145 + progress * 280
            if self.phase_time >= 4.0:
                self.state = "briefing"
                self.phase_time = 0.0
                self._say("Landed on Mars! Exit the ship and collect all 3 diamonds.", 4.0)
            return

        self.flight_time += dt
        # The automatic diagonal route leads from bottom-left to top-right.
        # WASD / arrows still let the player dodge and adjust the path.
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.ship_x += (35 + dx * 170) * dt
        self.ship_y += (-17 + dy * 170) * dt
        self.ship_x = max(90, min(self.WIDTH - 65, self.ship_x))
        self.ship_y = max(65, min(self.HEIGHT - 80, self.ship_y))
        self.shield_active = bool(keys[pygame.K_SPACE])

        # Asteroids spawn beside Mars (upper-right) and fly toward the ship.
        self.next_asteroid -= dt
        if self.next_asteroid <= 0:
            ax = random.uniform(900, 1060)
            ay = random.uniform(65, 190)
            vx0 = self.ship_x - ax
            vy0 = self.ship_y - ay
            distance = max(1.0, math.hypot(vx0, vy0))
            speed = random.uniform(135, 225)
            self.flight_asteroids.append([
                ax, ay, vx0 / distance * speed, vy0 / distance * speed,
                random.randrange(15, 24)
            ])
            self.next_asteroid = random.uniform(0.8, 1.5)

        for rock in self.flight_asteroids[:]:
            rock[0] += rock[2] * dt
            rock[1] += rock[3] * dt
            if (rock[0] < -45 or rock[0] > self.WIDTH + 45 or
                    rock[1] < -45 or rock[1] > self.HEIGHT + 45):
                self.flight_asteroids.remove(rock)
                continue
            radius = rock[4]
            if (self.flight_invulnerable <= 0 and
                    math.hypot(rock[0] - self.ship_x, rock[1] - self.ship_y) < radius + 25):
                self.flight_asteroids.remove(rock)
                if self.shield_active:
                    self.flight_message = "SHIELD BLOCKED THE ASTEROID!"
                else:
                    self.flight_lives -= 1
                    self.flight_invulnerable = 1.2
                    self.flight_message = "ASTEROID IMPACT — HOLD SPACE TO SHIELD!"
                    if self.flight_lives <= 0:
                        self.state = "flight_over"
                        return

        if self.flight_time >= self.flight_duration:
            self.state = "landing"
            self.phase_time = 0.0
            self.flight_message = "MARS APPROACH — LANDING THRUSTERS ENGAGED"

    def draw_flight(self):
        self.screen.fill((4, 7, 25))
        for x, y, radius in self.flight_stars:
            yy = int((y + (self.flight_time + self.phase_time) * 30) % self.HEIGHT)
            pygame.draw.circle(self.screen, (150, 180, 225), (x, yy), radius)

        if self.state == "launch":
            # Show the Moon only during launch, with the rocket starting on its surface.
            moon_center = (125, 650)
            pygame.draw.circle(self.screen, (150, 158, 176), moon_center, 155)
            pygame.draw.circle(self.screen, (190, 195, 207), (88, 600), 18)
            pygame.draw.circle(self.screen, (112, 120, 140), (175, 625), 24)
            pygame.draw.circle(self.screen, (112, 120, 140), (115, 690), 15)
            pygame.draw.circle(self.screen, (125, 132, 151), (205, 710), 12)
            self._text("ECLIPSE: LUNAR LAUNCH", 42, self.font_title, (140, 225, 255))
            draw_ship(self.screen, int(self.ship_x), int(self.ship_y + 48), 10, flame=1.0, pilot=True)
            self._text("Launching from the Moon to Mars...", 650, self.font_medium, (255, 220, 150))
            return

        if self.state == "landing":
            progress = min(1.0, self.phase_time / 4.0)
            radius = int(75 + progress * 280)
            pygame.draw.circle(self.screen, (180, 68, 48), (1000, 125), radius)
            pygame.draw.circle(self.screen, (125, 48, 43), (960, 100), max(12, int(radius * .22)))
            pygame.draw.circle(self.screen, (125, 48, 43), (1030, 165), max(14, int(radius * .28)))
            draw_ship(self.screen, int(self.ship_x), int(self.ship_y + 48), 10,
                      flame=max(0.15, 1.0 - progress * .7), pilot=True)
            self._text("MARS APPROACH", 42, self.font_title, (255, 175, 130))
            self._text("Landing thrusters engaged...", 650, self.font_medium, (255, 220, 150))
            return

        # Keep the space-flight view clear; Mars is drawn only in the landing scene.
        for i in range(1, 24):
            t = i / 24
            pygame.draw.circle(self.screen, (70, 105, 150),
                               (int(205 + t * 720), int(500 - t * 330)), 2)

        for rock in self.flight_asteroids:
            radius = rock[4]
            pygame.draw.circle(self.screen, (115, 113, 124), (int(rock[0]), int(rock[1])), radius)
            pygame.draw.circle(self.screen, (70, 72, 86),
                               (int(rock[0] - 5), int(rock[1] - 5)), max(3, radius // 3))

        if self.flight_invulnerable <= 0 or int(self.flight_invulnerable * 12) % 2 == 0:
            draw_ship(self.screen, int(self.ship_x), int(self.ship_y + 48), 10, flame=0.8, pilot=True)
        if self.shield_active:
            pygame.draw.circle(self.screen, (90, 235, 255),
                               (int(self.ship_x), int(self.ship_y)), 47, 3)

        self._text("MOON  →  MARS: DIAGONAL SPACE FLIGHT", 35, self.font_title, (140, 225, 255))
        progress = min(1.0, self.flight_time / self.flight_duration)
        pygame.draw.rect(self.screen, (35, 48, 72), (330, 62, 440, 13), border_radius=6)
        pygame.draw.rect(self.screen, (70, 225, 255), (330, 62, int(440 * progress), 13), border_radius=6)
        self._text(f"SHIP HULL: {self.flight_lives}", 120, self.font_medium, (255, 225, 150))
        self._text("Move: WASD / Arrow Keys     Hold SPACE: shield", 625, self.font_small)
        self._text(self.flight_message, 660, self.font_small, (255, 220, 175))

    def draw_background(self):
        self.screen.fill((18, 10, 30))
        for x, y, radius in self.stars:
            pygame.draw.circle(self.screen, (170, 165, 190), (x, y), radius)
        pygame.draw.polygon(self.screen, (80, 32, 43), self.mountains_far)
        pygame.draw.polygon(self.screen, (112, 43, 43), self.mountains_near)
        pygame.draw.rect(self.screen, (150, 57, 44), (0, 475, 1100, 225))
        pygame.draw.rect(self.screen, (187, 79, 51), (0, 475, 1100, 8))
        for x, y, w, h in [(100, 625, 50, 14), (320, 660, 65, 16), (720, 630, 48, 13), (930, 670, 80, 17)]:
            pygame.draw.ellipse(self.screen, (103, 40, 38), (x, y, w, h))

        # Giant alien door with three diamond sockets.
        door_rect = pygame.Rect(835, 425, 105, 155)
        door_color = (65, 95, 115) if not self.door_open else (24, 35, 48)
        pygame.draw.rect(self.screen, (35, 45, 62), door_rect.inflate(16, 12), border_radius=9)
        pygame.draw.rect(self.screen, door_color, door_rect, border_radius=7)
        pygame.draw.rect(self.screen, (160, 190, 205), door_rect, 3, border_radius=7)
        if not self.door_open:
            for sx in (860, 887, 914):
                pygame.draw.polygon(self.screen, (60, 245, 230), [(sx, 455), (sx + 10, 465), (sx, 475), (sx - 10, 465)])
            pygame.draw.circle(self.screen, (255, 190, 75), (887, 515), 8)
        else:
            pygame.draw.rect(self.screen, (8, 15, 28), (849, 440, 77, 132), border_radius=5)
            pygame.draw.line(self.screen, (80, 245, 220), (850, 445), (850, 570), 3)
            pygame.draw.line(self.screen, (80, 245, 220), (925, 445), (925, 570), 3)

        # The golden key is revealed only after the diamond door opens.
        if self.door_open and not self.has_key:
            kx, ky = 888, 520
            glow = 5 + int(abs(math.sin(self.console_flash * 3)) * 4)
            pygame.draw.circle(self.screen, (255, 205, 70), (kx, ky - 12), 11 + glow, 2)
            pygame.draw.circle(self.screen, (255, 213, 75), (kx, ky - 12), 9, 4)
            pygame.draw.line(self.screen, (255, 213, 75), (kx, ky - 3), (kx + 18, ky + 15), 6)
            pygame.draw.line(self.screen, (255, 213, 75), (kx + 12, ky + 9), (kx + 6, ky + 15), 4)
            pygame.draw.line(self.screen, (255, 213, 75), (kx + 17, ky + 14), (kx + 11, ky + 20), 4)

        # Original spaceship artwork is reused at the exit.
        draw_ship(self.screen, 1040, 590, 12, flame=0.35 if self.stage == "escape" else 0.0, hatch=1.0, pilot=False)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (15, 20, 35), (15, 14, 235, 70), border_radius=9)
        pygame.draw.rect(self.screen, (105, 150, 180), (15, 14, 235, 70), 2, border_radius=9)
        self.screen.blit(self.font_small.render(f"LIVES: {self.lives}", True, (255, 125, 125)), (30, 24))
        self.screen.blit(self.font_small.render(f"DIAMONDS: {self.diamonds_found}/3", True, (120, 255, 225)), (30, 51))
        if self.stage == "diamonds":
            objective = "OBJECTIVE: COLLECT 3 DIAMONDS"
        elif self.stage == "door":
            objective = "OBJECTIVE: APPROACH THE DOOR AND PRESS E"
        elif self.stage == "key":
            objective = "OBJECTIVE: FIND THE BIG KEY — PRESS E"
        else:
            objective = "OBJECTIVE: TAKE THE KEY TO YOUR SHIP →"
        self._text(objective, 108, self.font_small, (255, 225, 160))

    def draw(self):
        if self.state in ("launch", "flight", "landing"):
            self.draw_flight()
            return
        if self.state == "flight_over":
            self.screen.fill((4, 7, 25))
            self._text("SHIP DISABLED", 235, self.font_large, (255, 90, 110))
            self._text("Asteroids damaged your ship. Try the Moon-to-Mars flight again.", 305, self.font_medium)
            self._text("Press ENTER to retry or ESC to quit", 380, self.font_medium, (180, 220, 255))
            return
        self.draw_background()

        if self.state == "briefing":
            overlay = pygame.Surface((1100, 700), pygame.SRCALPHA)
            overlay.fill((3, 6, 20, 225))
            self.screen.blit(overlay, (0, 0))
            self._text("ECLIPSE — LEVEL 3", 100, self.font_large, (255, 180, 120))
            self._text("MARS MYSTERY", 150, self.font_title, (255, 110, 90))
            instructions = [
                "1. Move across Mars and collect all three glowing diamonds.",
                "2. Red lasers turn on and off — wait until they switch off to cross.",
                "3. At the giant door, press E to place the three diamonds.",
                "4. Enter the opened chamber and press E near the big golden key.",
                "5. Carry the key to your spaceship on the far right to finish Level 3.",
                "Move: WASD / Arrow keys     Interact: E     Pause: P     Quit: ESC",
            ]
            for i, line in enumerate(instructions):
                self._text(line, 230 + i * 43, self.font_small if i == 5 else self.font_medium)
            self._button(pygame.Rect(385, 555, 330, 55), "PRESS ENTER / CLICK TO START")

        elif self.state == "playing":
            laser_on = (self.laser_phase % 2.8) < 1.65
            for laser in self.lasers:
                pole_color = (255, 50, 65) if laser_on else (75, 85, 105)
                pygame.draw.rect(self.screen, (48, 35, 48), (laser.x - 5, 490, laser.width + 10, 135), border_radius=5)
                pygame.draw.rect(self.screen, pole_color, laser, border_radius=5)
                if laser_on:
                    beam = pygame.Rect(laser.x - 16, 515, laser.width + 32, 5)
                    pygame.draw.rect(self.screen, (255, 105, 120), beam, border_radius=3)
                    pygame.draw.circle(self.screen, (255, 220, 220), beam.center, 4)
                else:
                    pygame.draw.circle(self.screen, (80, 255, 170), (laser.centerx, 508), 5)

            for diamond in self.diamonds:
                if diamond is not None:
                    pygame.draw.polygon(self.screen, (55, 255, 225), [(diamond.centerx, diamond.top), (diamond.right, diamond.centery), (diamond.centerx, diamond.bottom), (diamond.left, diamond.centery)])
                    pygame.draw.polygon(self.screen, (220, 255, 250), [(diamond.centerx, diamond.top + 5), (diamond.centerx + 5, diamond.centery), (diamond.centerx, diamond.bottom - 5), (diamond.centerx - 5, diamond.centery)])

            # Flash briefly after a laser hit, while preserving the original character design.
            if self.invulnerable <= 0 or int(self.invulnerable * 12) % 2 == 0:
                draw_astronaut(self.screen, int(self.player_x), int(self.player_y), sc=0.9, phase=self.walk_phase, face=self.facing)
            if self.has_key:
                pygame.draw.circle(self.screen, (255, 210, 75), (int(self.player_x + 20), int(self.player_y - 42)), 6, 3)
                pygame.draw.line(self.screen, (255, 210, 75), (int(self.player_x + 20), int(self.player_y - 36)), (int(self.player_x + 30), int(self.player_y - 28)), 3)

            self.draw_hud()
            if self.message_timer > 0:
                self._text(self.message, 143, self.font_small, (255, 235, 150))
            if self.stage == "door" and self._near(875, 95):
                self._text("PRESS E TO PLACE THE DIAMONDS", 180, self.font_small, (120, 255, 225))
            elif self.stage == "key" and self._near(920, 100):
                self._text("PRESS E TO PICK UP THE BIG KEY", 180, self.font_small, (255, 220, 90))
            if self.paused:
                self._text("PAUSED — PRESS P TO RESUME", 350, self.font_large, (255, 225, 140))

        elif self.state == "success":
            overlay = pygame.Surface((1100, 700), pygame.SRCALPHA)
            overlay.fill((2, 8, 20, 238))
            self.screen.blit(overlay, (0, 0))
            self._text("LEVEL 3 COMPLETE!", 180, self.font_large, (100, 255, 200))
            self._text("You collected all three diamonds and opened the ancient door.", 255, self.font_medium)
            self._text("You found the BIG GOLDEN KEY and escaped to your spaceship!", 300, self.font_medium, (255, 220, 120))
            self._text("The treasure vault remains locked... until Level 4.", 355, self.font_medium, (180, 220, 255))
            self._button(pygame.Rect(300, 490, 245, 54), "NEXT LEVEL")
            self._button(pygame.Rect(565, 490, 235, 54), "QUIT", False)

        elif self.state == "game_over":
            overlay = pygame.Surface((1100, 700), pygame.SRCALPHA)
            overlay.fill((3, 5, 15, 235))
            self.screen.blit(overlay, (0, 0))
            self._text("MISSION FAILED", 220, self.font_large, (255, 90, 100))
            self._text("You ran out of lives. Try timing the laser beams carefully.", 290, self.font_medium)
            self._button(pygame.Rect(385, 490, 330, 54), "TRY AGAIN")
            self._button(pygame.Rect(565, 555, 235, 54), "QUIT", False)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.04)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
            pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((MarsAdventure.WIDTH, MarsAdventure.HEIGHT))
    pygame.display.set_caption("ECLIPSE - Level 3: Mars Mystery")

    game = None

    def finish_game():
        if game is not None:
            game.running = False

    # This file runs Level 3 only; it does not import or recreate Level 2 or Level 4.
    game = MarsAdventure(screen, on_complete=finish_game, on_exit=finish_game)
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
