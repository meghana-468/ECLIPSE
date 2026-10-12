"""
LEVEL 1 - EARTH TO MOON   (pygame version of the Panda3D level)
Requires:  pip install pygame        (pygame 2.0 or newer)
Run alone: python levels/level1_pygame.py
Same flow and features as the Panda3D level:
    menu (Start Game button) -> astronaut boards the ship -> countdown
    3, 2, 1, LAUNCH! -> takeoff -> flight (stars, Earth behind, Moon ahead,
    asteroids) -> approach to the Moon -> crash-landing on the Moon ->
    Level 1 ending screen with a hint about Level 2.

Controls
    Arrow keys / WASD ... fly            P or ESC ... pause / resume
    ENTER or SPACE ...... start / continue         R ... retry after a crash

Everything is drawn in code (a 2D version of the capsule ship and the
astronaut), so no image or sound files are needed.

How the main game uses this level
---------------------------------
    from levels.level1_pygame import Level1

    level = Level1(screen, on_complete=start_level_2, on_exit=back_to_menu)

    # inside your main loop:
    for event in pygame.event.get():
        level.handle_event(event)
    level.update(dt)            # dt in seconds
    level.draw(screen)          # then pygame.display.flip()

* `on_complete()` is called with no arguments when the player presses
  "CONTINUE TO LEVEL 2". After that `level.finished` is True and the level
  stops updating, so the main game can switch to Level 2.
* `on_exit()` (optional) is called if the player chooses QUIT in the pause
  or crash menu. Without it a pygame.QUIT event is posted.
* The level draws on an internal 1100x700 canvas and scales it to whatever
  surface you pass to draw(), keeping the aspect ratio.
"""
import math
import random
import sys

import pygame

W, H = 1100, 700            # internal canvas size
FPS = 60
GROUND_Y = 560              # ground / launch pad level (screen y)

LAUNCH_SHIP_X = 690         # ship position on the launch pad
LAUNCH_SCALE = 34.0         # pixels per ship-model unit on the pad
FLIGHT_SCALE = 11.0         # ... and during flight
LAND_X = 600                # ship position on the Moon

WHITE = (245, 248, 255)
CYAN = (70, 220, 255)
GOLD = (255, 211, 90)
RED = (255, 75, 80)
GREEN = (75, 235, 130)
HULL_COL = (92, 97, 117)
HULL_LIGHT = (140, 147, 170)
GLASS = (20, 36, 92)
METAL = (140, 146, 158)
TRIM = (240, 242, 248)


# ======================================================================
#  Small helpers
# ======================================================================
def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_col(c1, c2, t):
    t = clamp(t, 0.0, 1.0)
    return (int(lerp(c1[0], c2[0], t)), int(lerp(c1[1], c2[1], t)),
            int(lerp(c1[2], c2[2], t)))


def ease_in(u):
    u = clamp(u, 0.0, 1.0)
    return u * u


def ease_out(u):
    u = clamp(u, 0.0, 1.0)
    return 1.0 - (1.0 - u) * (1.0 - u)


def ease_io(u):
    u = clamp(u, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def ip(x, y):
    return (int(x), int(y))


def draw_text(surf, text, font, color, pos, anchor="center", shadow=True):
    img = font.render(text, True, color)
    rect = img.get_rect()
    setattr(rect, anchor, ip(pos[0], pos[1]))
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        surf.blit(sh, rect.move(2, 2))
    surf.blit(img, rect)
    return rect


def draw_text_scaled(surf, text, font, color, pos, scale):
    img = font.render(text, True, color)
    sh = font.render(text, True, (0, 0, 0))
    if abs(scale - 1.0) > 0.01:
        img = pygame.transform.rotozoom(img, 0, scale)
        sh = pygame.transform.rotozoom(sh, 0, scale)
    rect = img.get_rect(center=ip(pos[0], pos[1]))
    surf.blit(sh, rect.move(3, 3))
    surf.blit(img, rect)


class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label

    def hit(self, pos):
        return self.rect.collidepoint(int(pos[0]), int(pos[1]))

    def draw(self, surf, font, mouse):
        hover = self.hit(mouse)
        fill = (45, 110, 175) if hover else (22, 66, 118)
        pygame.draw.rect(surf, fill, self.rect, border_radius=10)
        pygame.draw.rect(surf, CYAN, self.rect, 2, border_radius=10)
        draw_text(surf, self.label, font, WHITE, self.rect.center)


class Particles:
    """Soft round puffs: smoke, dust, explosions."""

    def __init__(self):
        self.items = []

    def clear(self):
        self.items = []

    def add(self, x, y, vx, vy, r0, r1, life, color, a0=200):
        self.items.append({"x": x, "y": y, "vx": vx, "vy": vy, "r0": r0,
                           "r1": r1, "life": life, "t": 0.0,
                           "color": color, "a0": a0})

    def update(self, dt):
        keep = []
        for p in self.items:
            p["t"] += dt
            if p["t"] >= p["life"]:
                continue
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            keep.append(p)
        self.items = keep

    def draw(self, surf, layer):
        if not self.items:
            return
        layer.fill((0, 0, 0, 0))
        for p in self.items:
            k = p["t"] / p["life"]
            r = int(lerp(p["r0"], p["r1"], k))
            a = int(clamp(p["a0"] * (1.0 - k), 0, 255))
            c = p["color"]
            pygame.draw.circle(layer, (c[0], c[1], c[2], a),
                               ip(p["x"], p["y"]), max(1, r))
        surf.blit(layer, (0, 0))


def add_explosion(parts, x, y, r, big=False):
    count = 26 if big else 14
    for _ in range(count):
        ang = random.uniform(0, math.tau)
        sp = random.uniform(40, 260 if big else 190)
        col = random.choice(((255, 170, 60), (255, 120, 40),
                             (255, 225, 120), (230, 230, 230)))
        parts.add(x, y, math.cos(ang) * sp, math.sin(ang) * sp, r * 0.25,
                  r * (0.9 if big else 0.6), random.uniform(0.45, 0.95),
                  col, 230)


# ======================================================================
#  Artwork (all drawn with pygame primitives)
# ======================================================================
def draw_ship(surf, ox, oy, s, flame=0.0, hatch=1.0):
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

    # Dark cockpit window near the top.
    window = pygame.Rect(int(X(-0.31)), int(Y(6.35)),
                         max(3, int(0.62 * s)), max(3, int(1.05 * s)))
    pygame.draw.ellipse(surf, (25, 75, 135), window)
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
    limb((0, -46), -swing * 30, 19, 7, suit, dark)            # near arm


def make_asteroid(x, y, r, vy, vx):
    n = 11
    return {
        "x": x, "y": y, "r": r, "vy": vy, "vx": vx,
        "rot": random.uniform(0, math.tau), "spin": random.uniform(-1.5, 1.5),
        "verts": [(math.tau * i / n, random.uniform(0.72, 1.12)) for i in range(n)],
        "craters": [(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5),
                     random.uniform(0.12, 0.25)) for _ in range(3)],
        "shade": random.randint(95, 135),
    }


def draw_asteroid(surf, a):
    x, y, r, rot = a["x"], a["y"], a["r"], a["rot"]
    sh = a["shade"]
    pts = [ip(x + math.cos(ang + rot) * r * f, y + math.sin(ang + rot) * r * f)
           for ang, f in a["verts"]]
    pygame.draw.polygon(surf, (sh, sh - 10, sh - 22), pts)
    pygame.draw.polygon(surf, (sh + 55, sh + 40, sh + 25), pts, 2)
    cr, sr = math.cos(rot), math.sin(rot)
    for fx, fy, fr in a["craters"]:
        cx = x + (fx * cr - fy * sr) * r
        cy = y + (fx * sr + fy * cr) * r
        pygame.draw.circle(surf, (sh - 30, sh - 36, sh - 42), ip(cx, cy),
                           max(2, int(fr * r)))


def draw_moon(surf, cx, cy, r, features):
    if r < 1:
        return
    pygame.draw.circle(surf, (176, 178, 190), (cx, cy), r)
    for fx, fy, fr, dark in features:
        c = (cx + int(fx * r), cy + int(fy * r))
        rr = max(2, int(fr * r))
        pygame.draw.circle(surf, (128, 130, 144) if dark else (150, 152, 165), c, rr)
        pygame.draw.circle(surf, (196, 198, 210), c, rr, max(1, int(rr * 0.08)))
    pygame.draw.circle(surf, (225, 228, 238), (cx, cy), r, 3)


def make_moon_features():
    rnd = random.Random(11)
    feats = []
    while len(feats) < 18:
        fx, fy = rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8)
        fr = rnd.uniform(0.04, 0.2)
        if math.hypot(fx, fy) + fr < 0.95:
            feats.append((fx, fy, fr, rnd.random() < 0.5))
    return feats


def make_earth_texture(size=400):
    rnd = random.Random(7)
    tex = pygame.Surface((size, size), pygame.SRCALPHA)
    tex.fill((0, 0, 0, 0))
    pygame.draw.circle(tex, (22, 78, 190), (size // 2, size // 2), size // 2)
    for i in range(10):                                       # continents
        cx = rnd.randint(int(size * 0.12), int(size * 0.88))
        cy = rnd.randint(int(size * 0.15), int(size * 0.85))
        rr = rnd.randint(int(size * 0.06), int(size * 0.16))
        n = 9
        pts = []
        for j in range(n):
            ang = math.tau * j / n
            k = rnd.uniform(0.55, 1.25)
            pts.append((int(cx + math.cos(ang) * rr * k * 1.4),
                        int(cy + math.sin(ang) * rr * k)))
        pygame.draw.polygon(tex, (58, 150, 80) if i % 3 else (150, 130, 80), pts)
    for _ in range(14):                                       # clouds
        cx = rnd.randint(0, size)
        cy = rnd.randint(0, size)
        pygame.draw.ellipse(tex, (232, 238, 248),
                            (cx, cy, rnd.randint(30, 80), rnd.randint(8, 18)))
    pygame.draw.ellipse(tex, (240, 246, 255), (int(size * 0.25), -int(size * 0.08),
                                               int(size * 0.5), int(size * 0.2)))
    pygame.draw.ellipse(tex, (240, 246, 255), (int(size * 0.3), int(size * 0.92),
                                               int(size * 0.4), int(size * 0.14)))
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
    tex.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.circle(tex, (110, 170, 255), (size // 2, size // 2), size // 2, 5)
    return tex


def make_stars(n):
    return [(random.randrange(W), random.randrange(H), random.choice((1, 1, 1, 2)),
             random.uniform(0.2, 1.0), random.choice((0.3, 0.6, 1.0, 1.4)))
            for _ in range(n)]


# Boarding path: along the pad, up the ramp, into the doorway.
_DOOR_BOTTOM_Y = GROUND_Y - 4.3 * LAUNCH_SCALE
_HULL_EDGE_X = LAUNCH_SHIP_X - 2.62 * LAUNCH_SCALE
ASTRO_PATH = [(90.0, float(GROUND_Y)), (170.0, float(GROUND_Y)),
              (_HULL_EDGE_X, _DOOR_BOTTOM_Y),
              (_HULL_EDGE_X + 31.0, _DOOR_BOTTOM_Y)]
_SEG = [math.hypot(ASTRO_PATH[i + 1][0] - ASTRO_PATH[i][0],
                   ASTRO_PATH[i + 1][1] - ASTRO_PATH[i][1])
        for i in range(len(ASTRO_PATH) - 1)]
PATH_TOTAL = sum(_SEG)
WALK_SPEED = 120.0


def path_pos(dist):
    dist = clamp(dist, 0.0, PATH_TOTAL)
    for i, seg in enumerate(_SEG):
        if dist <= seg or i == len(_SEG) - 1:
            k = 0.0 if seg == 0 else clamp(dist / seg, 0.0, 1.0)
            a, b = ASTRO_PATH[i], ASTRO_PATH[i + 1]
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k))
        dist -= seg
    return ASTRO_PATH[-1]


def build_launch_bg():
    bg = pygame.Surface((W, H))
    for y in range(GROUND_Y):
        pygame.draw.line(bg, lerp_col((70, 140, 220), (170, 215, 250), y / GROUND_Y),
                         (0, y), (W, y))
    pygame.draw.circle(bg, (255, 244, 190), (940, 110), 62)
    pygame.draw.circle(bg, (255, 232, 130), (940, 110), 46)
    for cx, cy, sc in ((170, 120, 1.0), (430, 80, 0.8), (780, 200, 0.7)):
        for dx, dy, w, h in ((0, 0, 140, 44), (40, -18, 110, 44), (80, 4, 130, 38)):
            pygame.draw.ellipse(bg, (255, 255, 255),
                                (int(cx + dx * sc), int(cy + dy * sc),
                                 int(w * sc), int(h * sc)))
    for x, w, h, c in ((-80, 520, 120, (60, 135, 90)), (330, 640, 170, (52, 122, 80)),
                       (760, 560, 110, (66, 142, 92))):
        pygame.draw.ellipse(bg, c, (x, GROUND_Y - h, w, h * 2))
    pygame.draw.rect(bg, (62, 140, 70), (0, GROUND_Y, W, H - GROUND_Y))
    rnd = random.Random(3)
    for _ in range(14):                                       # trees
        tx = rnd.randint(20, W - 20)
        ty = GROUND_Y + rnd.randint(40, 130)
        pygame.draw.rect(bg, (100, 70, 40), (tx - 3, ty - 14, 6, 16))
        pygame.draw.polygon(bg, (30, 100, 55), [(tx - 18, ty - 10), (tx, ty - 56),
                                                (tx + 18, ty - 10)])
    pygame.draw.rect(bg, (110, 114, 128), (40, GROUND_Y, W - 80, 26))   # pad
    pygame.draw.line(bg, (160, 165, 180), (40, GROUND_Y), (W - 40, GROUND_Y), 3)
    pygame.draw.rect(bg, (205, 95, 65), (824, 250, 22, GROUND_Y - 250))   # tower
    for yy in range(262, GROUND_Y - 20, 40):
        pygame.draw.line(bg, (160, 70, 48), (824, yy), (846, yy + 40), 2)
        pygame.draw.line(bg, (160, 70, 48), (846, yy), (824, yy + 40), 2)
    pygame.draw.rect(bg, (205, 95, 65), (760, 325, 70, 10))             # arm
    # boarding ramp with posts and a rail
    x0, y0 = ASTRO_PATH[1]
    x1, y1 = ASTRO_PATH[2]
    pygame.draw.polygon(bg, (150, 152, 165),
                        [ip(x0, y0), ip(x1, y1), ip(x1, y1 + 8), ip(x0, y0 + 8)])
    slope = (y1 - y0) / (x1 - x0)
    for px in (260, 380, 500):
        py = y0 + (px - x0) * slope
        pygame.draw.rect(bg, (90, 92, 104), (px - 3, int(py) + 6, 6, GROUND_Y - int(py) - 6))
    pygame.draw.line(bg, (210, 214, 224), ip(x0, y0 - 30), ip(x1, y1 - 30), 3)
    for px in range(int(x0), int(x1), 72):
        py = y0 + (px - x0) * slope
        pygame.draw.line(bg, (210, 214, 224), ip(px, py), ip(px, py - 30), 2)
    return bg


def build_moon_bg(earth_small):
    bg = pygame.Surface((W, H))
    bg.fill((3, 4, 12))
    rnd = random.Random(5)
    for _ in range(170):
        sx, sy = rnd.randrange(W), rnd.randrange(GROUND_Y)
        v = rnd.randint(120, 255)
        pygame.draw.circle(bg, (v, v, min(255, v + 12)), (sx, sy), rnd.choice((1, 1, 2)))
    bg.blit(earth_small, (70, 40))
    for x in (40, 320, 640, 900):                              # distant hills
        h = rnd.randint(60, 110)
        pygame.draw.polygon(bg, (88, 88, 98), [(x, GROUND_Y), (x + 130, GROUND_Y - h),
                                               (x + 280, GROUND_Y)])
    pygame.draw.rect(bg, (138, 138, 146), (0, GROUND_Y, W, H - GROUND_Y))
    pygame.draw.line(bg, (176, 176, 188), (0, GROUND_Y), (W, GROUND_Y), 3)
    for _ in range(10):                                        # craters
        cw = rnd.randint(80, 200)
        ch = rnd.randint(14, 30)
        cx = rnd.randint(0, W - cw)
        cy = rnd.randint(GROUND_Y + 22, H - ch - 6)
        pygame.draw.ellipse(bg, (108, 108, 118), (cx, cy, cw, ch))
        pygame.draw.ellipse(bg, (160, 160, 170), (cx, cy, cw, ch), 2)
    for _ in range(16):                                        # rocks
        rx = rnd.randint(0, W)
        ry = rnd.randint(GROUND_Y + 8, H - 8)
        rs = rnd.randint(6, 16)
        pygame.draw.polygon(bg, (110, 110, 120), [(rx - rs, ry), (rx - rs // 2, ry - rs),
                                                  (rx + rs // 2, ry - rs + 2), (rx + rs, ry)])
    return bg


# ======================================================================
#  The level
# ======================================================================
class Level1:
    NAME = "LEVEL 1 - EARTH TO MOON"
    FLIGHT_SECONDS = 70.0       # length of the flight (0% -> 100%)
    ARRIVAL_SECONDS = 5.0       # Moon approach before the landing scene
    SHIP_SPEED = 520.0          # pixels per second (sideways / up / down)
    SHIP_RESPONSE = 10.0        # higher = snappier steering
    FALL_SPEED = 340.0          # base asteroid speed in pixels per second
    SHIP_RADIUS = 26.0
    TAKEOFF_SECONDS = 6.5
    LANDING_DESCENT = 8.0

    PAUSABLE = ("boarding", "countdown", "takeoff", "flight", "arrival", "landing")
    SCENE_OF = {"menu": "launch", "boarding": "launch", "countdown": "launch",
                "takeoff": "launch", "flight": "flight", "arrival": "flight",
                "crashed": "flight", "landing": "moon", "complete": "moon"}

    def __init__(self, screen, on_complete=None, on_exit=None):
        pygame.font.init()
        self.screen = screen
        self.on_complete = on_complete
        self.on_exit = on_exit

        self.f_small = pygame.font.SysFont("arial,helvetica,dejavusans", 17, bold=True)
        self.f_med = pygame.font.SysFont("arial,helvetica,dejavusans", 28, bold=True)
        self.f_btn = pygame.font.SysFont("arial,helvetica,dejavusans", 22, bold=True)
        self.f_big = pygame.font.SysFont("arial,helvetica,dejavusans", 56, bold=True)
        self.f_huge = pygame.font.SysFont("arial,helvetica,dejavusans", 130, bold=True)

        self.world = pygame.Surface((W, H))
        self.canvas = pygame.Surface((W, H))
        self.fx_layer = pygame.Surface((W, H), pygame.SRCALPHA)
        self.dim = pygame.Surface((W, H))
        self.dim.fill((0, 0, 0))
        self.flash_surf = pygame.Surface((W, H))
        self.flash_surf.fill((255, 40, 40))
        self.sky_dark = pygame.Surface((W, GROUND_Y))
        self.sky_dark.fill((2, 3, 12))

        earth_tex = make_earth_texture(400)
        self.earth_big = pygame.transform.smoothscale(earth_tex, (840, 840))
        self.earth_small = pygame.transform.smoothscale(earth_tex, (110, 110))
        self.moon_features = make_moon_features()
        self.launch_bg = build_launch_bg()
        self.moon_bg = build_moon_bg(self.earth_small)
        self.stars = make_stars(190)
        self.parts = Particles()

        self.start_btn = Button((W // 2 - 125, 178, 250, 56), "START GAME")
        self.pause_btn = Button((W - 126, 14, 108, 38), "PAUSE")
        self.resume_btn = Button((W // 2 - 140, 300, 280, 52), "RESUME")
        self.restart_btn = Button((W // 2 - 140, 366, 280, 52), "RESTART LEVEL")
        self.quit_btn = Button((W // 2 - 140, 432, 280, 52), "QUIT")
        self.retry_btn = Button((W // 2 - 140, 330, 280, 52), "TRY AGAIN")
        self.crash_quit_btn = Button((W // 2 - 140, 396, 280, 52), "QUIT")
        self.continue_btn = Button((W // 2 - 190, 370, 380, 56), "CONTINUE TO LEVEL 2")

        self.view = (0, 0, 1.0)
        self._update_view(screen.get_size())
        self.finished = False
        self.paused = False
        self.reset_level()

    # ------------------------------------------------------------ view
    def _update_view(self, size):
        tw, th = size
        sc = min(tw / float(W), th / float(H))
        self.view = ((tw - W * sc) / 2.0, (th - H * sc) / 2.0, sc)

    def _to_canvas(self, pos):
        ox, oy, sc = self.view
        return ((pos[0] - ox) / sc, (pos[1] - oy) / sc)

    # ------------------------------------------------------------ state
    def set_state(self, name):
        self.state = name
        self.t = 0.0

    def say(self, text, seconds=3.0):
        self.msg = text
        self.msg_timer = seconds

    def reset_level(self):
        """Back to the launch pad with the Start Game button."""
        self.paused = False
        self.finished = False
        self.set_state("menu")
        self.parts.clear()
        self.asteroids = []
        self.hull = 100
        self.progress = 0.0
        self.flight_time = 0.0
        self.scroll = 0.0
        self.invuln = 0.0
        self.shake = 0.0
        self.shake_off = (0, 0)
        self.flash = 0.0
        self.fade = 0.0
        self.msg = ""
        self.msg_timer = 0.0
        self.spawn_timer = 1.0
        self.ship_x, self.ship_y = W / 2.0, H * 0.72
        self.vel_x = self.vel_y = 0.0
        self.hatch = 0.0               # 0 = door open, 1 = closed
        self.rise = 0.0                # takeoff height in pixels
        self.space_mix = 0.0           # sky darkening during takeoff
        self.astro_x, self.astro_y = ASTRO_PATH[0]
        self.astro_phase = 0.0
        self.astro_face = 1
        self.astro_scale = 1.0
        self.astro_visible = True
        self.land_y = -300.0
        self.land_flame = 0.0
        self.touched_down = False

    def start_game(self):
        if self.state == "menu":
            self.set_state("boarding")

    def begin_flight(self, message):
        self.set_state("flight")
        self.fade = 0.0 
        self.parts.clear()
        self.asteroids = []
        self.hull = 100
        self.progress = 0.0
        self.flight_time = 0.0
        self.invuln = 0.0
        self.shake = 0.0
        self.flash = 0.0
        self.spawn_timer = 1.0
        self.ship_x, self.ship_y = W / 2.0, H * 0.72
        self.vel_x = self.vel_y = 0.0
        self.say(message, 5.0)

    def retry(self):
        if self.state == "crashed":
            self.begin_flight("Try again - watch out for the asteroids!")

    def begin_arrival(self):
        for a in self.asteroids:
            add_explosion(self.parts, a["x"], a["y"], a["r"] * 0.8)
        self.asteroids = []
        self.set_state("arrival")
        self.say("Approaching the Moon...", 6.0)

    def begin_landing(self):
        self.set_state("landing")
        self.parts.clear()
        self.hatch = 1.0
        self.land_y = -300.0
        self.land_flame = 1.0
        self.touched_down = False
        self.astro_visible = False
        self.astro_face = -1
        self.astro_scale = 1.0
        self.astro_phase = 0.0
        self.shake = 0.0
        self.msg_timer = 0.0

    def crash(self):
        self.set_state("crashed")
        add_explosion(self.parts, self.ship_x, self.ship_y, 60, big=True)
        self.shake = 14.0
        self.flash = 0.8
        self.msg_timer = 0.0

    def finish(self):
        if self.state != "complete" or self.finished:
            return
        self.finished = True
        if self.on_complete is not None:
            self.on_complete()

    def quit(self):
        self.finished = True
        if self.on_exit is not None:
            self.on_exit()
        else:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def toggle_pause(self):
        if self.paused:
            self.paused = False
        elif self.state in self.PAUSABLE:
            self.paused = True

    # ------------------------------------------------------------ input
    def handle_event(self, event):
        if self.finished:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.toggle_pause()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.paused:
                    return
                if self.state == "menu":
                    self.start_game()
                elif self.state == "complete":
                    self.finish()
            elif event.key == pygame.K_r and not self.paused:
                self.retry()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._click(self._to_canvas(event.pos))

    def _click(self, pos):
        if self.paused:
            if self.resume_btn.hit(pos):
                self.paused = False
            elif self.restart_btn.hit(pos):
                self.reset_level()
            elif self.quit_btn.hit(pos):
                self.quit()
            return
        st = self.state
        if st == "menu" and self.start_btn.hit(pos):
            self.start_game()
        elif st == "crashed":
            if self.retry_btn.hit(pos):
                self.retry()
            elif self.crash_quit_btn.hit(pos):
                self.quit()
        elif st == "complete" and self.continue_btn.hit(pos):
            self.finish()
        elif st in self.PAUSABLE and self.pause_btn.hit(pos):
            self.toggle_pause()

    # ------------------------------------------------------------ update
    def update(self, dt):
        if self.finished or self.paused:
            return
        dt = clamp(dt, 0.0, 0.05)
        self.t += dt
        st = self.state
        if st == "boarding":
            self._update_boarding()
        elif st == "countdown":
            if self.t >= 3.9:
                self.set_state("takeoff")
        elif st == "takeoff":
            self._update_takeoff(dt)
        elif st in ("flight", "arrival", "crashed"):
            self._update_flight(dt)
        elif st == "landing":
            self._update_landing(dt)
        self.parts.update(dt)
        self.shake = max(0.0, self.shake - dt * 14.0)
        s = self.shake
        self.shake_off = (random.uniform(-s, s), random.uniform(-s, s)) if s > 0.05 else (0, 0)
        self.flash = max(0.0, self.flash - dt * 1.8)
        if self.msg_timer > 0.0:
            self.msg_timer = max(0.0, self.msg_timer - dt)

    def _update_boarding(self):
        walk_t = PATH_TOTAL / WALK_SPEED
        dist = min(self.t * WALK_SPEED, PATH_TOTAL)
        self.astro_x, self.astro_y = path_pos(dist)
        self.astro_phase = dist / 11.0
        t_in = self.t - walk_t
        if t_in > 0.0:
            self.astro_scale = max(0.0, 1.0 - t_in / 0.5)
            self.astro_visible = self.astro_scale > 0.02
            self.astro_phase = 0.0
        t_close = t_in - 0.5
        if t_close > 0.0:
            self.hatch = ease_io(t_close / 0.9)
        if self.t >= walk_t + 0.5 + 0.9 + 0.4:
            self.hatch = 1.0
            self.set_state("countdown")

    def _update_takeoff(self, dt):
        self.rise = 1050.0 * ease_in(self.t / 6.0)
        self.space_mix = clamp((self.rise - 200.0) / 800.0, 0.0, 1.0)
        if self.rise < 300.0:
            for _ in range(3):
                self.parts.add(LAUNCH_SHIP_X + random.uniform(-30, 30), GROUND_Y - 8,
                               random.uniform(-170, 170), random.uniform(-40, 10),
                               12, 50, 1.6, (215, 215, 220), 150)
        self.shake = max(self.shake, 5.0 * (1.0 - clamp(self.rise / 400.0, 0.0, 1.0)))
        self.fade = clamp((self.t - 5.0) / 1.2, 0.0, 1.0)
        if self.t >= self.TAKEOFF_SECONDS:
            self.begin_flight("Fly with the arrow keys or WASD - dodge the asteroids!")

    def _update_flight(self, dt):
        st = self.state
        if st == "flight":
            speed = 1.0
            self.flight_time += dt
            self.progress = min(1.0, self.flight_time / self.FLIGHT_SECONDS)
        elif st == "arrival":
            speed = lerp(1.0, 0.25, ease_io(self.t / self.ARRIVAL_SECONDS))
        else:
            speed = 0.15
        self.scroll += 260.0 * speed * dt

        # --- steering (smooth)
        tx = ty = 0.0
        if st == "flight":
            keys = pygame.key.get_pressed()
            dx = ((1 if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) else 0)
                  - (1 if (keys[pygame.K_LEFT] or keys[pygame.K_a]) else 0))
            dy = ((1 if (keys[pygame.K_DOWN] or keys[pygame.K_s]) else 0)
                  - (1 if (keys[pygame.K_UP] or keys[pygame.K_w]) else 0))
            length = math.hypot(dx, dy)
            if length > 0:
                tx = dx / length * self.SHIP_SPEED
                ty = dy / length * self.SHIP_SPEED
        elif st == "arrival":
            tx = clamp((W / 2.0 - self.ship_x) * 3.0, -self.SHIP_SPEED, self.SHIP_SPEED)
            ty = clamp((H * 0.72 - self.ship_y) * 3.0, -self.SHIP_SPEED, self.SHIP_SPEED)
        k = min(1.0, dt * self.SHIP_RESPONSE)
        self.vel_x += (tx - self.vel_x) * k
        self.vel_y += (ty - self.vel_y) * k
        if st != "crashed":
            self.ship_x = clamp(self.ship_x + self.vel_x * dt, 60.0, W - 60.0)
            self.ship_y = clamp(self.ship_y + self.vel_y * dt, 230.0, H - 110.0)

        if st == "flight":
            self.invuln = max(0.0, self.invuln - dt)

        # --- asteroids: spawn, move toward the ship, collide
        if st == "flight" and self.progress < 0.96:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0.0:
                self.spawn_timer = max(0.35, 0.9 - 0.5 * self.progress) * random.uniform(0.8, 1.2)
                r = random.uniform(18, 52)
                if random.random() < 0.45:
                    x = clamp(self.ship_x + random.uniform(-120, 120), 30, W - 30)
                else:
                    x = random.uniform(30, W - 30)
                self.asteroids.append(make_asteroid(
                    x, -r, r, random.uniform(0, 140), random.uniform(-25, 25)))
        keep = []
        hit = None
        for a in self.asteroids:
            a["y"] += (self.FALL_SPEED * speed + a["vy"] * speed) * dt
            a["x"] += a["vx"] * dt
            a["rot"] += a["spin"] * dt
            if a["y"] > H + 90:
                continue
            if st == "flight" and self.invuln <= 0.0 and hit is None:
                d = math.hypot(a["x"] - self.ship_x, a["y"] - self.ship_y)
                if d < a["r"] * 0.85 + self.SHIP_RADIUS:
                    hit = a
                    continue
            keep.append(a)
        self.asteroids = keep
        if hit is not None:
            add_explosion(self.parts, hit["x"], hit["y"], hit["r"])
            self.hull -= 25
            self.invuln = 1.2
            self.shake = 10.0
            self.flash = 0.6
            if self.hull <= 0:
                self.hull = 0
                self.crash()
                return

        # --- state changes
        if st == "flight" and self.progress >= 1.0:
            self.begin_arrival()
        elif st == "arrival":
            self.fade = clamp((self.t - self.ARRIVAL_SECONDS) / 1.0, 0.0, 1.0)
            if self.t >= self.ARRIVAL_SECONDS + 1.0:
                self.begin_landing()

    def _update_landing(self, dt):
        """Descend to the Moon, crash-land, then show the Level 2 hint."""
        t = self.t
        self.fade = clamp(1.0 - t / 1.0, 0.0, 1.0)
        u = clamp(t / self.LANDING_DESCENT, 0.0, 1.0)
        self.land_y = -300.0 + (GROUND_Y + 300.0) * ease_out(u)

        if t < self.LANDING_DESCENT:
            self.land_flame = 1.1 - 0.5 * ease_in(u)
            near = clamp((self.land_y - (GROUND_Y - 260.0)) / 260.0, 0.0, 1.0)
            if random.random() < near * 3.0 * min(1.0, dt * 60.0):
                side = random.choice((-1, 1))
                self.parts.add(LAND_X + random.uniform(-40, 40), GROUND_Y - 6,
                               side * random.uniform(80, 220), random.uniform(-25, 5),
                               10, 40, 1.4, (170, 170, 178), 140)
        elif not self.touched_down:
            # Hard impact on the Moon: dust, sparks, and a screen shake.
            self.touched_down = True
            self.land_flame = 0.0
            self.shake = 14.0
            self.flash = 0.45
            add_explosion(self.parts, LAND_X, GROUND_Y - 35, 58, big=True)
            for i in range(30):
                side = -1 if i % 2 else 1
                self.parts.add(LAND_X + random.uniform(-30, 30), GROUND_Y - 6,
                               side * random.uniform(60, 280), random.uniform(-45, 4),
                               12, 52, 1.8, (175, 175, 183), 190)

        # Keep the hatch closed and the astronaut inside. No flag-planting step.
        self.hatch = 1.0
        self.astro_visible = False

        # Give the crash effect a moment, then show the Level 1 ending.
        if t >= self.LANDING_DESCENT + 3.0:
            self.set_state("complete")

    # ------------------------------------------------------------ drawing
    def draw(self, target=None):
        if target is None:
            target = self.screen
        self._update_view(target.get_size())
        scene = self.SCENE_OF[self.state]
        w = self.world
        if scene == "launch":
            self._draw_launch(w)
        elif scene == "flight":
            self._draw_flight(w)
        else:
            self._draw_moon(w)
        self.parts.draw(w, self.fx_layer)

        c = self.canvas
        c.fill((0, 0, 0))
        c.blit(w, (int(self.shake_off[0]), int(self.shake_off[1])))
        if self.flash > 0.0:
            self.flash_surf.set_alpha(int(clamp(self.flash * 110, 0, 255)))
            c.blit(self.flash_surf, (0, 0))
        mouse = self._to_canvas(pygame.mouse.get_pos())
        self._draw_ui(c, mouse)
        if self.fade > 0.0:
            self.dim.set_alpha(int(clamp(self.fade * 255, 0, 255)))
            c.blit(self.dim, (0, 0))

        ox, oy, sc = self.view
        if abs(sc - 1.0) < 1e-6 and target.get_size() == (W, H):
            target.blit(c, (0, 0))
        else:
            target.fill((0, 0, 0))
            scaled = pygame.transform.smoothscale(c, (max(1, int(W * sc)), max(1, int(H * sc))))
            target.blit(scaled, (int(ox), int(oy)))

    def _draw_stars(self, w, alpha_mul=1.0, limit_y=H):
        for x, y, size, bright, layer in self.stars:
            yy = (y + self.scroll * layer) % H
            if yy >= limit_y:
                continue
            shade = int(clamp((90 + 165 * bright) * alpha_mul, 0, 255))
            pygame.draw.circle(w, (shade, shade, min(255, shade + 15)), ip(x, yy), size)

    def _draw_launch(self, w):
        st = self.state
        w.blit(self.launch_bg, (0, 0))
        if self.space_mix > 0.0:                               # sky turns to space
            self.sky_dark.set_alpha(int(clamp(self.space_mix * 255, 0, 255)))
            w.blit(self.sky_dark, (0, 0))
            self._draw_stars(w, self.space_mix, GROUND_Y)
        ny = GROUND_Y - self.rise
        flame = 0.0
        if st == "takeoff":
            flame = random.uniform(0.9, 1.3)
        draw_ship(w, LAUNCH_SHIP_X, ny, LAUNCH_SCALE, flame, self.hatch)
        if self.astro_visible and st in ("menu", "boarding"):
            draw_astronaut(w, self.astro_x, self.astro_y, 0.68 * self.astro_scale,
                           self.astro_phase, self.astro_face)

    def _moon_geom(self):
        if self.state == "arrival":
            e = ease_io(self.t / self.ARRIVAL_SECONDS)
            r = lerp(1026.0, 1500.0, e)
            edge = lerp(430.0, 520.0, e)
        else:
            p = self.progress
            r = 26.0 + 1000.0 * p ** 3
            edge = lerp(150.0, 430.0, p * p)
        return r, edge - r

    def _draw_flight(self, w):
        w.fill((4, 6, 18))
        self._draw_stars(w)
        p = self.progress
        ecy = H + 245.0 + 900.0 * p
        if ecy - 420.0 < H:
            w.blit(self.earth_big, (int(W * 0.32 - 420), int(ecy - 420)))
        mr, mcy = self._moon_geom()
        draw_moon(w, W // 2, int(mcy), int(mr), self.moon_features)
        for i in range(16):                                    # speed streaks
            sx = (i * 71 + 30) % W
            sy = (i * 97 + self.scroll * 1.6) % H
            pygame.draw.line(w, (50, 70, 110), ip(sx, sy), ip(sx, sy + 16), 1)
        for a in self.asteroids:
            draw_asteroid(w, a)
        if self.state != "crashed":
            blink = self.invuln > 0.0 and int(self.invuln * 12) % 2 == 0
            if not blink:
                fs = FLIGHT_SCALE
                sw, sh = int(6.4 * fs), int(21 * fs)
                spr = pygame.Surface((sw, sh), pygame.SRCALPHA)
                draw_ship(spr, sw / 2.0, sh / 2.0 + 5.0 * fs, fs,
                          random.uniform(0.85, 1.25), 1.0)
                tilt = -self.vel_x / self.SHIP_SPEED * 14.0
                rot = pygame.transform.rotate(spr, tilt)
                w.blit(rot, rot.get_rect(center=ip(self.ship_x, self.ship_y)))

    def _draw_moon(self, w):
        w.blit(self.moon_bg, (0, 0))

        if self.touched_down:
            # Draw the capsule tilted on its side to show the crash landing.
            ship_surface = pygame.Surface((340, 390), pygame.SRCALPHA)
            draw_ship(ship_surface, 170, 330, LAUNCH_SCALE, 0.0, self.hatch)
            crashed_ship = pygame.transform.rotate(ship_surface, 68)
            w.blit(crashed_ship, crashed_ship.get_rect(
                center=ip(LAND_X, GROUND_Y - 38)))
        else:
            draw_ship(w, LAND_X, self.land_y, LAUNCH_SCALE,
                      self.land_flame * random.uniform(0.9, 1.2)
                      if self.land_flame > 0 else 0.0, self.hatch)

        # The astronaut stays inside; Level 1 ends after the impact.

    # ------------------------------------------------------------ interface
    def _draw_ui(self, c, mouse):
        st = self.state
        if st == "menu":
            panel = pygame.Surface((640, 215))
            panel.fill((6, 14, 36))
            panel.set_alpha(190)
            c.blit(panel, (W // 2 - 320, 30))
            draw_text(c, "MISSION: MOON", self.f_big, GOLD, (W // 2, 78))
            draw_text(c, "Level 1 - Earth to Moon", self.f_med, WHITE, (W // 2, 134))
            self.start_btn.draw(c, self.f_btn, mouse)
            draw_text(c, "ENTER = start   |   WASD / arrows = fly   |   P or ESC = pause",
                      self.f_small, WHITE, (W // 2, H - 22))
            return

        self._draw_hud(c, mouse)

        if st == "countdown":
            labels = ("3", "2", "1", "LAUNCH!")
            idx = min(3, int(self.t))
            pop = lerp(1.8, 1.0, ease_out((self.t - int(self.t)) / 0.45))
            font = self.f_huge if idx < 3 else self.f_big
            draw_text_scaled(c, labels[idx], font, GOLD, (W // 2, 200), pop)
        elif st == "boarding":
            draw_text(c, "Astronaut boarding...", self.f_med, GOLD, (W // 2, 120))

        if self.msg_timer > 0.0 and self.msg and st in ("flight", "arrival", "boarding"):
            draw_text(c, self.msg, self.f_med, GOLD, (W // 2, 150))

        if st == "crashed":
            self.dim.set_alpha(150)
            c.blit(self.dim, (0, 0))
            draw_text(c, "SPACESHIP CRASHED!", self.f_big, RED, (W // 2, 230))
            draw_text(c, "Asteroids tore through the hull.", self.f_btn, WHITE, (W // 2, 285))
            self.retry_btn.draw(c, self.f_btn, mouse)
            self.crash_quit_btn.draw(c, self.f_btn, mouse)
            draw_text(c, "Press R to try again", self.f_small, WHITE, (W // 2, 480))
        elif st == "complete":
            panel = pygame.Surface((820, 330))
            panel.fill((6, 14, 36))
            panel.set_alpha(215)
            c.blit(panel, (W // 2 - 410, 105))
            draw_text(c, "MISSION ENDED!", self.f_big, GOLD, (W // 2, 160))
            draw_text(c, "The spaceship crash-landed on the Moon.", self.f_med,
                      WHITE, (W // 2, 220))
            draw_text(c, "The rest of the mission will be explained in Level 2!",
                      self.f_btn, CYAN, (W // 2, 275))
            self.continue_btn.draw(c, self.f_btn, mouse)
            draw_text(c, "To be continued...", self.f_small, WHITE, (W // 2, 450))

        if self.paused:
            self.dim.set_alpha(170)
            c.blit(self.dim, (0, 0))
            draw_text(c, "PAUSED", self.f_big, GOLD, (W // 2, 230))
            self.resume_btn.draw(c, self.f_btn, mouse)
            self.restart_btn.draw(c, self.f_btn, mouse)
            self.quit_btn.draw(c, self.f_btn, mouse)

    def _draw_hud(self, c, mouse):
        draw_text(c, self.NAME, self.f_btn, WHITE, (W // 2, 24))
        bar = pygame.Rect(W // 2 - 190, 46, 380, 14)
        pygame.draw.rect(c, (30, 40, 65), bar, border_radius=7)
        fill = pygame.Rect(bar.left, bar.top, int(bar.width * clamp(self.progress, 0.0, 1.0)),
                           bar.height)
        if fill.width > 0:
            pygame.draw.rect(c, CYAN, fill, border_radius=7)
        pygame.draw.rect(c, (150, 170, 200), bar, 1, border_radius=7)
        draw_text(c, "EARTH", self.f_small, (120, 180, 255), (bar.left - 10, 53),
                  anchor="midright", shadow=False)
        draw_text(c, "MOON", self.f_small, (215, 215, 225), (bar.right + 10, 53),
                  anchor="midleft", shadow=False)
        draw_text(c, "JOURNEY %d%%" % int(self.progress * 100), self.f_small, WHITE,
                  (W // 2, 80))

        draw_text(c, "HULL", self.f_small, WHITE, (24, 24), anchor="midleft")
        hb = pygame.Rect(24, 40, 220, 16)
        pygame.draw.rect(c, (30, 40, 65), hb, border_radius=7)
        frac = clamp(self.hull / 100.0, 0.0, 1.0)
        col = GREEN if frac > 0.5 else GOLD if frac > 0.25 else RED
        if frac > 0:
            pygame.draw.rect(c, col, (hb.left, hb.top, int(hb.width * frac), hb.height),
                             border_radius=7)
        pygame.draw.rect(c, (150, 170, 200), hb, 1, border_radius=7)
        draw_text(c, "%d%%" % self.hull, self.f_small, WHITE, (hb.right + 10, 48),
                  anchor="midleft")

        if self.state in self.PAUSABLE:
            self.pause_btn.draw(c, self.f_small, mouse)

    # ------------------------------------------------------------ stand-alone
    def run(self):
        """Simple loop for running the level on its own."""
        clock = pygame.time.Clock()
        running = True
        while running and not self.finished:
            dt = clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_event(event)
            self.update(dt)
            self.draw()
            pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Level 1 - Earth to Moon")

    def level_done():
        print("Level 1 complete - the main game would start Level 2 now.")

    level = Level1(screen, on_complete=level_done)
    level.run()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
   
