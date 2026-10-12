import math
import random
import sys

import pygame

pygame.init()

# SPACE JET ADVENTURE - LEVEL 4: MARS TREASURE
# Controls: WASD / arrows = move | SPACE = shoot (auto-aims) | LEFT CLICK = shoot at cursor
#           P = pause | R = restart (after win / fail) | ESC = quit
WIDTH, HEIGHT = 1000, 650
FPS = 60
GROUND_TOP = 350
GROUND_BOTTOM = 585

COUNTDOWN_SECONDS = 100       # rescue ship leaves when this reaches 0
PLAYER_MAX_HEALTH = 100
FLIGHT_SECONDS = 10.0
SHOT_COOLDOWN_MS = 280
TREASURE_POINTS = 1000
KILL_POINTS = 150

DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Jet Adventure - Mars Treasure")
CLOCK = pygame.time.Clock()
FRAME = pygame.Surface((WIDTH, HEIGHT))   # the world is drawn here, then shaken onto DISPLAY
SURF = FRAME                              # current drawing target

FONT = pygame.font.SysFont("arial", 25, bold=True)
SMALL = pygame.font.SysFont("arial", 17)
BIG = pygame.font.SysFont("arial", 46, bold=True)

WHITE = (245, 248, 255)
CYAN = (65, 220, 255)
GOLD = (255, 205, 55)
RED = (245, 75, 65)
GREEN = (95, 235, 150)

random.seed()

stars = [
    (random.randrange(WIDTH), random.randrange(330), random.choice([1, 1, 2]))
    for _ in range(120)
]
space_stars = [
    (random.randrange(WIDTH), random.randrange(HEIGHT), random.choice([1, 1, 2, 3]))
    for _ in range(170)
]

# Distant Mars mountains
mountains = []
for x in range(-30, WIDTH + 100, 55):
    mountains.append((x, random.randint(245, 330), random.randint(50, 110)))

# Permanent surface rocks
rocks = []
for _ in range(45):
    rocks.append((random.randint(0, WIDTH),
                  random.randint(GROUND_TOP + 20, GROUND_BOTTOM),
                  random.randint(5, 17)))

# Pre-rendered sky gradient and horizon haze
SKY = pygame.Surface((WIDTH, GROUND_TOP + 20))
for _y in range(GROUND_TOP + 20):
    _t = min(1.0, _y / float(GROUND_TOP)) ** 1.7
    pygame.draw.line(SKY, (int(10 + 150 * _t), int(8 + 70 * _t), int(30 + 40 * _t)),
                     (0, _y), (WIDTH, _y))
HAZE = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
for _i in range(70):
    pygame.draw.line(HAZE, (225, 140, 105, int(120 * (1 - abs(_i - 35) / 35.0))),
                     (0, _i), (WIDTH, _i))


# ----------------------------------------------------------------------
#  Drawing helpers
# ----------------------------------------------------------------------
def text(message, font, color, x, y, center=False):
    image = font.render(message, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    SURF.blit(image, rect)


def depth_scale(y):
    """Perspective: things near the horizon are smaller, things near the camera bigger."""
    t = (y - GROUND_TOP) / float(GROUND_BOTTOM - GROUND_TOP)
    t = max(0.0, min(1.0, t))
    return 0.62 + 0.55 * t


def blit_sprite(fn, x, y, scale, size, anchor, args=(), flash=False):
    """Draw fn() onto a temporary surface, scale it for depth and blit it at (x, y)."""
    global SURF
    sprite = pygame.Surface(size, pygame.SRCALPHA)
    previous = SURF
    SURF = sprite
    fn(anchor[0], anchor[1], *args)
    SURF = previous
    if flash:
        sprite.fill((90, 90, 90, 0), special_flags=pygame.BLEND_RGB_ADD)
    w, h = max(1, int(size[0] * scale)), max(1, int(size[1] * scale))
    sprite = pygame.transform.smoothscale(sprite, (w, h))
    SURF.blit(sprite, (int(x - anchor[0] * scale), int(y - anchor[1] * scale)))


def shadow(x, y, s, width=26):
    pygame.draw.ellipse(SURF, (78, 36, 33),
                        (int(x - width * s), int(y - 5 * s), int(width * 2 * s), int(11 * s)))


def draw_background(now):
    SURF.blit(SKY, (0, 0))

    for sx, sy, size in stars:                       # twinkling stars
        b = 160 + int(90 * (0.5 + 0.5 * math.sin(now / 450 + sx)))
        pygame.draw.circle(SURF, (b, b, min(255, b + 10)), (sx, sy), size)

    pygame.draw.circle(SURF, (180, 66, 53), (800, 150), 78)      # distant planet
    pygame.draw.circle(SURF, (140, 48, 49), (822, 142), 67)
    pygame.draw.arc(SURF, (210, 102, 67), (745, 112, 80, 32), 0.3, 2.7, 4)

    pygame.draw.circle(SURF, (160, 135, 125), (620, 92), 19)     # small moon
    pygame.draw.circle(SURF, (125, 105, 103), (625, 88), 15)

    for x, peak_y, width in mountains:                           # mountains
        pygame.draw.polygon(SURF, (105, 43, 43),
                            [(x - width, GROUND_TOP + 12), (x, peak_y), (x + width, GROUND_TOP + 12)])
        pygame.draw.polygon(SURF, (135, 53, 43),
                            [(x, peak_y), (x + width, GROUND_TOP + 12), (x + width // 2, GROUND_TOP + 12)])

    pygame.draw.rect(SURF, (139, 56, 42), (0, GROUND_TOP, WIDTH, HEIGHT - GROUND_TOP))
    pygame.draw.rect(SURF, (112, 42, 36), (0, GROUND_TOP, WIDTH, 14))

    # Perspective floor: lines converge on the horizon, rows get wider toward the camera
    vx = WIDTH // 2
    for i in range(-6, 17):
        x_bottom = i * 100
        x_top = vx + (x_bottom - vx) * 0.12
        pygame.draw.line(SURF, (124, 49, 38), (x_top, GROUND_TOP + 14), (x_bottom, HEIGHT), 1)
    for k in range(1, 9):
        y = GROUND_TOP + 14 + int(((k / 8.0) ** 2) * (HEIGHT - GROUND_TOP - 14))
        pygame.draw.line(SURF, (154, 64 + k * 2, 43), (0, y), (WIDTH, y), 2)

    for x, y, size in rocks:                                     # rocks and craters
        s = depth_scale(y)
        w, h = int(size * 2 * s), max(2, int(size * s))
        pygame.draw.ellipse(SURF, (85, 39, 37), (x - w // 2, y - h // 2, w, h))
        pygame.draw.arc(SURF, (183, 77, 52), (x - w // 2, y - h // 2, w, h), 0.2, 2.8, 2)

    for i in range(22):                                          # blowing dust
        x = (i * 79 + int(now * 0.045)) % WIDTH
        y = GROUND_TOP + 35 + (i * 29) % 190
        pygame.draw.circle(SURF, (194, 101, 67), (x, y), 2)

    SURF.blit(HAZE, (0, GROUND_TOP - 35))


def draw_astronaut(x, y, now, moving=True, facing=1):
    """Detailed astronaut with smooth walking, running and visor animations."""
    x, y = int(x), int(y)
    t = now / 1000.0

    phase = t * (11 if moving else 0)
    leg_swing = math.sin(phase) * (11 if moving else 0)
    arm_swing = math.sin(phase + math.pi) * (7 if moving else 0)
    bounce = abs(math.sin(phase)) * 2 if moving else 0
    body_y = y + int(bounce)

    suit = (226, 235, 242)
    suit_shadow = (155, 178, 194)
    suit_highlight = (255, 255, 255)
    dark = (25, 42, 59)
    blue = (45, 155, 207)
    glow = (65, 225, 255)

    # Backpack with equipment
    pygame.draw.rect(SURF, (105, 132, 151), (x - facing * 17 - 5, body_y - 13, 15, 28), border_radius=5)
    pygame.draw.rect(SURF, dark, (x - facing * 17 - 2, body_y - 9, 9, 19), border_radius=3)
    pygame.draw.rect(SURF, blue, (x - facing * 17, body_y - 5, 7, 5), border_radius=2)
    pygame.draw.circle(SURF, glow, (x - facing * 17 + 3, body_y + 7), 2)
    pygame.draw.line(SURF, suit_shadow, (x - facing * 18, body_y - 12), (x - facing * 21, body_y - 20), 2)
    pygame.draw.circle(SURF, RED, (x - facing * 21, body_y - 21), 2)

    # Legs with animated knees and boots
    hip_y = body_y + 10
    for hip_x, swing in ((x - 5, leg_swing), (x + 5, -leg_swing)):
        hip = (hip_x, hip_y)
        knee = (int(hip_x + swing * 0.45), body_y + 22)
        foot = (int(hip_x + swing), body_y + 32 - int(abs(swing) * 0.15))
        pygame.draw.line(SURF, suit_shadow, hip, knee, 10)
        pygame.draw.line(SURF, suit, hip, knee, 7)
        pygame.draw.circle(SURF, blue, knee, 4)
        pygame.draw.line(SURF, suit_shadow, knee, foot, 9)
        pygame.draw.line(SURF, suit, knee, foot, 6)
        pygame.draw.ellipse(SURF, dark, (foot[0] - 7, foot[1] - 2, 15, 9))
        pygame.draw.line(SURF, (125, 165, 185), (foot[0] - 5, foot[1] + 5), (foot[0] + 6, foot[1] + 5), 2)

    # Torso armor and chest panel
    pygame.draw.ellipse(SURF, suit_shadow, (x - 14, body_y - 19, 28, 34))
    pygame.draw.ellipse(SURF, suit, (x - 11, body_y - 19, 23, 32))
    pygame.draw.rect(SURF, dark, (x - 7, body_y - 10, 14, 12), border_radius=3)
    pygame.draw.rect(SURF, blue, (x - 5, body_y - 8, 10, 5), border_radius=2)
    pygame.draw.circle(SURF, glow, (x, body_y + 1), 2)
    pygame.draw.line(SURF, suit_highlight, (x - 7, body_y - 15), (x + 5, body_y - 15), 2)

    # Animated arms
    for sx, sy, side, swing in ((x - 10, body_y - 12, -1, arm_swing),
                                (x + 10, body_y - 12, 1, -arm_swing)):
        elbow = (int(sx + side * 5 + swing * 0.4), int(sy + 8))
        hand = (int(sx + side * 8 + swing), int(body_y + 5 - abs(swing) * 0.15))
        pygame.draw.line(SURF, suit_shadow, (sx, sy), elbow, 9)
        pygame.draw.line(SURF, suit, (sx, sy), elbow, 6)
        pygame.draw.circle(SURF, blue, elbow, 4)
        pygame.draw.line(SURF, suit_shadow, elbow, hand, 8)
        pygame.draw.line(SURF, suit, elbow, hand, 5)
        pygame.draw.circle(SURF, dark, hand, 5)
        pygame.draw.circle(SURF, suit, hand, 3)

    # Laser blaster
    gx = x + facing * 10
    gun_x = gx if facing > 0 else gx - 18
    pygame.draw.rect(SURF, (60, 70, 85), (gun_x, body_y - 4, 18, 7), border_radius=2)
    pygame.draw.circle(SURF, CYAN, (gx + (18 if facing > 0 else -18), body_y - 1), 3)

    # Helmet and reflective visor
    helmet_y = body_y - 29
    pygame.draw.circle(SURF, suit_shadow, (x, helmet_y), 16)
    pygame.draw.circle(SURF, suit_highlight, (x - 1, helmet_y - 1), 14)
    pygame.draw.ellipse(SURF, (14, 30, 48), (x - 11, helmet_y - 10, 22, 18))
    pygame.draw.arc(SURF, (66, 175, 221), (x - 10, helmet_y - 10, 20, 17), 0.2, 2.8, 2)
    shine_x = x + int(math.sin(t * 1.5) * 2)
    pygame.draw.line(SURF, (150, 230, 255), (shine_x - 5, helmet_y - 5), (shine_x, helmet_y - 8), 2)
    pygame.draw.circle(SURF, WHITE, (x + 6, helmet_y - 3), 1)
    pygame.draw.circle(SURF, blue, (x - 14, helmet_y), 4)
    pygame.draw.circle(SURF, suit_highlight, (x - 14, helmet_y), 2)
    pygame.draw.circle(SURF, blue, (x + 14, helmet_y), 4)

    if moving and math.sin(phase) > 0.85:                        # footstep dust
        pygame.draw.circle(SURF, (190, 104, 72), (x - int(12 * facing), body_y + 34),
                           random.randint(2, 4))


def draw_alien(x, y, now, kind="rusher", seed=0.0):
    """Alien with animated legs, arms and glowing eyes. Shooters are purple and carry a cannon."""
    x, y = int(x), int(y)
    swing = math.sin(now * 0.018 + seed) * 8
    if kind == "shooter":
        skin, dark_skin = (132, 84, 176), (76, 44, 110)
    else:
        skin, dark_skin = (69, 144, 65), (35, 87, 47)

    hip = (x, y + 9)
    foot1 = (x - 7 + swing, y + 29)
    foot2 = (x + 7 - swing, y + 29)
    pygame.draw.line(SURF, dark_skin, hip, foot1, 8)
    pygame.draw.line(SURF, dark_skin, hip, foot2, 8)
    pygame.draw.ellipse(SURF, skin, (foot1[0] - 5, foot1[1] - 3, 12, 7))
    pygame.draw.ellipse(SURF, skin, (foot2[0] - 5, foot2[1] - 3, 12, 7))

    pygame.draw.ellipse(SURF, skin, (x - 12, y - 17, 24, 31))
    pygame.draw.ellipse(SURF, dark_skin, (x - 10, y - 13, 20, 24))

    arm1 = (x - 16, y - 4 + swing * 0.35)
    arm2 = (x + 16, y - 4 - swing * 0.35)
    pygame.draw.line(SURF, skin, (x - 8, y - 10), arm1, 7)
    pygame.draw.line(SURF, skin, (x + 8, y - 10), arm2, 7)
    pygame.draw.circle(SURF, skin, arm1, 5)
    pygame.draw.circle(SURF, skin, arm2, 5)
    if kind == "shooter":
        pygame.draw.rect(SURF, (50, 40, 70), (x - 30, y - 10, 18, 8), border_radius=3)
        pygame.draw.circle(SURF, (210, 110, 255), (x - 31, y - 6), 4)

    pygame.draw.ellipse(SURF, skin, (x - 17, y - 40, 34, 29))
    pygame.draw.ellipse(SURF, (245, 54, 39), (x - 12, y - 30, 9, 6))
    pygame.draw.ellipse(SURF, (245, 54, 39), (x + 3, y - 30, 9, 6))
    pygame.draw.circle(SURF, (255, 185, 90), (x - 8, y - 27), 2)
    pygame.draw.circle(SURF, (255, 185, 90), (x + 7, y - 27), 2)


def draw_treasure(x, y, now):
    x, y = int(x), int(y)
    glow = int(5 + 3 * math.sin(now / 140))
    pygame.draw.circle(SURF, (116, 68, 20), (x, y), 34 + glow, 2)
    pygame.draw.circle(SURF, (255, 180, 35), (x, y), 25 + glow, 1)
    pygame.draw.rect(SURF, (135, 74, 25), (x - 22, y - 3, 44, 25), border_radius=4)
    pygame.draw.rect(SURF, (244, 160, 43), (x - 22, y - 15, 44, 18), border_radius=6)
    pygame.draw.rect(SURF, (255, 202, 69), (x - 4, y - 13, 8, 32))
    pygame.draw.rect(SURF, (255, 223, 115), (x - 4, y - 3, 8, 10))
    pygame.draw.circle(SURF, GOLD, (x, y + 3), 4)
    pygame.draw.circle(SURF, WHITE, (x - 10, y - 10), 3)


def draw_spaceship(x, y, now, boost=0):
    x, y = int(x), int(y)
    flame_length = 13 + int(5 * math.sin(now / 65)) + int(boost)
    pygame.draw.polygon(SURF, (255, 125, 40),
                        [(x - 20, y - 7), (x - 20 - flame_length, y), (x - 20, y + 7)])
    pygame.draw.polygon(SURF, (255, 224, 110),
                        [(x - 20, y - 4), (x - 17 - flame_length, y), (x - 20, y + 4)])
    pygame.draw.polygon(SURF, (100, 155, 200),
                        [(x - 15, y), (x - 3, y - 23), (x + 22, y - 10), (x + 28, y)])
    pygame.draw.polygon(SURF, (175, 217, 239),
                        [(x - 27, y), (x - 10, y - 12), (x + 27, y - 8), (x + 38, y),
                         (x + 24, y + 9), (x - 10, y + 12)])
    pygame.draw.polygon(SURF, (30, 83, 125),
                        [(x - 1, y - 7), (x + 19, y - 5), (x + 28, y), (x + 8, y + 2)])
    pygame.draw.circle(SURF, CYAN, (x + 18, y - 3), 3)


def draw_earth(cx, cy, r):
    cx, cy, r = int(cx), int(cy), int(r)
    pygame.draw.circle(SURF, (36, 96, 200), (cx, cy), r)
    for dx, dy, fr in ((-.3, -.25, .28), (.25, .1, .3), (-.05, .45, .18)):
        pygame.draw.circle(SURF, (60, 160, 80), (int(cx + dx * r), int(cy + dy * r)), max(1, int(fr * r)))
    for dx, dy, fr in ((-.1, -.4, .12), (.35, -.2, .1), (-.4, .2, .1)):
        pygame.draw.circle(SURF, (235, 242, 255), (int(cx + dx * r), int(cy + dy * r)), max(1, int(fr * r)))
    pygame.draw.circle(SURF, (90, 160, 255), (cx, cy), r + 5, 5)
    pygame.draw.circle(SURF, (60, 120, 230), (cx, cy), r + 11, 3)


# ----------------------------------------------------------------------
#  Game state
# ----------------------------------------------------------------------
def reset_game():
    now = pygame.time.get_ticks()
    return {
        "phase": "play",                 # play -> launch -> flight -> win   (or lose)
        "player": pygame.Vector2(130, 490),
        "facing": 1,
        "moving": False,
        "health": float(PLAYER_MAX_HEALTH),
        "invuln_until": 0,
        "treasure": pygame.Vector2(850, 490),
        "ship": pygame.Vector2(115, 480),
        "collected": False,
        "aliens": [new_alien("rusher", now, 570, 465),
                   new_alien("rusher", now, 690, 515),
                   new_alien("shooter", now, 760, 435)],
        "bullets": [],
        "alien_shots": [],
        "particles": [],
        "medkits": [],
        "countdown": float(COUNTDOWN_SECONDS),
        "kills": 0,
        "score": 0,
        "score_rows": [],
        "last_shot": 0,
        "last_spawn": now,
        "message": "Find the treasure, then get back to the ship before the countdown ends!",
        "message_until": now + 5000,
        "shake_until": 0,
        "flash_until": 0,
        "phase_start": now,
        "fail_reason": "",
        "paused": False,
    }


def new_alien(kind, now, x=None, y=None):
    return {
        "pos": pygame.Vector2(WIDTH + 30 if x is None else x,
                              random.randint(GROUND_TOP + 60, GROUND_BOTTOM - 10) if y is None else y),
        "kind": kind,
        "speed": random.randint(74, 100) if kind == "rusher" else random.randint(58, 72),
        "hp": 2,
        "last_shot": now + random.randint(0, 1500),
        "hurt_until": 0,
        "strafe": random.choice([-1, 1]),
        "seed": random.random() * 100,
    }


def say(game, message, now, ms=2500):
    game["message"] = message
    game["message_until"] = now + ms


def burst(game, x, y, h, color, n=8, speed=140, life=0.6, size=3):
    for _ in range(n):
        ang = random.uniform(0, 2 * math.pi)
        spd = random.uniform(0.3, 1.0) * speed
        game["particles"].append({
            "x": x, "y": y, "h": h,
            "vx": math.cos(ang) * spd, "vy": math.sin(ang) * spd * 0.35,
            "vh": random.uniform(20, 120),
            "life": life * random.uniform(0.7, 1.2), "max": life,
            "color": color, "size": size,
        })
    if len(game["particles"]) > 220:
        del game["particles"][:len(game["particles"]) - 220]


def clamp_player(p):
    p.x = max(35, min(WIDTH - 35, p.x))
    p.y = max(GROUND_TOP + 55, min(GROUND_BOTTOM - 8, p.y))


def end_mission(game, now, reason):
    game["phase"] = "lose"
    game["fail_reason"] = reason
    game["phase_start"] = now
    game["bullets"].clear()
    game["alien_shots"].clear()


def hurt_player(game, amount, now, source=None):
    if now < game["invuln_until"] or game["phase"] != "play":
        return
    p = game["player"]
    game["health"] = max(0.0, game["health"] - amount)
    game["invuln_until"] = now + 700
    game["flash_until"] = now + 220
    game["shake_until"] = now + 260
    burst(game, p.x, p.y, 25, RED, 10, 150, 0.5)
    if source is not None:
        away = p - source
        if away.length_squared() > 0:
            away = away.normalize() * 30
            p.x += away.x
            p.y += away.y
            clamp_player(p)
    if game["health"] <= 0:
        end_mission(game, now, "The aliens overwhelmed you.")
    else:
        say(game, "Alien hit! Health %d%%" % int(game["health"]), now, 1500)


def auto_aim(game):
    """Direction for SPACE: toward the nearest alien in front of the astronaut, else straight ahead."""
    p, facing = game["player"], game["facing"]
    best, best_d = None, 520.0
    for a in game["aliens"]:
        to = a["pos"] - p
        if to.x * facing > 0 and abs(to.y) < abs(to.x) * 0.7 + 30 and to.length() < best_d:
            best, best_d = to, to.length()
    if best is not None and best.length_squared() > 0:
        return best.normalize()
    return pygame.Vector2(facing, 0)


def try_shoot(game, now, aim=None):
    if game["phase"] != "play" or game["paused"] or now - game["last_shot"] < SHOT_COOLDOWN_MS:
        return
    p = game["player"]
    direction = aim if aim is not None else auto_aim(game)
    if direction.length_squared() == 0:
        direction = pygame.Vector2(game["facing"], 0)
    direction = direction.normalize()
    if direction.x != 0:
        game["facing"] = 1 if direction.x > 0 else -1
    game["last_shot"] = now
    start = pygame.Vector2(p.x + direction.x * 24, p.y + direction.y * 8)
    game["bullets"].append({"pos": start, "vel": direction * 620})
    burst(game, start.x, start.y, 24, (255, 215, 110), 3, 90, 0.2, 2)


# ----------------------------------------------------------------------
#  Update
# ----------------------------------------------------------------------
def update_play(game, dt, now, keys):
    p = game["player"]
    d = pygame.Vector2(0, 0)
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        d.x -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        d.x += 1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        d.y -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        d.y += 1
    game["moving"] = d.length_squared() > 0
    if game["moving"]:
        if d.x != 0:
            game["facing"] = 1 if d.x > 0 else -1
        d = d.normalize()
        speed = 230 * (0.85 if game["collected"] else 1.0)     # the treasure is heavy
        p.x += d.x * speed * dt
        p.y += d.y * speed * dt
    clamp_player(p)

    # Rescue countdown
    game["countdown"] -= dt
    if game["countdown"] <= 0:
        game["countdown"] = 0.0
        end_mission(game, now, "The rescue ship left without you.")
        return

    # More aliens keep arriving - faster once the treasure is taken
    interval = 4500 if game["collected"] else 7500
    limit = 6 if game["collected"] else 5
    if now - game["last_spawn"] > interval and len(game["aliens"]) < limit:
        game["aliens"].append(new_alien("shooter" if random.random() < 0.4 else "rusher", now))
        game["last_spawn"] = now

    update_aliens(game, dt, now)
    if game["phase"] != "play":
        return
    update_alien_shots(game, dt, now)
    if game["phase"] != "play":
        return
    update_bullets(game, dt, now)

    for kit in game["medkits"][:]:                              # health packs
        if now > kit["until"]:
            game["medkits"].remove(kit)
        elif p.distance_to(kit["pos"]) < 30:
            game["health"] = min(float(PLAYER_MAX_HEALTH), game["health"] + 25)
            game["medkits"].remove(kit)
            say(game, "Medkit! +25 health", now, 1500)
            burst(game, kit["pos"].x, kit["pos"].y, 20, GREEN, 10, 100, 0.6)

    if not game["collected"] and p.distance_to(game["treasure"]) < 38:
        game["collected"] = True
        say(game, "TREASURE SECURED! Run to the spaceship - more aliens are coming!", now, 4500)
        burst(game, game["treasure"].x, game["treasure"].y, 20, GOLD, 24, 180, 0.9)
        game["shake_until"] = now + 400

    if game["collected"] and p.distance_to(game["ship"]) < 52:
        begin_launch(game, now)


def update_aliens(game, dt, now):
    p = game["player"]
    aliens = game["aliens"]
    for a in aliens:
        pos = a["pos"]
        to = p - pos
        dist = to.length()
        direction = to.normalize() if dist > 1 else pygame.Vector2(0, 0)
        if a["kind"] == "rusher":
            proximity = max(0.0, 1.0 - dist / 350.0)             # speeds up when close
            speed = a["speed"] * (1.0 + proximity * 0.35)
            pos.x += direction.x * speed * dt
            pos.y += direction.y * speed * dt
        else:                                                    # shooter: keeps its distance
            if dist > 270:
                pos.x += direction.x * a["speed"] * dt
                pos.y += direction.y * a["speed"] * dt
            elif dist < 180:
                pos.x -= direction.x * a["speed"] * 0.8 * dt
                pos.y -= direction.y * a["speed"] * 0.8 * dt
            else:
                pos.x += -direction.y * a["strafe"] * a["speed"] * 0.5 * dt
                pos.y += direction.x * a["strafe"] * a["speed"] * 0.5 * dt
            if dist < 460 and now - a["last_shot"] > 2000:
                a["last_shot"] = now
                game["alien_shots"].append({"pos": pygame.Vector2(pos.x, pos.y),
                                            "vel": direction * 270, "life": 3.0})
        pos.x = max(20, min(WIDTH + 40, pos.x))
        pos.y = max(GROUND_TOP + 45, min(GROUND_BOTTOM - 5, pos.y))

        if a["kind"] == "rusher" and dist < 34:                  # melee hit
            hurt_player(game, 15, now, pos)
            if game["phase"] != "play":
                return

    for i in range(len(aliens)):                                 # keep aliens from stacking
        for j in range(i + 1, len(aliens)):
            sep = aliens[i]["pos"] - aliens[j]["pos"]
            if 0 < sep.length() < 30:
                push = sep.normalize() * 0.5
                aliens[i]["pos"].x += push.x
                aliens[i]["pos"].y += push.y
                aliens[j]["pos"].x -= push.x
                aliens[j]["pos"].y -= push.y


def update_alien_shots(game, dt, now):
    p = game["player"]
    for shot in game["alien_shots"][:]:
        shot["pos"].x += shot["vel"].x * dt
        shot["pos"].y += shot["vel"].y * dt
        shot["life"] -= dt
        pos = shot["pos"]
        if shot["life"] <= 0 or pos.x < -20 or pos.x > WIDTH + 20 or pos.y < GROUND_TOP or pos.y > HEIGHT:
            game["alien_shots"].remove(shot)
        elif pos.distance_to(p) < 22:
            game["alien_shots"].remove(shot)
            hurt_player(game, 10, now, pos)
            if game["phase"] != "play":
                return


def update_bullets(game, dt, now):
    for b in game["bullets"][:]:
        b["pos"].x += b["vel"].x * dt
        b["pos"].y += b["vel"].y * dt
        pos = b["pos"]
        if pos.x < -10 or pos.x > WIDTH + 10 or pos.y < GROUND_TOP - 20 or pos.y > HEIGHT:
            game["bullets"].remove(b)
            continue
        for a in game["aliens"]:
            if pos.distance_to(a["pos"]) < 28:
                game["bullets"].remove(b)
                a["hp"] -= 1
                a["hurt_until"] = now + 120
                burst(game, a["pos"].x, a["pos"].y, 25, (150, 255, 120), 6, 120, 0.4)
                if a["hp"] <= 0:
                    game["aliens"].remove(a)
                    game["kills"] += 1
                    burst(game, a["pos"].x, a["pos"].y, 20, (120, 255, 140), 18, 200, 0.8, 4)
                    if random.random() < 0.3:
                        game["medkits"].append({"pos": pygame.Vector2(a["pos"].x, a["pos"].y),
                                                "until": now + 12000})
                break


def update_particles(game, dt):
    for q in game["particles"][:]:
        q["x"] += q["vx"] * dt
        q["y"] += q["vy"] * dt
        q["h"] += q["vh"] * dt
        q["vh"] -= 300 * dt
        q["life"] -= dt
        if q["life"] <= 0 or q["h"] < 0 and q["vh"] < 0:
            game["particles"].remove(q)


def begin_launch(game, now):
    health_pct = int(game["health"])
    secs_left = int(game["countdown"])
    game["score_rows"] = [
        ("Mars treasure", TREASURE_POINTS),
        ("Aliens defeated x%d" % game["kills"], game["kills"] * KILL_POINTS),
        ("Rescue time bonus (%ds left)" % secs_left, secs_left * 10),
        ("Suit health bonus (%d%%)" % health_pct, health_pct * 5),
    ]
    game["score"] = sum(v for _, v in game["score_rows"])
    game["phase"] = "launch"
    game["phase_start"] = now
    game["aliens"].clear()
    game["bullets"].clear()
    game["alien_shots"].clear()
    game["medkits"].clear()
    game["shake_until"] = now + 2500


def update_launch(game, dt, now):
    t = (now - game["phase_start"]) / 1000.0
    ship = game["ship"]
    if t < 2.4:
        burst(game, ship.x - 20, ship.y + 10, 5, (200, 120, 85), 2, 160, 0.9, 5)
    if t > 2.9:
        game["phase"] = "flight"
        game["phase_start"] = now
        game["particles"].clear()


def update_flight(game, dt, now):
    if (now - game["phase_start"]) / 1000.0 >= FLIGHT_SECONDS:
        game["phase"] = "win"
        game["phase_start"] = now


def update(game, dt, now, keys):
    if game["paused"]:
        return
    phase = game["phase"]
    if phase == "play":
        update_play(game, dt, now, keys)
    elif phase == "launch":
        update_launch(game, dt, now)
    elif phase == "flight":
        update_flight(game, dt, now)
    update_particles(game, dt)


# ----------------------------------------------------------------------
#  Rendering
# ----------------------------------------------------------------------
def draw_world(game, now):
    draw_background(now)
    phase = game["phase"]
    sx, sy = game["ship"].x, game["ship"].y
    s_pad = depth_scale(sy)
    pygame.draw.ellipse(SURF, (82, 42, 36), (sx - 60 * s_pad, sy - 6 * s_pad, 120 * s_pad, 26 * s_pad))

    items = []
    if phase != "launch":
        items.append((sy, lambda: draw_ship_entity(game, sx, sy, now, 0)))
    else:
        t = (now - game["phase_start"]) / 1000.0
        rise = 0.5 * 170 * t * t
        items.append((9999, lambda: draw_ship_entity(game, sx, sy - rise, now, min(45, 15 + t * 25),
                                                     ground_y=sy)))
    if not game["collected"] and phase in ("play", "lose"):
        tr = game["treasure"]
        items.append((tr.y, lambda tr=tr: draw_treasure_entity(tr, now)))
    for kit in game["medkits"]:
        items.append((kit["pos"].y, lambda kit=kit: draw_medkit(kit, now)))
    for a in game["aliens"]:
        items.append((a["pos"].y, lambda a=a: draw_alien_entity(game, a, now)))
    if phase in ("play", "lose"):
        items.append((game["player"].y, lambda: draw_player_entity(game, now)))
    for b in game["bullets"]:
        items.append((b["pos"].y, lambda b=b: draw_bullet(b)))
    for shot in game["alien_shots"]:
        items.append((shot["pos"].y, lambda shot=shot: draw_alien_shot(shot, now)))
    items.sort(key=lambda it: it[0])
    for _, fn in items:
        fn()

    for q in game["particles"]:
        s = depth_scale(q["y"])
        r = max(1, int(q["size"] * s * (q["life"] / q["max"] + 0.3)))
        pygame.draw.circle(SURF, q["color"], (int(q["x"]), int(q["y"] - q["h"] * s)), r)

    if phase == "play":
        target = game["ship"] if game["collected"] else game["treasure"]
        bob = int(6 * math.sin(now / 200))
        ty = int(target.y - 95 * depth_scale(target.y)) + bob
        pygame.draw.polygon(SURF, GOLD, [(target.x - 10, ty - 14), (target.x + 10, ty - 14), (target.x, ty)])
        if not game["collected"]:
            text("TREASURE", SMALL, GOLD, target.x, ty - 28, center=True)
        else:
            text("SHIP", SMALL, CYAN, target.x, ty - 28, center=True)


def draw_ship_entity(game, x, y, now, boost, ground_y=None):
    s = depth_scale(game["ship"].y)
    if ground_y is None:
        shadow(x, y + 12 * s, s, 38)
    blit_sprite(draw_spaceship, x, y - 12 * s, s * 1.15, (190, 80), (115, 40), (now, boost))


def draw_treasure_entity(tr, now):
    s = depth_scale(tr.y)
    shadow(tr.x, tr.y, s, 26)
    blit_sprite(draw_treasure, tr.x, tr.y - 20 * s, s, (110, 100), (55, 55), (now,))


def draw_medkit(kit, now):
    pos = kit["pos"]
    s = depth_scale(pos.y)
    if kit["until"] - now < 3000 and (now // 200) % 2:
        return
    shadow(pos.x, pos.y, s, 14)
    bob = int(3 * math.sin(now / 180))
    box = pygame.Rect(int(pos.x - 11 * s), int(pos.y - 24 * s) + bob, int(22 * s), int(18 * s))
    pygame.draw.rect(SURF, WHITE, box, border_radius=3)
    pygame.draw.rect(SURF, RED, (box.centerx - 2, box.y + 3, 4, max(4, box.h - 6)))
    pygame.draw.rect(SURF, RED, (box.x + 4, box.centery - 2, max(4, box.w - 8), 4))


def draw_alien_entity(game, a, now):
    pos = a["pos"]
    s = depth_scale(pos.y)
    shadow(pos.x, pos.y, s, 22)
    blit_sprite(draw_alien, pos.x, pos.y - 31 * s, s * 1.05, (100, 110), (50, 70),
                (now, a["kind"], a["seed"]), flash=now < a["hurt_until"])


def draw_player_entity(game, now):
    p = game["player"]
    s = depth_scale(p.y)
    shadow(p.x, p.y, s, 24)
    if now < game["invuln_until"] and (now // 80) % 2 == 0 and game["phase"] == "play":
        return
    blit_sprite(draw_astronaut, p.x, p.y - 38 * s, s * 1.05, (120, 130), (60, 85),
                (now, game["moving"], game["facing"]))


def draw_bullet(b):
    pos = b["pos"]
    s = depth_scale(pos.y)
    pygame.draw.ellipse(SURF, (70, 34, 30), (int(pos.x - 5 * s), int(pos.y - 2 * s), int(10 * s), max(2, int(4 * s))))
    c = (int(pos.x), int(pos.y - 24 * s))
    pygame.draw.circle(SURF, (255, 72, 48), c, max(2, int(6 * s)))
    pygame.draw.circle(SURF, (255, 215, 110), c, max(1, int(3 * s)))


def draw_alien_shot(shot, now):
    pos = shot["pos"]
    s = depth_scale(pos.y)
    pygame.draw.ellipse(SURF, (70, 34, 30), (int(pos.x - 6 * s), int(pos.y - 2 * s), int(12 * s), max(2, int(4 * s))))
    c = (int(pos.x), int(pos.y - 22 * s))
    r = max(3, int((8 + 2 * math.sin(now / 60)) * s))
    pygame.draw.circle(SURF, (150, 60, 220), c, r + 3)
    pygame.draw.circle(SURF, (215, 120, 255), c, r)
    pygame.draw.circle(SURF, WHITE, c, max(1, r // 3))


def draw_flight(game, now, final=False):
    elapsed = FLIGHT_SECONDS if final else (now - game["phase_start"]) / 1000.0
    p = max(0.0, min(1.0, elapsed / FLIGHT_SECONDS))
    SURF.fill((3, 5, 18))
    for sx, sy, layer in space_stars:
        x = (sx - elapsed * 60 * layer * (1.2 - 0.9 * p)) % WIDTH
        pygame.draw.circle(SURF, (150 + layer * 35,) * 3, (int(x), sy), 1 if layer < 3 else 2)

    draw_earth_p = max(0.0, (p - 0.1) / 0.9)
    pygame.draw.circle(SURF, (176, 92, 56),
                       (int(120 - 260 * p), int(520 + 170 * p)), int(230 * (1 - p) + 20))   # Mars shrinks
    draw_earth(WIDTH - 140, 300, 14 + 330 * draw_earth_p ** 2)                              # Earth grows

    ship_x = 320 + 170 * draw_earth_p
    ship_y = 330 + 10 * math.sin(elapsed * 2.2)
    blit_sprite(draw_spaceship, ship_x, ship_y, 1.6 - 0.7 * draw_earth_p, (190, 80), (115, 40), (now, 12))

    if p < 0.35:
        caption = "Engines roaring... leaving Mars behind."
    elif p < 0.7:
        caption = "Deep space. The alien treasure hums softly."
    elif not final:
        caption = "Earth! Home is in sight."
    else:
        caption = "Touchdown! Mission complete."
    text(caption, FONT, WHITE, WIDTH // 2, HEIGHT - 50, center=True)
    if not final and p > 0.9:
        glow = pygame.Surface((WIDTH, HEIGHT))
        glow.set_alpha(int(255 * (p - 0.9) / 0.1 * 0.6))
        glow.fill((255, 220, 170))
        SURF.blit(glow, (0, 0))


def panel(x, y, w, h, alpha=150):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((5, 8, 20, alpha))
    SURF.blit(s, (x, y))


def draw_hud(game, now):
    panel(12, 12, 290, 62)
    text("HEALTH", SMALL, WHITE, 24, 18)
    frac = max(0.0, game["health"]) / PLAYER_MAX_HEALTH
    bar_color = GREEN if frac > 0.6 else (GOLD if frac > 0.3 else RED)
    pygame.draw.rect(SURF, (30, 34, 48), (24, 42, 200, 18), border_radius=4)
    pygame.draw.rect(SURF, bar_color, (24, 42, int(200 * frac), 18), border_radius=4)
    pygame.draw.rect(SURF, WHITE, (24, 42, 200, 18), 2, border_radius=4)
    text("%d" % int(game["health"]), FONT, bar_color, 236, 36)

    secs = int(math.ceil(game["countdown"]))
    color = WHITE if secs > 40 else (GOLD if secs > 20 else RED)
    if secs <= 20 and (now // 300) % 2:
        color = WHITE
    panel(WIDTH // 2 - 150, 10, 300, 62)
    text("RESCUE SHIP DEPARTS IN", SMALL, CYAN, WIDTH // 2, 20, center=True)
    text("%02d:%02d" % divmod(secs, 60), BIG, color, WIDTH // 2, 48, center=True)

    panel(WIDTH - 232, 12, 220, 62)
    text("ALIENS DEFEATED", SMALL, WHITE, WIDTH - 220, 18)
    text(str(game["kills"]), FONT, GOLD, WIDTH - 220, 38)

    objective = "Bring the treasure back to your spaceship!" if game["collected"] else "Find the Mars treasure!"
    text(objective, FONT, GOLD if game["collected"] else WHITE, WIDTH // 2, HEIGHT - 52, center=True)
    text("WASD move   SPACE shoot   CLICK aim & shoot   P pause", SMALL, (215, 205, 215),
         WIDTH // 2, HEIGHT - 22, center=True)

    if now < game["message_until"]:
        panel(WIDTH // 2 - 340, 84, 680, 36, 130)
        text(game["message"], SMALL, WHITE, WIDTH // 2, 102, center=True)

    mx, my = pygame.mouse.get_pos()                                 # crosshair
    pygame.draw.circle(SURF, (255, 90, 70), (mx, my), 9, 2)
    pygame.draw.line(SURF, (255, 90, 70), (mx - 14, my), (mx - 5, my), 2)
    pygame.draw.line(SURF, (255, 90, 70), (mx + 5, my), (mx + 14, my), 2)
    pygame.draw.line(SURF, (255, 90, 70), (mx, my - 14), (mx, my - 5), 2)
    pygame.draw.line(SURF, (255, 90, 70), (mx, my + 5), (mx, my + 14), 2)


def dim(alpha):
    veil = pygame.Surface((WIDTH, HEIGHT))
    veil.set_alpha(alpha)
    veil.fill((0, 0, 0))
    SURF.blit(veil, (0, 0))


def render(game, now):
    global SURF
    SURF = FRAME
    phase = game["phase"]
    if phase in ("play", "lose", "launch"):
        draw_world(game, now)
        if phase == "launch":
            t = (now - game["phase_start"]) / 1000.0
            veil = pygame.Surface((WIDTH, HEIGHT))
            veil.set_alpha(max(0, min(255, int((t - 1.6) / 1.3 * 255))))
            veil.fill((3, 5, 18))
            SURF.blit(veil, (0, 0))
    elif phase == "flight":
        draw_flight(game, now)
    else:
        draw_flight(game, now, final=True)

    ox = oy = 0
    if now < game["shake_until"] or phase == "launch":
        ox, oy = random.randint(-5, 5), random.randint(-4, 4)
    DISPLAY.fill((0, 0, 0))
    DISPLAY.blit(FRAME, (ox, oy))
    SURF = DISPLAY

    if now < game["flash_until"] and phase == "play":
        flash = pygame.Surface((WIDTH, HEIGHT))
        flash.set_alpha(90)
        flash.fill((255, 20, 20))
        SURF.blit(flash, (0, 0))

    if phase == "play":
        draw_hud(game, now)
        if game["paused"]:
            dim(150)
            text("PAUSED", BIG, WHITE, WIDTH // 2, HEIGHT // 2 - 20, center=True)
            text("Press P to resume", FONT, CYAN, WIDTH // 2, HEIGHT // 2 + 30, center=True)
    elif phase == "lose":
        dim(170)
        text("MISSION FAILED", BIG, RED, WIDTH // 2, 230, center=True)
        text(game["fail_reason"], FONT, WHITE, WIDTH // 2, 290, center=True)
        text("Aliens defeated: %d" % game["kills"], SMALL, GOLD, WIDTH // 2, 335, center=True)
        text("Press R to try again   |   ESC to quit", FONT, CYAN, WIDTH // 2, 400, center=True)
    elif phase == "win":
        dim(150)
        panel(WIDTH // 2 - 280, 90, 560, 440, 190)
        text("MISSION COMPLETE", BIG, GOLD, WIDTH // 2, 135, center=True)
        text("The alien treasure is home on Earth!", SMALL, CYAN, WIDTH // 2, 175, center=True)
        y = 225
        for label, value in game["score_rows"]:
            text(label, FONT, WHITE, WIDTH // 2 - 240, y)
            text(str(value), FONT, WHITE, WIDTH // 2 + 240 - 70, y)
            y += 46
        text("FINAL SCORE", BIG, GOLD, WIDTH // 2 - 240, y + 20)
        text(str(game["score"]), BIG, GOLD, WIDTH // 2 + 240 - 110, y + 20)
        text("Press R to play again   |   ESC to quit", SMALL, CYAN, WIDTH // 2, 500, center=True)


def main():
    game = reset_game()
    running = True

    while running:
        dt = min(CLOCK.tick(FPS) / 1000.0, 0.035)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game["phase"] in ("win", "lose"):
                    game = reset_game()
                elif event.key == pygame.K_p and game["phase"] == "play":
                    game["paused"] = not game["paused"]
                elif event.key == pygame.K_SPACE:
                    try_shoot(game, now)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                aim = pygame.Vector2(mx, my) - game["player"]
                try_shoot(game, now, aim)

        keys = pygame.key.get_pressed()
        update(game, dt, now, keys)
        render(game, now)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
