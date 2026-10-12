

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





# ECLIPSE - LEVEL 2: LUNAR SURVIVAL

#

# Controls:

#   WASD / Arrow keys : Move

#   Left mouse button : Fire toward cursor

#   SPACE             : Fire at nearest alien

#   P                 : Pause / resume

#   R                 : Restart after game over

#   ESC               : Exit level





class Level2:

    WIDTH = 1100

    HEIGHT = 700



    PART_NAMES = ["Engine", "Wing", "Power Core", "Antenna", "Fuel Cell", "Landing Gear"]



    def __init__(self, screen, on_complete=None, on_exit=None):

        self.screen = screen

        self.on_complete = on_complete

        self.on_exit = on_exit



        self.world = pygame.Surface(

            (self.WIDTH, self.HEIGHT)

        ).convert()



        self.clock = pygame.time.Clock()

        self.running = True

        self.paused = False

        self.state = "briefing"



        self.rng = random.Random(21)



        self.stars = [

            (

                self.rng.randrange(self.WIDTH),

                self.rng.randrange(10, 455),

                self.rng.choice((1, 1, 1, 2)),

                self.rng.randrange(95, 220)

            )

            for _ in range(180)

        ]



        self.distant_craters = [

            (110, 612, 45, 13),

            (315, 655, 63, 17),

            (560, 605, 38, 12),

            (815, 660, 72, 18),

            (1015, 615, 47, 14),

            (680, 681, 29, 8),

        ]



        self.rocks = [

            (150, 642, 1.0),

            (390, 626, 0.8),

            (735, 650, 1.15),

            (955, 638, 0.9),

            (535, 671, 0.7),

            (1040, 676, 0.65),

        ]



        self.font_small = pygame.font.Font(None, 22)

        self.font_medium = pygame.font.Font(None, 30)

        self.font_large = pygame.font.Font(None, 58)

        self.font_title = pygame.font.Font(None, 36)



        self.reset_game()



    def reset_game(self):

        self.player_x = self.WIDTH * 0.5

        self.player_y = self.HEIGHT * 0.78



        self.player_speed = 235.0

        self.player_health = 100.0

        self.oxygen = 100.0



        self.oxygen_drain_rate = 2.5

        self.oxygen_tanks_collected = 0

        self.minimum_tanks_required = 0



        self.collected_parts = set()

        self.collectibles = []



        self.damage_cooldown = 0.0

        self.hit_flash = 0.0

        self.walk_time = 0.0

        self.facing = 1

        self.shot_cooldown = 0.0



        self.aliens = []

        self.bullets = []

        self.particles = []



        self.spawn_timer = 1.0

        self.alien_spawn_interval = 2.15

        self.alien_speed_base = 48.0



        self.kills = 0

        self.elapsed = 0.0

        self.shake = 0.0

        self.state = "briefing"

        self.paused = False



        self.message_timer = 0.0

        self.message = "COLLECT ALL SIX PARTS, THEN RETURN TO YOUR CRASHED SHIP"



        self.completion_called = False
        self.continue_message = ""
        self.crash_site = (550.0, 560.0)
        self.return_beacon_active = False



        self._spawn_collectibles()



    # --------------------------------------------------

    # COLLECTIBLES

    # --------------------------------------------------



    def _spawn_collectibles(self):

        self.collectibles.clear()



        # Six unique spaceship parts.

        part_positions = [

            (75, 585),

            (265, 615),

            (455, 570),

            (650, 620),

            (840, 575),

            (1030, 605),

        ]



        for name, position in zip(

            self.PART_NAMES, part_positions

        ):

            self.collectibles.append({

                "type": "part",

                "name": name,

                "x": float(position[0]),

                "y": float(position[1]),

                "radius": 17,

                "phase": random.uniform(0, math.tau),

            })



        # Five oxygen tanks, spaced apart across the playable area.

        tank_positions = [

            (165, 640),

            (365, 585),

            (565, 635),

            (765, 590),

            (955, 640),

        ]



        for x, y in tank_positions:

            self.collectibles.append({

                "type": "oxygen",

                "x": float(x),

                "y": float(y),

                "radius": 13,

                "phase": random.uniform(0, math.tau),

            })



    def _update_collectibles(self, dt):

        for item in self.collectibles[:]:

            item["phase"] += dt * 2.5



            distance = math.hypot(

                self.player_x - item["x"],

                self.player_y - item["y"]

            )



            if distance > item["radius"] + 22:

                continue



            if item["type"] == "oxygen":

                self.oxygen = min(100.0, self.oxygen + 40.0)

                self.oxygen_tanks_collected += 1



                self.message = (

                    f"OXYGEN TANK COLLECTED! "

                    f"TOTAL: {self.oxygen_tanks_collected}"

                )



                self.message_timer = 2.0



                self._burst(

                    item["x"],

                    item["y"],

                    (80, 220, 255),

                    16

                )



            else:

                self.collected_parts.add(item["name"])



                self.message = (

                    f"SHIP PART RECOVERED: {item['name'].upper()}"

                )



                self.message_timer = 2.5



                self._burst(

                    item["x"],

                    item["y"],

                    (255, 205, 95),

                    18

                )



            self.collectibles.remove(item)



        # Collecting every part activates the return-to-ship objective.
        # The mission is not complete until the astronaut reaches the crash site.
        if len(self.collected_parts) == len(self.PART_NAMES) and not self.return_beacon_active:
            self.return_beacon_active = True
            self.message = "ALL PARTS FOUND! RETURN TO YOUR CRASHED SPACESHIP"
            self.message_timer = 5.0



    def _draw_collectibles(self, surface):

        for item in self.collectibles:

            x = int(item["x"])

            y = int(

                item["y"] + math.sin(item["phase"]) * 3

            )



            if item["type"] == "oxygen":

                # Oxygen tank body.

                pygame.draw.rect(

                    surface,

                    (75, 190, 225),

                    (x - 9, y - 12, 18, 25),

                    border_radius=4

                )



                pygame.draw.rect(

                    surface,

                    (185, 245, 255),

                    (x - 5, y - 8, 10, 15),

                    border_radius=2

                )



                pygame.draw.rect(

                    surface,

                    (145, 155, 165),

                    (x - 5, y - 16, 10, 5),

                    border_radius=2

                )



                pygame.draw.line(

                    surface,

                    (40, 105, 145),

                    (x, y - 4),

                    (x, y + 4),

                    2

                )



                pygame.draw.ellipse(

                    surface,

                    (25, 26, 34),

                    (x - 13, y + 13, 26, 6)

                )



            else:

                # Different silhouettes identify the four ship parts.

                if item["name"] == "Engine":

                    pygame.draw.circle(

                        surface,

                        (145, 155, 170),

                        (x, y),

                        14

                    )

                    pygame.draw.circle(

                        surface,

                        (65, 85, 110),

                        (x, y),

                        8

                    )

                    pygame.draw.circle(

                        surface,

                        (255, 135, 65),

                        (x, y),

                        4

                    )



                elif item["name"] == "Wing":

                    pygame.draw.polygon(

                        surface,

                        (195, 200, 210),

                        [

                            (x - 16, y - 5),

                            (x + 14, y - 12),

                            (x + 8, y + 10),

                            (x - 13, y + 8),

                        ]

                    )

                    pygame.draw.line(

                        surface,

                        (105, 125, 150),

                        (x - 12, y + 3),

                        (x + 10, y - 5),

                        3

                    )



                elif item["name"] == "Fuel Cell":
                    pygame.draw.rect(
                        surface,
                        (190, 115, 55),
                        (x - 12, y - 15, 24, 30),
                        border_radius=4
                    )
                    pygame.draw.rect(
                        surface,
                        (255, 205, 110),
                        (x - 7, y - 9, 14, 18),
                        border_radius=2
                    )
                    pygame.draw.line(
                        surface, (235, 225, 200),
                        (x - 5, y - 19), (x + 5, y - 19), 3
                    )

                elif item["name"] == "Landing Gear":
                    pygame.draw.line(
                        surface, (205, 215, 225),
                        (x - 12, y - 12), (x + 10, y + 10), 5
                    )
                    pygame.draw.line(
                        surface, (205, 215, 225),
                        (x + 12, y - 12), (x - 10, y + 10), 5
                    )
                    pygame.draw.line(
                        surface, (115, 140, 165),
                        (x - 15, y + 12), (x + 15, y + 12), 4
                    )

                elif item["name"] == "Power Core":

                    pygame.draw.polygon(

                        surface,

                        (115, 80, 185),

                        [

                            (x, y - 16),

                            (x + 14, y - 7),

                            (x + 11, y + 10),

                            (x, y + 16),

                            (x - 11, y + 10),

                            (x - 14, y - 7),

                        ]

                    )

                    pygame.draw.circle(

                        surface,

                        (135, 245, 255),

                        (x, y),

                        6

                    )



                else:

                    pygame.draw.line(

                        surface,

                        (190, 200, 210),

                        (x, y + 12),

                        (x, y - 7),

                        4

                    )

                    pygame.draw.line(

                        surface,

                        (190, 200, 210),

                        (x - 12, y - 7),

                        (x + 12, y - 7),

                        3

                    )

                    pygame.draw.arc(

                        surface,

                        (100, 220, 255),

                        (x - 12, y - 18, 24, 22),

                        0,

                        math.pi,

                        3

                    )



                pygame.draw.circle(

                    surface,

                    (255, 215, 110),

                    (x, y),

                    21,

                    1

                )



    # --------------------------------------------------

    # EVENTS

    # --------------------------------------------------



    def handle_event(self, event):

        if event.type == pygame.QUIT:

            self.running = False



            if self.on_exit:

                self.on_exit()



            return



        if event.type == pygame.KEYDOWN:

            if self.state == "briefing" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.state = "playing"
                self.message = "SEARCH THE MOON FOR SIX SHIP PARTS AND OXYGEN"
                self.message_timer = 4.0
                return

            if self.state == "mission_complete" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.on_complete:
                    self.completion_called = True
                    self.on_complete()
                else:
                    self.continue_message = "NEXT LEVEL IS NOT CONNECTED YET"
                return

            if event.key == pygame.K_ESCAPE:

                self.running = False



                if self.on_exit:

                    self.on_exit()



            elif (

                event.key == pygame.K_p

                and self.state == "playing"

            ):

                self.paused = not self.paused



            elif (

                event.key == pygame.K_r

                and self.state in ("game_over", "mission_complete")

            ):

                self.reset_game()



            elif (

                event.key == pygame.K_SPACE

                and self.state == "playing"

                and not self.paused

            ):

                self.fire_at_nearest()



        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._mouse_to_world(event.pos)

            if self.state == "briefing":
                if pygame.Rect(385, 525, 330, 58).collidepoint(mx, my):
                    self.state = "playing"
                    self.message = "SEARCH THE MOON FOR SIX SHIP PARTS AND OXYGEN"
                    self.message_timer = 4.0
                return

            if self.state == "mission_complete":
                if pygame.Rect(300, 430, 245, 54).collidepoint(mx, my):
                    if self.on_complete:
                        self.completion_called = True
                        self.on_complete()
                    else:
                        self.continue_message = "NEXT LEVEL IS NOT CONNECTED YET"
                elif pygame.Rect(565, 430, 235, 54).collidepoint(mx, my):
                    self.running = False
                    if self.on_exit:
                        self.on_exit()
                return

            if self.state == "playing" and not self.paused:
                self.fire_toward(mx, my)



        if (

            event.type == pygame.MOUSEMOTION

            and self.state == "playing"

        ):

            mx, _ = self._mouse_to_world(event.pos)



            if mx < self.player_x:

                self.facing = -1

            elif mx > self.player_x:

                self.facing = 1



    def _mouse_to_world(self, pos):

        target_w, target_h = self.screen.get_size()



        if target_w <= 0 or target_h <= 0:

            return pos



        return (

            pos[0] * self.WIDTH / target_w,

            pos[1] * self.HEIGHT / target_h

        )



    # --------------------------------------------------

    # GAME UPDATE

    # --------------------------------------------------



    def update(self, dt):

        dt = min(max(dt, 0.0), 0.04)



        if self.state != "playing" or self.paused:

            return



        self.elapsed += dt

        self.walk_time += dt * 9.0



        self.shot_cooldown = max(

            0.0, self.shot_cooldown - dt

        )

        self.damage_cooldown = max(

            0.0, self.damage_cooldown - dt

        )

        self.hit_flash = max(

            0.0, self.hit_flash - dt

        )

        self.shake = max(

            0.0, self.shake - dt * 18.0

        )

        self.message_timer = max(

            0.0, self.message_timer - dt

        )



        # Oxygen drains continuously.

        # It drains faster later in the mission.

        self.oxygen_drain_rate = min(

            4.2,

            2.5 + self.elapsed * 0.006

        )



        self.oxygen = max(

            0.0,

            self.oxygen - self.oxygen_drain_rate * dt

        )



        keys = pygame.key.get_pressed()



        dx = float(

            keys[pygame.K_d] or keys[pygame.K_RIGHT]

        ) - float(

            keys[pygame.K_a] or keys[pygame.K_LEFT]

        )



        dy = float(

            keys[pygame.K_s] or keys[pygame.K_DOWN]

        ) - float(

            keys[pygame.K_w] or keys[pygame.K_UP]

        )



        if dx or dy:

            length = math.hypot(dx, dy)

            dx /= length

            dy /= length



            self.player_x += dx * self.player_speed * dt

            self.player_y += dy * self.player_speed * dt



            if dx:

                self.facing = 1 if dx > 0 else -1



        self.player_x = max(

            34, min(self.WIDTH - 34, self.player_x)

        )

        self.player_y = max(

            465, min(650, self.player_y)

        )



        self._update_spawning(dt)

        self._update_aliens(dt)

        self._update_bullets(dt)

        self._update_particles(dt)

        self._update_collectibles(dt)

        if self.return_beacon_active and self.state == "playing":
            distance_to_ship = math.hypot(
                self.player_x - self.crash_site[0],
                self.player_y - self.crash_site[1]
            )
            if distance_to_ship <= 58:
                self.state = "mission_complete"
                self.message = "YOU RETURNED TO YOUR CRASHED SPACESHIP"
                self.message_timer = 0.0

        if self.player_health <= 0 or self.oxygen <= 0:

            self.player_health = max(0.0, self.player_health)



            if self.oxygen <= 0:

                self.message = "OXYGEN DEPLETED"

            else:

                self.message = "SUIT INTEGRITY LOST"



            self.state = "game_over"



    # --------------------------------------------------

    # ALIENS

    # --------------------------------------------------



    def _update_spawning(self, dt):

        self.spawn_timer -= dt



        self.alien_spawn_interval = max(

            0.85, 2.15 - self.elapsed * 0.012

        )



        max_aliens = min(

            14,

            9 + int(self.elapsed // 45)

        )



        if self.spawn_timer <= 0 and len(self.aliens) < max_aliens:

            self.spawn_alien()



            self.spawn_timer = (

                self.alien_spawn_interval

                * random.uniform(0.78, 1.22)

            )



    def spawn_alien(self):

        side = random.choice(("left", "right", "back"))



        if side == "left":

            x = random.randint(35, 100)

            y = random.randint(490, 640)



        elif side == "right":

            x = random.randint(

                self.WIDTH - 100,

                self.WIDTH - 35

            )

            y = random.randint(490, 640)



        else:

            x = random.randint(100, self.WIDTH - 100)

            y = random.randint(475, 520)



        heavy_chance = min(

            0.55,

            0.20 + self.elapsed * 0.003

        )



        heavy = (

            self.elapsed > 25

            and random.random() < heavy_chance

        )



        self.aliens.append({

            "x": float(x),

            "y": float(y),

            "hp": 3 if heavy else 1,

            "max_hp": 3 if heavy else 1,

            "speed": (

                random.uniform(43, 61)

                + min(38, self.elapsed * 0.16)

            ),

            "radius": 21 if heavy else 15,

            "phase": random.uniform(0, math.tau),

            "heavy": heavy,

            "flash": 0.0,

        })



    def _update_aliens(self, dt):

        for alien in self.aliens[:]:

            alien["flash"] = max(

                0.0, alien["flash"] - dt

            )



            dx = self.player_x - alien["x"]

            dy = self.player_y - alien["y"]



            distance = math.hypot(dx, dy)



            if distance > 0.001:

                alien["x"] += (

                    dx / distance

                    * alien["speed"]

                    * dt

                )

                alien["y"] += (

                    dy / distance

                    * alien["speed"]

                    * dt

                )



            alien["phase"] += dt * 4.0



            if (

                distance < alien["radius"] + 19

                and self.damage_cooldown <= 0

            ):

                self.player_health = max(

                    0.0, self.player_health - 18.0

                )



                self.damage_cooldown = 0.7

                self.hit_flash = 0.22

                self.shake = 7.0



                self._burst(

                    self.player_x,

                    self.player_y,

                    (255, 90, 75),

                    9

                )



                if distance > 0.001:

                    alien["x"] -= dx / distance * 35

                    alien["y"] -= dy / distance * 35



    # --------------------------------------------------

    # SHOOTING

    # --------------------------------------------------



    def _update_bullets(self, dt):

        for bullet in self.bullets[:]:

            bullet["x"] += bullet["vx"] * dt

            bullet["y"] += bullet["vy"] * dt

            bullet["life"] -= dt



            if (

                bullet["life"] <= 0

                or not (

                    -20 <= bullet["x"] <= self.WIDTH + 20

                    and 0 <= bullet["y"] <= self.HEIGHT

                )

            ):

                self.bullets.remove(bullet)

                continue



            for alien in self.aliens[:]:

                distance = math.hypot(

                    alien["x"] - bullet["x"],

                    alien["y"] - bullet["y"]

                )



                if distance < alien["radius"] + 5:

                    alien["hp"] -= 1

                    alien["flash"] = 0.12



                    self._burst(

                        bullet["x"],

                        bullet["y"],

                        (100, 235, 255),

                        5

                    )



                    if bullet in self.bullets:

                        self.bullets.remove(bullet)



                    if alien["hp"] <= 0:

                        self.aliens.remove(alien)

                        self.kills += 1



                        self._burst(

                            alien["x"],

                            alien["y"],

                            (105, 255, 155),

                            17

                        )



                    break



    def fire_at_nearest(self):

        if self.shot_cooldown > 0:

            return



        if self.aliens:

            target = min(

                self.aliens,

                key=lambda alien: math.hypot(

                    alien["x"] - self.player_x,

                    alien["y"] - self.player_y

                )

            )



            self.fire_toward(

                target["x"], target["y"]

            )



        else:

            self.fire_toward(

                self.player_x + self.facing * 100,

                self.player_y

            )



    def fire_toward(self, target_x, target_y):

        if (

            self.shot_cooldown > 0

            or self.state != "playing"

            or self.paused

        ):

            return



        start_x = self.player_x + self.facing * 20

        start_y = self.player_y - 5



        dx = target_x - start_x

        dy = target_y - start_y



        length = math.hypot(dx, dy)



        if length < 0.001:

            dx, dy, length = float(self.facing), 0.0, 1.0



        speed = 560.0



        self.bullets.append({

            "x": start_x,

            "y": start_y,

            "vx": dx / length * speed,

            "vy": dy / length * speed,

            "life": 1.15,

        })



        self.shot_cooldown = 0.22



        self._burst(

            start_x,

            start_y,

            (90, 225, 255),

            3

        )



    # --------------------------------------------------

    # PARTICLES

    # --------------------------------------------------



    def _update_particles(self, dt):

        for particle in self.particles[:]:

            particle["x"] += particle["vx"] * dt

            particle["y"] += particle["vy"] * dt



            particle["vx"] *= max(

                0.0, 1.0 - dt * 1.8

            )

            particle["vy"] *= max(

                0.0, 1.0 - dt * 1.8

            )



            particle["life"] -= dt



            if particle["life"] <= 0:

                self.particles.remove(particle)



    def _burst(self, x, y, color, count):

        for _ in range(count):

            angle = random.uniform(0, math.tau)

            speed = random.uniform(45, 185)

            life = random.uniform(0.18, 0.55)



            self.particles.append({

                "x": float(x),

                "y": float(y),

                "vx": math.cos(angle) * speed,

                "vy": math.sin(angle) * speed,

                "life": life,

                "max_life": life,

                "size": random.randint(2, 4),

                "color": color,

            })



    # --------------------------------------------------

    # DRAWING

    # --------------------------------------------------



    def draw(self, target=None):

        surface = self.world



        self._draw_background(surface)

        self._draw_lunar_surface(surface)

        self._draw_collectibles(surface)

        if self.return_beacon_active and self.state == "playing":
            bx, by = int(self.crash_site[0]), int(self.crash_site[1] - 52)
            pulse = 18 + int(4 * math.sin(self.elapsed * 5.0))
            pygame.draw.circle(surface, (70, 225, 255), (bx, by), pulse, 3)
            pygame.draw.line(surface, (70, 225, 255), (bx, by + pulse), (bx, by + pulse + 18), 3)
            beacon_text = self.font_small.render("RETURN TO SHIP", True, (150, 235, 255))
            surface.blit(beacon_text, beacon_text.get_rect(center=(bx + 85, by - 4)))

        for alien in sorted(

            self.aliens,

            key=lambda item: item["y"]

        ):

            self._draw_alien(surface, alien)



        for bullet in self.bullets:

            tail_x = bullet["x"] - bullet["vx"] * 0.025

            tail_y = bullet["y"] - bullet["vy"] * 0.025



            pygame.draw.line(

                surface,

                (45, 155, 220),

                (int(tail_x), int(tail_y)),

                (int(bullet["x"]), int(bullet["y"])),

                5

            )



            pygame.draw.circle(

                surface,

                (180, 250, 255),

                (int(bullet["x"]), int(bullet["y"])),

                3

            )



        self._draw_astronaut(surface)

        self._draw_particles(surface)

        self._draw_hud(surface)



        if self.hit_flash > 0:

            overlay = pygame.Surface(

                (self.WIDTH, self.HEIGHT),

                pygame.SRCALPHA

            )



            overlay.fill((

                255,

                35,

                35,

                int(65 * self.hit_flash / 0.22)

            ))



            surface.blit(overlay, (0, 0))



        if self.state == "briefing":
            self._draw_briefing(surface)

        elif self.paused:

            self._draw_center_panel(

                surface,

                "MISSION PAUSED",

                "Press P to resume"

            )



        elif self.state == "game_over":

            self._draw_center_panel(

                surface,

                "MISSION FAILED",

                "Press R to retry  |  ESC to exit"

            )



        elif self.state == "mission_complete":
            self._draw_success_screen(surface)



        elif self.message_timer > 0:

            self._draw_mission_message(surface)



        target = target or self.screen



        if target.get_size() == (

            self.WIDTH, self.HEIGHT

        ):

            target.blit(surface, (0, 0))



        else:

            scaled = pygame.transform.smoothscale(

                surface,

                target.get_size()

            )

            target.blit(scaled, (0, 0))



    def _draw_background(self, surface):

        surface.fill((3, 5, 16))



        glow = pygame.Surface(

            (self.WIDTH, self.HEIGHT),

            pygame.SRCALPHA

        )



        pygame.draw.ellipse(

            glow,

            (25, 42, 73, 55),

            (170, 250, 780, 320)

        )



        pygame.draw.ellipse(

            glow,

            (45, 70, 100, 25),

            (280, 300, 560, 220)

        )



        surface.blit(glow, (0, 0))



        for x, y, radius, brightness in self.stars:

            pulse = (

                0.88

                + 0.12 * math.sin(

                    self.elapsed * 1.7 + x * 0.03

                )

            )



            c = int(brightness * pulse)



            pygame.draw.circle(

                surface,

                (c, c, min(255, c + 8)),

                (x, y),

                radius

            )



        # Earth.

        earth_x, earth_y = 865, 150



        pygame.draw.circle(

            surface, (16, 47, 92),

            (earth_x, earth_y), 51

        )



        pygame.draw.circle(

            surface, (40, 111, 183),

            (earth_x - 5, earth_y - 3), 46

        )



        pygame.draw.ellipse(

            surface, (70, 151, 112),

            (832, 119, 24, 19)

        )



        pygame.draw.ellipse(

            surface, (73, 157, 118),

            (858, 143, 28, 17)

        )



        pygame.draw.ellipse(

            surface, (50, 127, 97),

            (842, 163, 18, 22)

        )



        pygame.draw.arc(

            surface, (115, 190, 235),

            (814, 99, 102, 102),

            0.4, 2.8, 3

        )



        pygame.draw.circle(

            surface, (160, 210, 245),

            (849, 130), 3

        )



        ridge = [

            (0, 505), (0, 478), (70, 459),

            (135, 486), (205, 450), (280, 483),

            (355, 463), (430, 493), (510, 454),

            (585, 481), (655, 451), (720, 480),

            (790, 459), (875, 486), (945, 453),

            (1030, 482), (1100, 463),

            (1100, 545), (0, 545)

        ]



        pygame.draw.polygon(

            surface, (34, 39, 54), ridge

        )



        pygame.draw.lines(

            surface, (70, 76, 91),

            False, ridge[1:-2], 2

        )



    def _draw_lunar_surface(self, surface):

        pygame.draw.rect(

            surface, (42, 43, 53),

            (0, 525, self.WIDTH, 175)

        )



        pygame.draw.line(

            surface, (104, 106, 119),

            (0, 526), (self.WIDTH, 526), 2

        )



        pygame.draw.polygon(

            surface, (54, 55, 65),

            [

                (0, 550), (140, 538), (280, 558),

                (425, 542), (560, 554), (730, 539),

                (880, 559), (1100, 542),

                (1100, 700), (0, 700)

            ]

        )



        for i in range(36):

            x = (i * 83 + 29) % self.WIDTH

            y = 565 + ((i * 37) % 125)

            length = 9 + (i % 5) * 5



            pygame.draw.line(

                surface, (67, 68, 78),

                (x, y), (x + length, y - 2), 1

            )



        for x, y, w, h in self.distant_craters:

            pygame.draw.ellipse(

                surface, (28, 29, 37),

                (x - w // 2, y - h // 2, w, h)

            )



            pygame.draw.arc(

                surface, (93, 94, 105),

                (x - w // 2, y - h // 2, w, h),

                0.1, math.pi - 0.1, 2

            )



        for x, y, scale in self.rocks:

            self._draw_rock(surface, x, y, scale)



                # Large crashed spaceship, reusing the Level 1 rocket artwork.
        # It is drawn as background scenery; all Level 2 gameplay stays the same.
        ship_surface = pygame.Surface((300, 330), pygame.SRCALPHA)
        draw_ship(
            ship_surface,
            150, 280, 26.0,
            flame=0.0, hatch=1.0, pilot=True
        )
        crashed_ship = pygame.transform.rotate(ship_surface, 68)
        surface.blit(
            crashed_ship,
            crashed_ship.get_rect(center=(185, 510))
        )

    def _draw_rock(self, surface, x, y, scale):

        points = [

            (x - 23 * scale, y),

            (x - 19 * scale, y - 13 * scale),

            (x - 7 * scale, y - 23 * scale),

            (x + 8 * scale, y - 20 * scale),

            (x + 21 * scale, y - 8 * scale),

            (x + 24 * scale, y),

        ]



        points = [

            (int(px), int(py))

            for px, py in points

        ]



        shadow = [

            (px + 5, py + 5)

            for px, py in points

        ]



        pygame.draw.polygon(

            surface, (28, 29, 36), shadow

        )



        pygame.draw.polygon(

            surface, (86, 88, 99), points

        )



        pygame.draw.polygon(

            surface, (118, 120, 130), points[:4]

        )



        pygame.draw.line(

            surface, (139, 141, 150),

            points[2], points[3], 2

        )



    def _draw_alien(self, surface, alien):

        x, y = int(alien["x"]), int(alien["y"])

        r = alien["radius"]



        bob = math.sin(alien["phase"]) * 2.5

        y = int(y + bob)



        if alien["heavy"]:

            body = (179, 132, 77)

            dark = (92, 58, 40)

            highlight = (242, 194, 118)

        else:

            body = (91, 203, 127)

            dark = (30, 83, 67)

            highlight = (156, 247, 170)



        pygame.draw.ellipse(

            surface, (23, 25, 32),

            (x - r - 7, y + r - 1, 2 * r + 14, 8)

        )



        leg_sway = int(

            math.sin(alien["phase"] * 1.5) * 3

        )



        pygame.draw.line(

            surface, dark,

            (x - 5, y + 9),

            (x - 9 + leg_sway, y + r + 8), 5

        )



        pygame.draw.line(

            surface, dark,

            (x + 5, y + 9),

            (x + 10 - leg_sway, y + r + 8), 5

        )



        pygame.draw.line(

            surface, body,

            (x - r + 2, y + 1),

            (x - r - 7, y + 11), 5

        )



        pygame.draw.line(

            surface, body,

            (x + r - 2, y + 1),

            (x + r + 7, y + 10), 5

        )



        spikes = [

            (x - 11, y - 7),

            (x - 8, y - 18),

            (x - 1, y - 10),

            (x + 5, y - 20),

            (x + 9, y - 8)

        ]



        pygame.draw.polygon(

            surface, dark,

            [(x - r, y + 3), *spikes, (x + r, y + 4)]

        )



        pygame.draw.ellipse(

            surface, dark,

            (x - r, y - r + 1, 2 * r, 2 * r + 5)

        )



        pygame.draw.ellipse(

            surface, body,

            (x - r + 3, y - r + 3, 2 * r - 6, 2 * r - 3)

        )



        pygame.draw.arc(

            surface, highlight,

            (x - r + 4, y - r + 3, 2 * r - 8, 2 * r - 5),

            3.5, 5.6, 2

        )



        eye_dir = 1 if self.player_x >= x else -1



        pygame.draw.ellipse(

            surface, (255, 65, 77),

            (x - 9 + eye_dir, y - 4, 7, 8)

        )



        pygame.draw.ellipse(

            surface, (255, 65, 77),

            (x + 2 + eye_dir, y - 4, 7, 8)

        )



        pygame.draw.circle(

            surface, (255, 225, 205),

            (x - 6 + eye_dir, y - 1), 2

        )



        pygame.draw.circle(

            surface, (255, 225, 205),

            (x + 5 + eye_dir, y - 1), 2

        )



        if alien["max_hp"] > 1:

            bar_w = 36

            bar_x = x - bar_w // 2

            bar_y = y - r - 11



            pygame.draw.rect(

                surface, (35, 35, 42),

                (bar_x, bar_y, bar_w, 4)

            )



            pygame.draw.rect(

                surface, (246, 183, 89),

                (

                    bar_x,

                    bar_y,

                    int(bar_w * alien["hp"] / alien["max_hp"]),

                    4

                )

            )



        if alien["flash"] > 0:

            pygame.draw.circle(

                surface, (230, 255, 255),

                (x, y), r + 5, 2

            )



    def _draw_astronaut(self, surface):
        x, y = int(self.player_x), int(self.player_y)

        moving = pygame.key.get_pressed()
        is_moving = any(
            moving[k]
            for k in (
                pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
            )
        )

        bob = abs(math.sin(self.walk_time)) * 2 if is_moving else 0
        y = int(y - bob)

        # Keep the existing ground shadow, then draw the Level 1 astronaut.
        pygame.draw.ellipse(
            surface, (23, 24, 31),
            (x - 23, y + 24, 47, 12)
        )
        draw_astronaut(
            surface,
            x, y + 34,
            sc=1.1,
            phase=self.walk_time if is_moving else 0.0,
            face=self.facing
        )

    def _draw_particles(self, surface):

        for particle in self.particles:

            ratio = max(

                0.0,

                particle["life"] / particle["max_life"]

            )



            color = tuple(

                int(c * ratio)

                for c in particle["color"]

            )



            radius = max(

                1, int(particle["size"] * ratio)

            )



            pygame.draw.circle(

                surface,

                color,

                (int(particle["x"]), int(particle["y"])),

                radius

            )



    # --------------------------------------------------

    # HUD — ORIGINAL STYLE PRESERVED

    # --------------------------------------------------



    def _draw_hud(self, surface):

        panel = pygame.Surface(

            (self.WIDTH, 82),

            pygame.SRCALPHA

        )



        panel.fill((4, 9, 20, 218))

        surface.blit(panel, (0, 0))



        pygame.draw.line(

            surface, (42, 113, 145),

            (0, 81), (self.WIDTH, 81), 2

        )



        title = self.font_title.render(

            "E C L I P S E  //  LUNAR SURVIVAL",

            True,

            (205, 235, 247)

        )



        surface.blit(title, (24, 14))



        subtitle = self.font_small.render(

            "MISSION 02  •  LANDING ZONE SECURITY",

            True,

            (109, 177, 202)

        )



        surface.blit(subtitle, (26, 49))



        # Health bar.

        health_label = self.font_small.render(

            "SUIT INTEGRITY",

            True,

            (185, 207, 219)

        )



        surface.blit(health_label, (530, 16))



        bar_x, bar_y, bar_w, bar_h = 530, 42, 225, 14



        pygame.draw.rect(

            surface, (34, 43, 55),

            (bar_x, bar_y, bar_w, bar_h),

            border_radius=4

        )



        fill_w = int(

            bar_w * self.player_health / 100

        )



        if self.player_health > 55:

            health_color = (72, 219, 156)

        elif self.player_health > 25:

            health_color = (245, 183, 81)

        else:

            health_color = (255, 81, 86)



        if fill_w > 0:

            pygame.draw.rect(

                surface, health_color,

                (bar_x, bar_y, fill_w, bar_h),

                border_radius=4

            )



        health_text = self.font_small.render(

            f"{int(self.player_health):03d}%",

            True,

            (235, 244, 248)

        )



        surface.blit(

            health_text,

            (bar_x + bar_w + 10, bar_y - 3)

        )



        # Existing enemy counter.

        kills_text = self.font_medium.render(

            f"HOSTILES  {self.kills:02d}",

            True,

            (133, 245, 180)

        )



        surface.blit(kills_text, (875, 20))



        # New oxygen bar.

        oxygen_label = self.font_small.render(

            "OXYGEN",

            True,

            (160, 220, 245)

        )



        surface.blit(oxygen_label, (530, 91))



        oxygen_x, oxygen_y = 600, 94

        oxygen_w, oxygen_h = 145, 12



        pygame.draw.rect(

            surface, (34, 43, 55),

            (oxygen_x, oxygen_y, oxygen_w, oxygen_h),

            border_radius=4

        )



        oxygen_fill = int(

            oxygen_w * self.oxygen / 100

        )



        if self.oxygen > 50:

            oxygen_color = (80, 200, 255)

        elif self.oxygen > 25:

            oxygen_color = (245, 183, 81)

        else:

            oxygen_color = (255, 65, 75)



        if oxygen_fill > 0:

            pygame.draw.rect(

                surface, oxygen_color,

                (oxygen_x, oxygen_y, oxygen_fill, oxygen_h),

                border_radius=4

            )



        oxygen_text = self.font_small.render(

            f"{int(self.oxygen):03d}%",

            True,

            (235, 244, 248)

        )



        surface.blit(

            oxygen_text,

            (oxygen_x + oxygen_w + 8, oxygen_y - 4)

        )



        # Mission objectives.

        parts_text = self.font_small.render(

            f"SHIP PARTS  {len(self.collected_parts)}/{len(self.PART_NAMES)}",

            True,

            (255, 211, 125)

        )



        tanks_text = self.font_small.render(

            f"OXYGEN TANKS  {self.oxygen_tanks_collected}/"

            "6",

            True,

            (130, 220, 255)

        )



        surface.blit(parts_text, (24, 94))

        surface.blit(tanks_text, (24, 118))



        # Objective reminder.

        objective = self.font_small.render(

            "OBJECTIVE: FIND PARTS, THEN RETURN TO CRASH SITE",

            True,

            (218, 220, 226)

        )



        surface.blit(objective, (24, 145))



        # Critical oxygen warning.

        if self.oxygen <= 25 and self.state == "playing":

            warning = self.font_medium.render(

                "WARNING: OXYGEN CRITICAL!",

                True,

                (255, 85, 85)

            )



            surface.blit(

                warning,

                warning.get_rect(

                    center=(self.WIDTH // 2, 190)

                )

            )



        # Critical health warning.

        if (

            self.player_health <= 25

            and self.state == "playing"

        ):

            warning = self.font_medium.render(

                "WARNING: SUIT INTEGRITY CRITICAL!",

                True,

                (255, 85, 85)

            )



            surface.blit(

                warning,

                warning.get_rect(

                    center=(self.WIDTH // 2, 220)

                )

            )



        controls = self.font_small.render(

            "MOVE  WASD/ARROWS     FIRE  CLICK / SPACE     PAUSE  P",

            True,

            (151, 165, 180)

        )



        surface.blit(

            controls,

            (self.WIDTH - controls.get_width() - 22,

             self.HEIGHT - 31)

        )



        # Targeting reticle.

        if self.aliens:

            target = min(

                self.aliens,

                key=lambda alien: math.hypot(

                    alien["x"] - self.player_x,

                    alien["y"] - self.player_y

                )

            )



            tx, ty = int(target["x"]), int(target["y"])



            pygame.draw.circle(

                surface, (110, 225, 255),

                (tx, ty), target["radius"] + 11, 1

            )



            pygame.draw.line(

                surface, (110, 225, 255),

                (tx - 22, ty), (tx - 15, ty), 1

            )



            pygame.draw.line(

                surface, (110, 225, 255),

                (tx + 15, ty), (tx + 22, ty), 1

            )



            pygame.draw.line(

                surface, (110, 225, 255),

                (tx, ty - 22), (tx, ty - 15), 1

            )



            pygame.draw.line(

                surface, (110, 225, 255),

                (tx, ty + 15), (tx, ty + 22), 1

            )



    def _draw_briefing(self, surface):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((1, 5, 18, 232))
        surface.blit(overlay, (0, 0))

        title = self.font_large.render("MISSION BRIEFING: LUNAR SURVIVAL", True, (105, 205, 255))
        surface.blit(title, title.get_rect(center=(self.WIDTH // 2, 125)))

        lines = [
            "• A forceful landing damaged the spaceship and scattered its parts.",
            "• Explore the Moon and collect all SIX spaceship parts.",
            "• Oxygen is limited. Find the SIX oxygen tanks; each restores 40%.",
            "• Watch out for hostile aliens while exploring.",
            "• After finding every part, return to the original crashed spaceship.",
            "• The mission only ends when you reach the crash site.",
        ]
        y = 220
        for line in lines:
            rendered = self.font_medium.render(line, True, (230, 239, 249))
            surface.blit(rendered, (95, y))
            y += 43

        self._draw_button(surface, pygame.Rect(385, 525, 330, 58), "START MISSION", True)
        hint = self.font_small.render("Press ENTER or click START MISSION", True, (155, 195, 220))
        surface.blit(hint, hint.get_rect(center=(self.WIDTH // 2, 605)))

    def _draw_success_screen(self, surface):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((1, 5, 18, 235))
        surface.blit(overlay, (0, 0))

        title = self.font_large.render("MISSION COMPLETE", True, (91, 255, 194))
        surface.blit(title, title.get_rect(center=(self.WIDTH // 2, 245)))

        details = [
            "All six spaceship parts recovered.",
            "You returned to the original crashed spaceship.",
            "Lunar survival mission completed successfully!",
        ]
        y = 305
        for line in details:
            rendered = self.font_medium.render(line, True, (225, 239, 248))
            surface.blit(rendered, rendered.get_rect(center=(self.WIDTH // 2, y)))
            y += 36

        self._draw_button(surface, pygame.Rect(300, 430, 245, 54), "CONTINUE TO NEXT LEVEL", True, compact=True)
        self._draw_button(surface, pygame.Rect(565, 430, 235, 54), "QUIT GAME", False)
        if self.continue_message:
            note = self.font_small.render(self.continue_message, True, (255, 207, 115))
            surface.blit(note, note.get_rect(center=(self.WIDTH // 2, 515)))

    def _draw_button(self, surface, rect, label, primary=True, compact=False):
        fill = (0, 92, 190, 230) if primary else (10, 25, 45, 235)
        color = (115, 220, 255) if primary else (70, 190, 235)
        button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        button_surface.fill(fill)
        surface.blit(button_surface, rect.topleft)
        pygame.draw.rect(surface, color, rect, 2, border_radius=9)
        font = self.font_small if compact else self.font_medium
        text = font.render(label, True, (245, 250, 255))
        surface.blit(text, text.get_rect(center=rect.center))

    def _draw_mission_message(self, surface):

        text = self.font_medium.render(

            self.message,

            True,

            (236, 226, 188)

        )



        plate = pygame.Surface(

            (text.get_width() + 28, 42),

            pygame.SRCALPHA

        )



        plate.fill((5, 10, 20, 190))



        px = (

            self.WIDTH - plate.get_width()

        ) // 2



        surface.blit(plate, (px, 170))

        surface.blit(text, (px + 14, 181))



    def _draw_center_panel(self, surface, heading, detail):

        overlay = pygame.Surface(

            (self.WIDTH, self.HEIGHT),

            pygame.SRCALPHA

        )



        overlay.fill((1, 3, 12, 190))

        surface.blit(overlay, (0, 0))



        title = self.font_large.render(

            heading,

            True,

            (220, 239, 248)

        )



        subtitle = self.font_medium.render(

            detail,

            True,

            (165, 202, 220)

        )



        surface.blit(

            title,

            title.get_rect(

                center=(self.WIDTH // 2, 305)

            )

        )



        surface.blit(

            subtitle,

            subtitle.get_rect(

                center=(self.WIDTH // 2, 365)

            )

        )



    # --------------------------------------------------

    # STANDALONE GAME LOOP

    # --------------------------------------------------



    def run(self):

        while self.running:

            dt = self.clock.tick(60) / 1000.0



            for event in pygame.event.get():

                self.handle_event(event)



            self.update(dt)

            self.draw()



            pygame.display.flip()





def main():

    pygame.init()



    screen = pygame.display.set_mode(

        (1100, 700)

    )



    pygame.display.set_caption(

        "ECLIPSE - Level 2: Lunar Survival"

    )



    level = Level2(screen)

    level.run()



    pygame.quit()

    sys.exit()





if __name__ == "__main__":

    main()
