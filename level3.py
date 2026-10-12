import pygame

import random

import math



pygame.init()



# ------------------------------------------------------------

# ECLIPSE - SPACE JET ADVENTURE: MARS MISSION

# Controls: WASD / Arrow keys to move, SPACE to shoot

# ENTER starts, R retries, ESC quits

# ------------------------------------------------------------



WIDTH, HEIGHT = 1000, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("ECLIPSE - Space Jet Adventure: Mars Mission")

clock = pygame.time.Clock()



BLACK = (5, 7, 20)

WHITE = (245, 248, 255)

CYAN = (60, 220, 255)

RED = (245, 65, 65)

ORANGE = (255, 145, 45)

GREEN = (80, 245, 120)

PURPLE = (150, 75, 220)

YELLOW = (255, 225, 70)

DARK_GREEN = (28, 83, 55)

SKIN_GREEN = (95, 155, 91)

LIGHT_GREEN = (155, 205, 130)

MARS_RED = (166, 62, 38)

MARS_LIGHT = (220, 105, 65)

MARS_DARK = (100, 38, 30)



font = pygame.font.SysFont("arial", 24)

small_font = pygame.font.SysFont("arial", 17)

big_font = pygame.font.SysFont("arial", 44, bold=True)



MENU, PLAYING, BOSS, LANDING, GAME_OVER, WIN = (

    "MENU", "PLAYING", "BOSS", "LANDING", "GAME_OVER", "WIN"

)

state = MENU



PLAYER_SPEED = 6

BOSS_MAX_HEALTH = 100

POWERUP_SIZE = 28



stars = [[random.randrange(WIDTH), random.randrange(HEIGHT),

          random.choice([1, 2, 3])] for _ in range(130)]



player = pygame.Rect(100, 280, 54, 38)

bullets, aliens, alien_bullets, powerups = [], [], [], []
particles, asteroids = [], []
asteroid_timer = 0
screen_shake = 0

score, lives, boss_health = 0, 3, BOSS_MAX_HEALTH

spawn_timer = boss_shot_timer = invincible_timer = 0

rapid_timer = shield_timer = shoot_timer = powerup_timer = 0

boss = pygame.Rect(790, 230, 145, 150)

boss_direction = 1

landing_progress = 0

rocket_y = 300

rocket_x = 120

landing_message = "APPROACHING MARS"





def draw_text(text, font_obj, color, x, y, center=False):

    image = font_obj.render(text, True, color)

    rect = image.get_rect()

    if center:

        rect.center = (x, y)

    else:

        rect.topleft = (x, y)

    screen.blit(image, rect)





def draw_mars(x=850, y=105, radius=62):

    # Planet shading and surface details

    pygame.draw.circle(screen, MARS_RED, (int(x), int(y)), radius)

    pygame.draw.circle(screen, MARS_DARK,

                       (int(x + radius * .35), int(y + radius * .12)),

                       int(radius * .72))

    pygame.draw.circle(screen, MARS_RED,

                       (int(x - radius * .18), int(y - radius * .10)),

                       int(radius * .78))

    pygame.draw.ellipse(screen, MARS_LIGHT,

                        (x - radius * .65, y - radius * .45,

                         radius * .58, radius * .24))

    pygame.draw.ellipse(screen, MARS_DARK,

                        (x + radius * .05, y + radius * .22,

                         radius * .48, radius * .19))

    pygame.draw.circle(screen, ORANGE,

                       (int(x - radius * .35), int(y + radius * .30)),

                       max(3, radius // 8))





def draw_background():

    screen.fill(BLACK)

    for star in stars:

        if state not in (MENU, WIN, GAME_OVER):

            star[0] -= star[2]

        if star[0] < 0:

            star[0] = WIDTH

            star[1] = random.randrange(HEIGHT)

        pygame.draw.circle(screen, WHITE,

                           (int(star[0]), int(star[1])), star[2] // 2 + 1)



    if state in (LANDING, WIN):

        # Mars surface / horizon

        pygame.draw.ellipse(screen, (72, 31, 29), (-100, 455, 1250, 280))

        pygame.draw.ellipse(screen, MARS_RED, (-60, 480, 1160, 230))

        for i in range(18):

            x = (i * 71 + 25) % WIDTH

            y = 505 + (i * 17) % 70

            pygame.draw.ellipse(screen, MARS_DARK, (x, y, 28, 6))

        draw_mars(820, 140, 80)

    else:

        draw_mars()





def draw_rocket(rect, flame=True, landed=False):
    """Draw the upright Level 1-style rocket: silver hull, red fins,
    blue cockpit, astronaut, orange bands, and an animated engine flame.
    The same design is used during gameplay and the Mars landing sequence.
    """
    # Gameplay uses a short hitbox, while the landing scene uses a tall one.
    horizontal_flight = rect.height < 50
    if horizontal_flight:
        # During combat the rocket flies horizontally across the screen,
        # with its nose pointing right and engine flame trailing behind.
        scale = 0.34
        center_x = rect.centerx
        bottom_y = rect.centery + 28
    else:
        scale = min(rect.width / 150, rect.height / 240)
        scale = max(0.28, min(scale, 0.42))
        center_x = rect.centerx
        bottom_y = rect.bottom

    s = scale
    width = max(60, int(150 * s))
    height = max(90, int(240 * s))
    rocket = pygame.Surface((width, height), pygame.SRCALPHA)
    cx = width // 2
    base = height - int(22 * s)

    def pt(x, y):
        return (int(cx + x * s), int(base - y * s))

    # Bright, layered exhaust below the engine bell.
    if flame and not landed:
        flicker = random.uniform(0.82, 1.18)
        length = 66 * s * flicker
        pygame.draw.polygon(rocket, (255, 80, 20),
                            [pt(-18, 4), pt(18, 4), pt(0, -length)])
        pygame.draw.polygon(rocket, (255, 175, 35),
                            [pt(-10, 2), pt(10, 2), pt(0, -length * 0.72)])
        pygame.draw.polygon(rocket, (255, 245, 175),
                            [pt(-4, 1), pt(4, 1), pt(0, -length * 0.42)])

    # Engine nozzle.
    pygame.draw.polygon(rocket, (65, 72, 88),
                        [pt(-23, 20), pt(23, 20), pt(18, 0), pt(-18, 0)])
    pygame.draw.line(rocket, (180, 188, 204), pt(-18, 6), pt(18, 6),
                     max(1, int(2 * s)))

    # Red side fins, matching the Level 1 rocket.
    pygame.draw.polygon(rocket, (150, 40, 48),
                        [pt(-20, 90), pt(-47, 12), pt(-22, 20), pt(-16, 88)])
    pygame.draw.polygon(rocket, (220, 66, 58),
                        [pt(20, 90), pt(47, 12), pt(22, 20), pt(16, 88)])
    pygame.draw.polygon(rocket, (105, 32, 42),
                        [pt(-47, 12), pt(-30, 18), pt(-22, 30)])
    pygame.draw.polygon(rocket, (170, 42, 48),
                        [pt(47, 12), pt(30, 18), pt(22, 30)])

    # Metallic silver body with shaded panels and a pointed nose cone.
    body = [pt(-22, 22), pt(-22, 150), pt(0, 218),
            pt(22, 150), pt(22, 22)]
    pygame.draw.polygon(rocket, (205, 212, 226), body)
    pygame.draw.polygon(rocket, (126, 137, 158),
                        [pt(-22, 22), pt(-22, 150), pt(0, 218), pt(0, 22)])
    pygame.draw.polygon(rocket, (242, 245, 250),
                        [pt(-5, 28), pt(-5, 155), pt(0, 192), pt(0, 28)])
    pygame.draw.polygon(rocket, (82, 91, 111), body, max(1, int(2 * s)))
    pygame.draw.line(rocket, (255, 255, 255), pt(-5, 191), pt(0, 211),
                     max(1, int(2 * s)))
    pygame.draw.line(rocket, (125, 135, 153), pt(0, 211), pt(5, 191),
                     max(1, int(2 * s)))

    # Blue glass cockpit with reflections and a small astronaut helmet.
    win_rect = pygame.Rect(0, 0, max(8, int(28 * s)), max(12, int(43 * s)))
    win_rect.center = pt(0, 139)
    pygame.draw.ellipse(rocket, (24, 54, 91), win_rect)
    inner = win_rect.inflate(-max(2, int(5 * s)), -max(2, int(5 * s)))
    pygame.draw.ellipse(rocket, (40, 117, 158), inner)
    pygame.draw.ellipse(rocket, (105, 225, 255), win_rect,
                        max(1, int(2 * s)))
    pygame.draw.arc(rocket, (220, 250, 255), win_rect.inflate(-3, -3),
                    1.0, 2.7, max(1, int(2 * s)))
    helmet = pygame.Rect(0, 0, max(5, int(15 * s)), max(6, int(17 * s)))
    helmet.center = (win_rect.centerx, win_rect.centery + int(5 * s))
    pygame.draw.ellipse(rocket, (238, 239, 243), helmet)
    visor = pygame.Rect(0, 0, max(4, int(10 * s)), max(4, int(7 * s)))
    visor.center = (helmet.centerx + int(1 * s), helmet.centery)
    pygame.draw.ellipse(rocket, (238, 181, 58), visor)
    pygame.draw.ellipse(rocket, (255, 232, 150), visor, 1)

    # Orange safety bands and small technical lights.
    for yy in (48, 56):
        pygame.draw.line(rocket, (238, 132, 52), pt(-21, yy), pt(21, yy),
                         max(1, int(2 * s)))
    for yy in (82, 104):
        for side in (-1, 1):
            pygame.draw.circle(rocket, (70, 198, 226), pt(side * 15, yy),
                               max(1, int(2.5 * s)))
    pygame.draw.rect(rocket, (70, 78, 95),
                     pygame.Rect(int(cx - 9 * s), int(base - 34 * s),
                                 max(2, int(18 * s)), max(2, int(8 * s))),
                     border_radius=max(1, int(2 * s)))

    if horizontal_flight:
        # Rotate the same Level 1-style rocket 90 degrees so it faces right.
        rocket = pygame.transform.rotate(rocket, -90)
        rocket_rect = rocket.get_rect(center=rect.center)
    else:
        rocket_rect = rocket.get_rect(midbottom=(int(center_x), int(bottom_y)))
    screen.blit(rocket, rocket_rect)


def draw_lander(x, y, scale=1.0, flame=False, landed=False):
    """Front-facing vertical Mars lander used in the cinematic ending."""
    x, y = int(x), int(y)
    def pt(dx, dy):
        return (int(x + dx * scale), int(y + dy * scale))
    # exhaust glow
    if flame and not landed:
        glow = pygame.Surface((int(70 * scale), int(55 * scale)), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 105, 25, 70),
                            (0, 0, int(70 * scale), int(55 * scale)))
        screen.blit(glow, (int(x - 35 * scale), int(y + 70 * scale)))
        pygame.draw.polygon(screen, ORANGE, [
            pt(-13, 67), pt(0, 112 + random.randint(0, 8)), pt(13, 67)
        ])
        pygame.draw.polygon(screen, YELLOW, [
            pt(-6, 67), pt(0, 96 + random.randint(0, 5)), pt(6, 67)
        ])
    # landing legs and feet
    leg_col = (72, 82, 91)
    if landed or flame:
        pygame.draw.line(screen, leg_col, pt(-18, 54), pt(-31, 83), max(2, int(4 * scale)))
        pygame.draw.line(screen, leg_col, pt(18, 54), pt(31, 83), max(2, int(4 * scale)))
        pygame.draw.line(screen, leg_col, pt(-36, 83), pt(-25, 83), max(2, int(4 * scale)))
        pygame.draw.line(screen, leg_col, pt(25, 83), pt(36, 83), max(2, int(4 * scale)))
    # shadowed capsule and nose
    pygame.draw.polygon(screen, (90, 102, 115), [
        pt(-21, 17), pt(-13, -4), pt(0, -13), pt(13, -4), pt(21, 17),
        pt(18, 61), pt(-18, 61)
    ])
    pygame.draw.polygon(screen, (204, 216, 225), [
        pt(-16, 17), pt(-10, -2), pt(0, -9), pt(10, -2), pt(16, 17),
        pt(14, 58), pt(-14, 58)
    ])
    pygame.draw.ellipse(screen, (25, 70, 101),
                        (int(x - 11 * scale), int(y + 8 * scale),
                         int(22 * scale), int(19 * scale)))
    pygame.draw.ellipse(screen, (65, 177, 215),
                        (int(x - 8 * scale), int(y + 10 * scale),
                         int(15 * scale), int(13 * scale)))
    pygame.draw.ellipse(screen, (218, 249, 255),
                        (int(x - 5 * scale), int(y + 11 * scale),
                         int(6 * scale), int(4 * scale)))
    # thermal shield, seams and side thrusters
    pygame.draw.line(screen, (102, 119, 133), pt(-13, 34), pt(13, 34), max(1, int(2 * scale)))
    pygame.draw.rect(screen, (115, 129, 142),
                     (int(x - 17 * scale), int(y + 39 * scale),
                      int(34 * scale), max(2, int(8 * scale))),
                     border_radius=max(1, int(2 * scale)))
    pygame.draw.circle(screen, (255, 180, 55), pt(-17, 47), max(2, int(3 * scale)))
    pygame.draw.circle(screen, (255, 180, 55), pt(17, 47), max(2, int(3 * scale)))


def draw_real_alien(alien):
    """Layered pseudo-3D alien creature with glossy eyes and animated limbs."""
    x, y, w, h = alien.x, alien.y, alien.width, alien.height
    cx = x + w // 2
    t = pygame.time.get_ticks() / 100
    sway = int(math.sin(t + x * 0.05) * 4)
    # shadow behind the creature
    pygame.draw.ellipse(screen, (20, 28, 31),
                        (x + 3, y + h - 3, w - 2, 9))
    # arms, elbows and clawed fingers
    arm_dark = (34, 77, 55)
    arm_light = (93, 146, 91)
    pygame.draw.line(screen, arm_dark, (x + 12, y + 20),
                     (x + 2, y + 29 + sway), 7)
    pygame.draw.line(screen, arm_light, (x + 12, y + 20),
                     (x + 3, y + 28 + sway), 3)
    pygame.draw.line(screen, arm_dark, (x + w - 12, y + 20),
                     (x + w - 2, y + 29 - sway), 7)
    pygame.draw.line(screen, arm_light, (x + w - 12, y + 20),
                     (x + w - 3, y + 28 - sway), 3)
    for fx, fy in ((x, y + 30 + sway), (x + w, y + 30 - sway)):
        pygame.draw.line(screen, arm_light, (fx, fy), (fx - 3, fy + 4), 2)
        pygame.draw.line(screen, arm_light, (fx, fy), (fx + 2, fy + 4), 2)

    # legs and feet
    pygame.draw.line(screen, arm_dark, (cx - 5, y + h - 10),
                     (cx - 9, y + h + 2 + sway), 6)
    pygame.draw.line(screen, arm_dark, (cx + 5, y + h - 10),
                     (cx + 10, y + h + 2 - sway), 6)
    pygame.draw.ellipse(screen, arm_light, (cx - 15, y + h - 1 + sway, 12, 5))
    pygame.draw.ellipse(screen, arm_light, (cx + 4, y + h - 1 - sway, 12, 5))

    # torso, shaded from dark edge to lit center
    pygame.draw.ellipse(screen, (18, 53, 40), (x + 8, y + 18, w - 16, h - 5))
    pygame.draw.ellipse(screen, (48, 105, 65), (x + 10, y + 18, w - 19, h - 8))
    pygame.draw.ellipse(screen, (90, 145, 86), (x + 14, y + 19, w - 27, h - 13))
    pygame.draw.ellipse(screen, (128, 177, 104), (cx - 5, y + 22, 9, h - 18))
    pygame.draw.rect(screen, (45, 95, 61), (cx - 5, y + 13, 10, 11))

    # large alien skull, with rim shading and a bright forehead
    pygame.draw.ellipse(screen, (19, 53, 42), (x + 2, y - 1, w - 4, int(h * .76)))
    pygame.draw.ellipse(screen, (50, 105, 64), (x + 5, y + 1, w - 10, int(h * .70)))
    pygame.draw.ellipse(screen, (100, 157, 91), (x + 8, y + 2, w - 16, int(h * .60)))
    pygame.draw.ellipse(screen, (142, 187, 111), (x + 12, y + 4, w - 24, 12))
    pygame.draw.arc(screen, (190, 215, 145), (x + 9, y + 1, w - 18, 16),
                    math.pi, 2 * math.pi, 2)

    # eye sockets and wet, reflective black eyes
    eye_y = y + 17
    pygame.draw.ellipse(screen, (26, 55, 46), (x + 6, eye_y - 5, 15, 20))
    pygame.draw.ellipse(screen, (26, 55, 46), (x + w - 21, eye_y - 5, 15, 20))
    pygame.draw.ellipse(screen, (3, 9, 17), (x + 8, eye_y - 4, 12, 17))
    pygame.draw.ellipse(screen, (3, 9, 17), (x + w - 20, eye_y - 4, 12, 17))
    pygame.draw.ellipse(screen, (120, 190, 204), (x + 10, eye_y - 1, 4, 6))
    pygame.draw.ellipse(screen, (120, 190, 204), (x + w - 18, eye_y - 1, 4, 6))
    pygame.draw.circle(screen, WHITE, (x + 12, eye_y - 1), 2)
    pygame.draw.circle(screen, WHITE, (x + w - 16, eye_y - 1), 2)

    # nostrils, mouth, cheek plates and bioluminescent spots
    pygame.draw.polygon(screen, (39, 86, 54), [
        (cx - 3, y + 22), (cx, y + 27), (cx + 3, y + 22)
    ])
    pygame.draw.arc(screen, (13, 35, 27), (cx - 8, y + 25, 16, 8),
                    0, math.pi, 2)
    pygame.draw.arc(screen, (158, 190, 119), (x + 6, y + 18, 9, 10),
                    4.5, 5.9, 2)
    pygame.draw.arc(screen, (158, 190, 119), (x + w - 15, y + 18, 9, 10),
                    3.5, 5.1, 2)
    for dx, dy in ((9, 27), (w - 10, 26), (cx - 10, 32), (cx + 9, 31)):
        pygame.draw.circle(screen, (44, 105, 65), (x + dx, y + dy), 2)
        pygame.draw.circle(screen, (154, 207, 119), (x + dx, y + dy), 1)


def draw_boss():
    """Large cinematic alien commander with shaded skin, armor and glowing details."""
    x, y, w, h = boss
    # groundless shadow and massive shoulders
    pygame.draw.ellipse(screen, (12, 22, 27), (x - 12, y + 91, w + 24, 65))
    pygame.draw.ellipse(screen, (22, 49, 48), (x - 10, y + 68, w + 20, h - 37))
    pygame.draw.ellipse(screen, (43, 84, 67), (x + 2, y + 75, w - 4, h - 53))
    pygame.draw.ellipse(screen, (74, 117, 75), (x + 21, y + 79, w - 42, h - 64))
    # ribbed chest plates
    for i in range(4):
        yy = y + 96 + i * 8
        pygame.draw.arc(screen, (20, 51, 42), (x + 37, yy, w - 74, 13),
                        0, math.pi, 3)
        pygame.draw.arc(screen, (110, 151, 90), (x + 39, yy, w - 78, 10),
                        0, math.pi, 1)

    # skull with multiple shading layers
    pygame.draw.ellipse(screen, (13, 43, 37), (x + 13, y + 1, w - 26, 116))
    pygame.draw.ellipse(screen, (43, 91, 62), (x + 17, y + 2, w - 34, 108))
    pygame.draw.ellipse(screen, (83, 133, 78), (x + 23, y + 5, w - 46, 94))
    pygame.draw.ellipse(screen, (125, 164, 96), (x + 36, y + 8, w - 72, 37))
    pygame.draw.arc(screen, (183, 207, 133), (x + 31, y + 4, w - 62, 39),
                    math.pi, 2 * math.pi, 3)

    # brow ridge and large reflective eyes
    pygame.draw.arc(screen, (23, 54, 43), (x + 29, y + 26, 45, 30),
                    math.pi, 2 * math.pi, 7)
    pygame.draw.arc(screen, (23, 54, 43), (x + 75, y + 26, 45, 30),
                    math.pi, 2 * math.pi, 7)
    for ex in (x + 48, x + 99):
        pygame.draw.ellipse(screen, (22, 49, 43), (ex - 16, y + 35, 31, 41))
        pygame.draw.ellipse(screen, (2, 8, 17), (ex - 12, y + 38, 24, 34))
        pygame.draw.ellipse(screen, (76, 156, 171), (ex - 7, y + 43, 9, 12))
        pygame.draw.ellipse(screen, (225, 251, 255), (ex - 5, y + 43, 4, 5))
    # nose, mouth, teeth
    pygame.draw.polygon(screen, (35, 77, 52), [
        (x + 68, y + 65), (x + 76, y + 82), (x + 84, y + 65)
    ])
    pygame.draw.arc(screen, (8, 25, 23), (x + 51, y + 76, 49, 25),
                    0, math.pi, 4)
    pygame.draw.line(screen, (188, 202, 157), (x + 63, y + 88),
                     (x + 67, y + 93), 2)
    pygame.draw.line(screen, (188, 202, 157), (x + 77, y + 88),
                     (x + 81, y + 93), 2)

    # dark alien armor with luminous purple cores
    for ax in (x + 22, x + w - 22):
        pygame.draw.circle(screen, (27, 35, 57), (ax, y + 105), 17)
        pygame.draw.circle(screen, (91, 54, 143), (ax, y + 105), 12)
        pygame.draw.circle(screen, (188, 93, 255), (ax, y + 105), 6)
        pygame.draw.circle(screen, (235, 205, 255), (ax - 2, y + 102), 2)
    for i in range(5):
        px = x + 34 + i * 19
        py = y + 20 + (i % 2) * 5
        pygame.draw.circle(screen, (42, 82, 54), (px, py), 4)
        pygame.draw.circle(screen, (176, 215, 122), (px - 1, py - 1), 2)

    # Boss health bar
    pygame.draw.rect(screen, (45, 18, 28), (300, 75, 400, 22), border_radius=5)
    health_width = int(400 * max(0, boss_health) / BOSS_MAX_HEALTH)
    pygame.draw.rect(screen, RED, (300, 75, 400, 22), border_radius=5)
    pygame.draw.rect(screen, GREEN, (300, 75, health_width, 22), border_radius=5)
    pygame.draw.rect(screen, WHITE, (300, 75, 400, 22), 2, border_radius=5)
    draw_text("MARS ALIEN COMMANDER", small_font, WHITE, 390, 43)


def spawn_explosion(x, y, color=ORANGE, amount=18):
    """Create a burst of fading debris particles at a world position."""
    for _ in range(amount):
        angle = random.random() * math.tau
        speed = random.uniform(1.0, 5.0)
        particles.append({
            "x": float(x), "y": float(y),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(18, 38),
            "max_life": 38,
            "size": random.randint(2, 5),
            "color": color
        })


def draw_asteroid(rock):
    """Draw a rotating-looking, cratered space rock."""
    rect = rock["rect"]
    x, y, r = rect.centerx, rect.centery, rect.width // 2
    pygame.draw.circle(screen, (46, 48, 60), (x + 2, y + 3), r)
    pygame.draw.circle(screen, (104, 99, 94), (x, y), r)
    pygame.draw.arc(screen, (171, 158, 143), (x-r+3, y-r+3, 2*r-6, 2*r-6),
                    2.4, 5.5, 3)
    for dx, dy, rr in ((-r//3, -r//4, max(2, r//5)), (r//3, r//4, max(2, r//6)), (r//4, -r//3, max(2, r//8))):
        pygame.draw.circle(screen, (66, 65, 67), (x+dx, y+dy), rr)
        pygame.draw.arc(screen, (147, 137, 128), (x+dx-rr, y+dy-rr, rr*2, rr*2), 0.2, 2.6, 2)


def draw_effects():
    for particle in particles:
        ratio = max(0.15, particle["life"] / particle["max_life"])
        size = max(1, int(particle["size"] * ratio))
        pygame.draw.circle(screen, particle["color"],
                           (int(particle["x"]), int(particle["y"])), size)


def draw_powerups():

    for item in powerups:

        kind, rect = item["type"], item["rect"]

        color = {"HEALTH": GREEN, "RAPID": YELLOW, "SHIELD": CYAN}[kind]

        pygame.draw.circle(screen, color, rect.center, 16)

        pygame.draw.circle(screen, WHITE, rect.center, 16, 2)

        symbol = {"HEALTH": "+", "RAPID": "R", "SHIELD": "S"}[kind]

        image = font.render(symbol, True, BLACK)

        screen.blit(image, image.get_rect(center=rect.center))





def reset_game():

    global player, bullets, aliens, alien_bullets, powerups, particles, asteroids
    global asteroid_timer, screen_shake

    global score, lives, boss_health, boss_direction, boss

    global spawn_timer, boss_shot_timer, invincible_timer

    global rapid_timer, shield_timer, shoot_timer, powerup_timer
    global asteroid_timer, screen_shake

    global landing_progress, rocket_x, rocket_y, landing_message



    player = pygame.Rect(100, 280, 54, 38)

    bullets, aliens, alien_bullets, powerups = [], [], [], []
    particles, asteroids = [], []
    asteroid_timer = screen_shake = 0

    score, lives, boss_health = 0, 3, BOSS_MAX_HEALTH

    spawn_timer = boss_shot_timer = invincible_timer = 0

    rapid_timer = shield_timer = shoot_timer = powerup_timer = 0

    boss = pygame.Rect(790, 230, 145, 150)

    boss_direction = 1

    landing_progress = 0

    rocket_x, rocket_y = 120, 300

    landing_message = "APPROACHING MARS"





def take_damage():

    global lives, invincible_timer, screen_shake

    if invincible_timer == 0 and shield_timer == 0:

        lives -= 1
        invincible_timer = 90
        screen_shake = 10
        spawn_explosion(player.centerx, player.centery, RED, 12)





def spawn_powerup():

    kind = random.choice(["HEALTH", "RAPID", "SHIELD"])

    powerups.append({

        "type": kind,

        "rect": pygame.Rect(WIDTH, random.randint(70, HEIGHT - 50),

                            POWERUP_SIZE, POWERUP_SIZE)

    })





running = True

while running:

    clock.tick(60)



    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                running = False

            if state == MENU and event.key in (pygame.K_RETURN, pygame.K_SPACE):

                reset_game()

                state = PLAYING

            elif state in (GAME_OVER, WIN):

                if event.key == pygame.K_r:

                    reset_game()

                    state = PLAYING

                elif event.key == pygame.K_RETURN:

                    state = MENU



    keys = pygame.key.get_pressed()



    if state in (PLAYING, BOSS):

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:

            player.x -= PLAYER_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:

            player.x += PLAYER_SPEED

        if keys[pygame.K_UP] or keys[pygame.K_w]:

            player.y -= PLAYER_SPEED

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:

            player.y += PLAYER_SPEED

        player.clamp_ip(screen.get_rect())



        if invincible_timer > 0:

            invincible_timer -= 1

        if rapid_timer > 0:

            rapid_timer -= 1

        if shield_timer > 0:

            shield_timer -= 1

        # Update debris and exhaust particles with light drag and gravity.
        for particle in particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vx"] *= 0.97
            particle["vy"] = particle["vy"] * 0.97 + 0.025
            particle["life"] -= 1
            if particle["life"] <= 0:
                particles.remove(particle)

        # Asteroids become more frequent as the score rises.
        asteroid_timer += 1
        if asteroid_timer >= max(42, 115 - score // 10):
            asteroid_timer = 0
            size = random.randint(24, 43)
            asteroids.append({
                "rect": pygame.Rect(WIDTH + size, random.randint(65, HEIGHT - 65), size, size),
                "speed": random.uniform(2.5, 4.5) + min(2.0, score / 200)
            })
        for rock in asteroids[:]:
            rock["rect"].x -= int(rock["speed"])
            if rock["rect"].right < 0:
                asteroids.remove(rock)
            elif rock["rect"].colliderect(player):
                asteroids.remove(rock)
                spawn_explosion(rock["rect"].centerx, rock["rect"].centery, (170, 154, 136), 22)
                take_damage()

        shoot_timer += 1

        shoot_delay = 5 if rapid_timer > 0 else 13

        if keys[pygame.K_SPACE] and shoot_timer >= shoot_delay:

            bullets.append(pygame.Rect(player.right, player.centery - 3, 19, 6))

            shoot_timer = 0



        for bullet in bullets[:]:

            bullet.x += 12

            if bullet.left > WIDTH:

                bullets.remove(bullet)



        powerup_timer += 1

        if powerup_timer >= 600:

            powerup_timer = 0

            spawn_powerup()



        for item in powerups[:]:

            item["rect"].x -= 3

            if item["rect"].right < 0:

                powerups.remove(item)

            elif item["rect"].colliderect(player):

                kind = item["type"]

                if kind == "HEALTH":

                    lives = min(3, lives + 1)

                elif kind == "RAPID":

                    rapid_timer = 600

                elif kind == "SHIELD":

                    shield_timer = 300

                powerups.remove(item)



        if state == PLAYING:

            spawn_timer += 1

            if spawn_timer >= max(18, 55 - score // 20):

                spawn_timer = 0

                ah = random.randint(36, 43)

                aliens.append(pygame.Rect(WIDTH, random.randint(65, HEIGHT - 65),

                                          42, ah))



            for alien in aliens[:]:

                alien.x -= 3 + score // 100

                if alien.right < 0:

                    aliens.remove(alien)

                elif alien.colliderect(player):

                    aliens.remove(alien)

                    take_damage()



            for bullet in bullets[:]:

                hit_alien = next((a for a in aliens if bullet.colliderect(a)), None)

                if hit_alien is not None:

                    aliens.remove(hit_alien)

                    if bullet in bullets:

                        bullets.remove(bullet)

                    score += 10
                    spawn_explosion(hit_alien.centerx, hit_alien.centery, LIGHT_GREEN, 16)

            for bullet in bullets[:]:
                hit_rock = next((rock for rock in asteroids if bullet.colliderect(rock["rect"])), None)
                if hit_rock is not None:
                    asteroids.remove(hit_rock)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    spawn_explosion(hit_rock["rect"].centerx, hit_rock["rect"].centery, (170, 154, 136), 12)
                    score += 2

            if score >= 100:

                aliens.clear()

                alien_bullets.clear()

                state = BOSS



        elif state == BOSS:

            boss.y += 3 * boss_direction

            if boss.top <= 100:

                boss_direction = 1

            elif boss.bottom >= HEIGHT - 35:

                boss_direction = -1



            boss_shot_timer += 1

            if boss_shot_timer >= 72:

                boss_shot_timer = 0

                alien_bullets.append(pygame.Rect(

                    boss.left - 10, boss.centery - 4, 20, 9

                ))



            for shot in alien_bullets[:]:
                shot["rect"].x -= 7
                shot["rect"].y += int(shot["vy"])
                if shot["rect"].right < 0 or shot["rect"].bottom < 0 or shot["rect"].top > HEIGHT:
                    alien_bullets.remove(shot)
                elif shot["rect"].colliderect(player):
                    alien_bullets.remove(shot)
                    take_damage()



            for bullet in bullets[:]:
                if bullet.colliderect(boss):
                    bullets.remove(bullet)
                    boss_health -= 5
                    if random.random() < 0.35:
                        spawn_explosion(boss.left + random.randint(0, boss.width),
                                        boss.top + random.randint(0, boss.height), PURPLE, 5)



            if boss_health <= 0:

                boss_health = 0

                # Begin the landing sequence; victory is not shown yet.

                state = LANDING

                landing_progress = 0

                rocket_x, rocket_y = 120, 300

                landing_message = "BOSS DEFEATED - RETURNING TO MARS"



        if lives <= 0:

            state = GAME_OVER



    elif state == LANDING:

        # Rocket flies across the screen, then descends to the Martian surface.

        landing_progress += 1

        if landing_progress < 100:

            rocket_x = min(420, rocket_x + 3)

            rocket_y = 290 + int(math.sin(landing_progress / 8) * 18)

            landing_message = "RETURN FLIGHT: MARS IN SIGHT"

        elif landing_progress < 220:

            rocket_x = min(690, rocket_x + 2)

            rocket_y = min(410, rocket_y + 1)

            landing_message = "DESCENDING TO THE SURFACE"

        elif landing_progress < 285:

            rocket_x = min(755, rocket_x + 1)

            rocket_y = min(420, rocket_y + 0.25)

            landing_message = "LANDING LEGS DEPLOYED"

        else:

            rocket_x, rocket_y = 755, 420

            landing_message = "LANDING SUCCESSFUL"

            state = WIN



    # --------------------------- DRAW ---------------------------

    draw_background()



    if state == MENU:

        draw_text("ECLIPSE: SPACE JET ADVENTURE", big_font, CYAN,

                  WIDTH // 2, 180, center=True)

        draw_text("LEVEL 3 - MARS MISSION", font, ORANGE,

                  WIDTH // 2, 250, center=True)

        draw_text("Destroy 10 aliens, defeat the alien commander,",

                  small_font, WHITE, WIDTH // 2, 315, center=True)

        draw_text("then land your rocket safely on Mars!", small_font, WHITE,

                  WIDTH // 2, 340, center=True)

        draw_text("Press ENTER to Start", font, YELLOW,

                  WIDTH // 2, 405, center=True)

        draw_text("Move: WASD / Arrows   |   Hold SPACE to Shoot",

                  small_font, WHITE, WIDTH // 2, 450, center=True)

        draw_text("Collect + Health, R Rapid Fire, S Shield",

                  small_font, CYAN, WIDTH // 2, 480, center=True)



    elif state in (PLAYING, BOSS):

        if invincible_timer == 0 or invincible_timer // 6 % 2 == 0:

            draw_rocket(player, flame=True)

        for bullet in bullets:

            pygame.draw.rect(screen, GREEN, bullet, border_radius=3)

            pygame.draw.circle(screen, WHITE, (bullet.right, bullet.centery), 3)

        for alien in aliens:

            draw_real_alien(alien)

        for shot in alien_bullets:
            rect = shot["rect"]
            pygame.draw.ellipse(screen, (110, 15, 35), rect.inflate(8, 6))
            pygame.draw.ellipse(screen, RED, rect)
            pygame.draw.circle(screen, ORANGE, rect.center, 3)
        for rock in asteroids:
            draw_asteroid(rock["rect"] and rock)
        draw_effects()
        if shield_timer > 0:
            pulse = int(3 * math.sin(pygame.time.get_ticks() / 90))
            pygame.draw.ellipse(screen, (40, 210, 255), player.inflate(20 + pulse, 18 + pulse), 3)
            pygame.draw.ellipse(screen, (105, 235, 255), player.inflate(13, 11), 1)
        draw_powerups()

        draw_text(f"Score: {score}", font, WHITE, 20, 15)

        draw_text(f"Lives: {lives}", font, WHITE, 20, 50)

        if rapid_timer > 0:

            draw_text("RAPID FIRE!", small_font, YELLOW, 20, 125)

        if shield_timer > 0:

            draw_text("SHIELD ACTIVE!", small_font, CYAN, 20, 150)

        draw_text("ASTEROIDS: shoot or dodge", small_font, (200, 190, 175), 20, 175)
        if state == PLAYING:

            draw_text(f"MISSION PROGRESS: {min(10, score // 10)}/10", small_font, CYAN, 20, 95)
            draw_text("Destroy 10 aliens to summon the commander!",

                      small_font, WHITE, 20, 95)

        else:

            draw_boss()

            draw_text("Defeat the Mars alien commander!", small_font,
                      WHITE, 20, 95)
            if boss_health <= BOSS_MAX_HEALTH // 2:
                draw_text("WARNING: COMMANDER ENRAGED - SPREAD FIRE!", small_font, RED, 20, 122)



    elif state == LANDING:

        # Draw the rocket on the way down; the win screen waits until landing ends.

        draw_rocket(pygame.Rect(int(rocket_x), int(rocket_y), 48, 70),

                    flame=landing_progress < 220,

                    landed=landing_progress >= 220)

        draw_text("MARS LANDING SEQUENCE", big_font, CYAN,

                  WIDTH // 2, 45, center=True)

        draw_text(landing_message, font, WHITE, WIDTH // 2, 95, center=True)

        bar_w = min(500, int(500 * landing_progress / 285))

        pygame.draw.rect(screen, (50, 55, 65), (250, 125, 500, 14),

                         border_radius=7)

        pygame.draw.rect(screen, GREEN, (250, 125, bar_w, 14),

                         border_radius=7)

        pygame.draw.rect(screen, WHITE, (250, 125, 500, 14), 2,

                         border_radius=7)



    elif state == GAME_OVER:

        draw_text("MISSION FAILED", big_font, RED, WIDTH // 2, 220, center=True)

        draw_text(f"Final Score: {score}", font, WHITE,

                  WIDTH // 2, 290, center=True)

        draw_text("Press R to Retry or ENTER for Menu", small_font, WHITE,

                  WIDTH // 2, 360, center=True)



    elif state == WIN:

        # Show the same Level 1-style rocket upright after its Mars touchdown.
        # Its engine is off and its landing legs are deployed.
        landed_rocket = pygame.Rect(730, 350, 100, 140)
        draw_rocket(landed_rocket, flame=False, landed=True)
        pygame.draw.line(screen, (72, 82, 91), (754, 466), (741, 486), 4)
        pygame.draw.line(screen, (72, 82, 91), (806, 466), (819, 486), 4)
        pygame.draw.line(screen, (72, 82, 91), (735, 486), (749, 486), 4)
        pygame.draw.line(screen, (72, 82, 91), (812, 486), (826, 486), 4)

        draw_text("MISSION COMPLETE!", big_font, GREEN,

                  WIDTH // 2, 190, center=True)

        draw_text("THE ROCKET HAS LANDED ON MARS", font, CYAN,

                  WIDTH // 2, 260, center=True)

        draw_text(f"Final Score: {score}", font, WHITE,

                  WIDTH // 2, 320, center=True)

        draw_text("Press R to Play Again or ENTER for Menu", small_font,

                  WHITE, WIDTH // 2, 385, center=True)



    if screen_shake > 0 and state in (PLAYING, BOSS):
        screen_shake -= 1
    pygame.display.flip()



pygame.quit()