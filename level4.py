"""ECLIPSE — LEVEL 4: THE RED LAKE
Standalone final level only. The previous level's first key is carried in.
Requires pygame: pip install pygame
Run: python ECLIPSE_level4.py
"""
import math
import random
import math
import sys
import pygame

pygame.init()

# ==================================================
# SPACE JET ADVENTURE - SINGLE FILE GAME
# ==================================================
W, H = 1000, 650
WORLD_W, WORLD_H = 1800, 1400
FPS = 60

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("SPACE JET ADVENTURE")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22, bold=True)
SMALL = pygame.font.SysFont("arial", 15, bold=True)
BIG = pygame.font.SysFont("arial", 42, bold=True)

WHITE = (240, 248, 255)
CYAN = (45, 225, 255)
BLUE = (40, 115, 255)
ORANGE = (255, 135, 35)
RED = (255, 55, 75)
GREEN = (50, 245, 135)
YELLOW = (255, 220, 55)
PURPLE = (185, 65, 255)
DARK = (5, 9, 28)

STARS = [(random.randrange(W), random.randrange(H),
          random.choice([1, 1, 1, 2]))
         for _ in range(220)]


def label(msg, x, y, color=WHITE, font=FONT):
    img = font.render(str(msg), True, color)
    screen.blit(img, (int(x), int(y)))


def centered(msg, y, color=WHITE, font=BIG):
    img = font.render(msg, True, color)
    screen.blit(img, (W // 2 - img.get_width() // 2, y))


def health_bar(x, y, width, value, maximum=100):
    pygame.draw.rect(screen, (45, 50, 68), (x, y, width, 15), border_radius=6)
    ratio = max(0, min(1, value / maximum))
    color = GREEN if ratio > .5 else ORANGE if ratio > .25 else RED
    if ratio:
        pygame.draw.rect(screen, color,
                         (x, y, int(width * ratio), 15), border_radius=6)
    pygame.draw.rect(screen, CYAN, (x, y, width, 15), 1, border_radius=6)


def panel(x, y, width, height):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill((3, 12, 35, 220))
    screen.blit(surf, (x, y))
    pygame.draw.rect(screen, CYAN, (x, y, width, height), 1, border_radius=9)


# ---------------- SPACESHIP ----------------
def draw_ship(x, y, direction=(1, 0), scale=1, time=0):
    """Draw a detailed spaceship rotated toward its aim direction."""
    d = pygame.Vector2(direction)
    if d.length_squared() == 0:
        d = pygame.Vector2(1, 0)
    d = d.normalize()
    side = pygame.Vector2(-d.y, d.x)
    center = pygame.Vector2(x, y)

    def p(forward, sideways):
        q = center + d * forward * scale + side * sideways * scale
        return int(q.x), int(q.y)

    # Animated engine glow
    flame = 17 + int(7 * abs(math.sin(time * 12)))
    pygame.draw.polygon(screen, (255, 70, 25),
                        [p(-17, -8), p(-17-flame, 0), p(-17, 8)])
    pygame.draw.polygon(screen, CYAN,
                        [p(-17, -4), p(-17-flame*.75, 0), p(-17, 4)])

    # Large wings
    pygame.draw.polygon(screen, (45, 80, 150),
                        [p(2, 0), p(-23, -30), p(-15, -7)])
    pygame.draw.polygon(screen, (45, 80, 150),
                        [p(2, 0), p(-23, 30), p(-15, 7)])

    # Main fuselage
    pygame.draw.polygon(screen, (225, 235, 247),
                        [p(36, 0), p(12, -10), p(-22, -13),
                         p(-15, 0), p(-22, 13), p(12, 10)])
    pygame.draw.polygon(screen, ORANGE,
                        [p(8, -10), p(-10, -12), p(-17, -8), p(0, -5)])
    pygame.draw.polygon(screen, ORANGE,
                        [p(8, 10), p(-10, 12), p(-17, 8), p(0, 5)])

    # Cockpit and central stripe
    pygame.draw.polygon(screen, (20, 70, 115),
                        [p(23, 0), p(10, -5), p(0, -4), p(7, 0), p(0, 4), p(10, 5)])
    pygame.draw.line(screen, CYAN, p(10, 0), p(25, 0), max(1, int(2*scale)))

    # Wing lights
    for f, s in [(-12, -19), (-12, 19)]:
        pygame.draw.circle(screen, CYAN, p(f, s), max(2, int(3*scale)))


# ---------------- ASTRONAUT ----------------
def draw_astronaut(x, y, direction=(1, 0), time=0):
    d = pygame.Vector2(direction)
    if d.length_squared() == 0:
        d = pygame.Vector2(1, 0)
    d = d.normalize()
    side = pygame.Vector2(-d.y, d.x)
    c = pygame.Vector2(x, y)

    def p(f, s):
        q = c + d*f + side*s
        return int(q.x), int(q.y)

    # Shadow
    pygame.draw.ellipse(screen, (85, 35, 30), (x-17, y+16, 34, 9))

    # Boots and backpack
    pygame.draw.line(screen, (35, 55, 90), p(-9, -5), p(-17, -8), 7)
    pygame.draw.line(screen, (35, 55, 90), p(-9, 5), p(-17, 8), 7)
    pygame.draw.ellipse(screen, (60, 105, 145),
                        (x-15, y-8, 13, 24))

    # Suit
    pygame.draw.circle(screen, (215, 228, 242), (x, y+3), 12)
    pygame.draw.circle(screen, (255, 255, 255), (x, y+3), 12, 2)

    # Helmet and glass visor
    pygame.draw.circle(screen, (235, 245, 255), (x, y-9), 12)
    pygame.draw.circle(screen, (90, 205, 245), p(3, 0), 8)
    pygame.draw.arc(screen, WHITE, (x-10, y-19, 20, 20), .2, 2.7, 2)

    # Shoulder light
    pygame.draw.circle(screen, ORANGE, p(-2, 10), 3)

    # Aim arrow
    pygame.draw.polygon(screen, YELLOW,
                        [p(25, 0), p(13, -5), p(13, 5)])


# ---------------- ALIENS ----------------
def draw_alien(x, y, time=0, size=1):
    bob = math.sin(time * 5 + x * .02) * 3
    yy = int(y + bob)
    r = int(15 * size)

    # Legs
    for offset in (-8, 8):
        pygame.draw.line(screen, PURPLE, (x+offset, yy+8),
                         (x+offset*1.5, yy+18), max(2, int(4*size)))

    # Glowing body
    pygame.draw.ellipse(screen, (75, 30, 130),
                        (x-r-2, yy-r-2, 2*r+4, 2*r+4))
    pygame.draw.ellipse(screen, PURPLE,
                        (x-r, yy-r, 2*r, 2*r))
    pygame.draw.ellipse(screen, (220, 100, 255),
                        (x-r//2, yy-r, r, r//2))

    # Eyes
    for offset in (-5, 5):
        pygame.draw.ellipse(screen, RED,
                            (x+int(offset*size)-3, yy-4, 6, 8))
        pygame.draw.circle(screen, WHITE,
                           (x+int(offset*size), yy-2), 1)


# ---------------- TREASURE ----------------
def draw_treasure(x, y, time=0):
    glow = 25 + int(4 * math.sin(time * 5))
    pygame.draw.circle(screen, (255, 180, 30), (x, y), glow, 2)
    pygame.draw.rect(screen, (105, 55, 20), (x-19, y-2, 38, 23),
                     border_radius=4)
    pygame.draw.rect(screen, (255, 175, 25), (x-20, y-8, 40, 10),
                     border_radius=3)
    pygame.draw.rect(screen, YELLOW, (x-4, y-3, 8, 13))
    pygame.draw.circle(screen, WHITE, (x-8, y-5), 2)


# ---------------- EARTH ----------------
def draw_earth(x, y, radius):
    pygame.draw.circle(screen, (10, 35, 100), (x, y), radius+7)
    pygame.draw.circle(screen, (20, 95, 225), (x, y), radius)
    pygame.draw.circle(screen, CYAN, (x, y), radius, max(2, radius//35))

    # Simplified continents
    pygame.draw.ellipse(screen, (55, 190, 115),
                        (x-radius*.55, y-radius*.4,
                         radius*.65, radius*.45))
    pygame.draw.ellipse(screen, (55, 190, 115),
                        (x+radius*.05, y-radius*.05,
                         radius*.42, radius*.65))
    pygame.draw.ellipse(screen, (75, 205, 135),
                        (x-radius*.45, y+radius*.15,
                         radius*.25, radius*.25))


# ---------------- RESET ----------------
def reset_game():
    global player, ship_pos, treasure_pos, aim
    global aliens, bullets, astronaut_hp, ship_hp
    global treasure_found, phase, damage_cooldown
    global flight_aliens, flight_bullets, flight_aim
    global ship_y, wave, spawn_timer, flight_damage
    global flight_progress, landing_time, notice, notice_time

    ship_pos = pygame.Vector2(180, 700)
    player = pygame.Vector2(260, 700)
    treasure_pos = pygame.Vector2(1450, 300)
    aim = pygame.Vector2(1, 0)

    locations = [
        (450, 500), (650, 900), (950, 450),
        (1100, 1050), (1450, 800), (750, 250),
        (300, 300), (1550, 1150)
    ]

    aliens = [
        {"pos": pygame.Vector2(x, y),
         "hp": 2, "speed": random.randint(55, 80)}
        for x, y in locations
    ]

    bullets = []
    astronaut_hp = 100
    ship_hp = 100
    treasure_found = False
    phase = "mars"
    damage_cooldown = 0

    flight_aliens = []
    flight_bullets = []
    flight_aim = pygame.Vector2(1, 0)
    ship_y = H // 2
    wave = 0
    spawn_timer = 1
    flight_damage = 0
    flight_progress = 0
    landing_time = 0
    notice = ""
    notice_time = 0


# ---------------- MARS SCENE ----------------
def draw_mars(camera, time):
    screen.fill((110, 40, 34))

    # Layered Mars sky
    pygame.draw.rect(screen, (120, 47, 39), (0, 0, W, H))
    pygame.draw.circle(screen, (185, 85, 55), (800, 105), 58)
    pygame.draw.circle(screen, (220, 120, 70), (800, 105), 48)

    # Rocky surface decorations
    for i in range(150):
        wx = (i * 173) % WORLD_W
        wy = (i * 227) % WORLD_H
        sx, sy = int(wx-camera.x), int(wy-camera.y)

        if -30 < sx < W+30 and -30 < sy < H+30:
            r = 5 + i % 13
            pygame.draw.circle(screen, (140, 57, 43), (sx, sy), r)
            pygame.draw.circle(screen, (180, 75, 48),
                               (sx-r//3, sy-r//3), max(2, r//3))

    # Ship landing shadow and ship
    sx, sy = int(ship_pos.x-camera.x), int(ship_pos.y-camera.y)
    pygame.draw.ellipse(screen, (65, 30, 25), (sx-42, sy+23, 85, 13))
    draw_ship(sx, sy, (1, 0), .9, time)
    label("YOUR SHIP", sx-40, sy+37, CYAN, SMALL)

    # Treasure appears as the astronaut approaches
    distance = player.distance_to(treasure_pos)
    if not treasure_found and distance < 180:
        tx, ty = int(treasure_pos.x-camera.x), int(treasure_pos.y-camera.y)
        draw_treasure(tx, ty, time)
        label("HIDDEN TREASURE", tx-67, ty-43, YELLOW, SMALL)

    # Aliens and alien health
    for alien in aliens:
        ax = int(alien["pos"].x-camera.x)
        ay = int(alien["pos"].y-camera.y)
        if -50 < ax < W+50 and -50 < ay < H+50:
            draw_alien(ax, ay, time)
            health_bar(ax-16, ay-26, 32, alien["hp"], 2)

    # Player bullets
    for bullet in bullets:
        bx = int(bullet["pos"].x-camera.x)
        by = int(bullet["pos"].y-camera.y)
        pygame.draw.circle(screen, CYAN, (bx, by), 7)
        pygame.draw.circle(screen, WHITE, (bx, by), 3)

    px, py = int(player.x-camera.x), int(player.y-camera.y)
    draw_astronaut(px, py, aim, time)

    # Futuristic HUD
    panel(12, 12, 335, 91)
    label("SPACE JET ADVENTURE", 25, 19, YELLOW)
    label("ASTRONAUT HEALTH", 25, 52, WHITE, SMALL)
    health_bar(175, 53, 150, astronaut_hp)

    panel(W-300, 12, 286, 67)
    if treasure_found:
        label("TREASURE SECURED!", W-282, 24, GREEN, SMALL)
        label("RETURN TO YOUR SHIP", W-282, 47, YELLOW, SMALL)
    else:
        label("SEARCH FOR TREASURE", W-282, 23, CYAN, SMALL)
        signal = ("STRONG" if distance < 180 else
                  "MEDIUM" if distance < 400 else
                  "WEAK" if distance < 650 else "NO SIGNAL")
        label("SIGNAL: "+signal, W-282, 47, YELLOW, SMALL)

    panel(12, H-64, 380, 51)
    label("MOVE: WASD / ARROWS     SHOOT: SPACE", 23, H-55, WHITE, SMALL)
    label("ENTER SHIP: E", 23, H-33, CYAN, SMALL)


# ---------------- FLIGHT SCENE ----------------
def draw_flight(time):
    screen.fill((3, 7, 28))

    for i, (sx, sy, r) in enumerate(STARS):
        x = int((sx-time*(12+i%4)) % W)
        pygame.draw.circle(screen, WHITE, (x, sy), r)

    # Distant planets
    pygame.draw.circle(screen, (45, 45, 110), (640, 120), 36)
    pygame.draw.circle(screen, (90, 80, 165), (640, 120), 30)

    radius = min(55+int(flight_progress*1.4), 155)
    draw_earth(850, 315, radius)

    draw_ship(175, int(ship_y), flight_aim, 1, time)

    for alien in flight_aliens:
        draw_alien(int(alien["pos"].x), int(alien["pos"].y), time, 1.15)

    for bullet in flight_bullets:
        bx, by = int(bullet["pos"].x), int(bullet["pos"].y)
        pygame.draw.line(screen, CYAN, (bx-10, by), (bx+10, by), 4)
        pygame.draw.circle(screen, WHITE, (bx, by), 3)

    panel(12, 12, 315, 88)
    label("RETURN TO EARTH", 25, 19, YELLOW)
    label("SHIP HEALTH", 25, 52, WHITE, SMALL)
    health_bar(130, 53, 170, ship_hp)

    panel(W-200, 12, 188, 43)
    label("ALIEN WAVE: "+str(min(wave+1, 3))+"/3",
          W-187, 22, CYAN, SMALL)

    panel(12, H-65, 340, 51)
    label("W/S: DODGE     ARROWS: AIM", 23, H-55, WHITE, SMALL)
    label("SPACE: FIRE", 23, H-33, CYAN, SMALL)


# ---------------- MAIN ----------------
def main():
    global player, aim, bullets, aliens, astronaut_hp
    global treasure_found, phase, damage_cooldown
    global ship_hp, flight_aliens, flight_bullets
    global flight_aim, ship_y, wave, spawn_timer
    global flight_damage, flight_progress, landing_time
    global notice, notice_time

    reset_game()
    running = True
    elapsed = 0

    while running:
        dt = min(clock.tick(FPS)/1000, .04)
        elapsed += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_r and phase in ("won", "lost"):
                    reset_game()

                if event.key == pygame.K_SPACE:
                    if phase == "mars":
                        bullets.append({
                            "pos": player.copy()+aim*25,
                            "vel": aim*560,
                            "life": 1.4
                        })
                    elif phase == "flight":
                        flight_bullets.append({
                            "pos": pygame.Vector2(175, ship_y)+flight_aim*35,
                            "vel": flight_aim*700,
                            "life": 1.5
                        })

                if event.key == pygame.K_e and phase == "mars":
                    if player.distance_to(ship_pos) < 85:
                        if treasure_found:
                            phase = "flight"
                            flight_aliens.clear()
                            flight_bullets.clear()
                            flight_aim = pygame.Vector2(1, 0)
                            ship_y = H//2
                            wave = 0
                            spawn_timer = .5
                            flight_progress = 0
                        else:
                            notice = "Find the treasure before leaving!"
                            notice_time = 2

        keys = pygame.key.get_pressed()

        # ============== MARS EXPLORATION ==============
        if phase == "mars":
            movement = pygame.Vector2(0, 0)

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                movement.x -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                movement.x += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                movement.y -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                movement.y += 1

            if movement.length_squared():
                movement = movement.normalize()
                aim = movement.copy()
                player += movement*230*dt

            player.x = max(25, min(WORLD_W-25, player.x))
            player.y = max(25, min(WORLD_H-25, player.y))

            if not treasure_found and player.distance_to(treasure_pos) < 38:
                treasure_found = True
                notice = "TREASURE COLLECTED! RETURN TO YOUR SHIP!"
                notice_time = 3

            for alien in aliens[:]:
                delta = player-alien["pos"]
                distance = delta.length()

                if 1 < distance < 450:
                    alien["pos"] += delta.normalize()*alien["speed"]*dt

                if distance < 32 and damage_cooldown <= 0:
                    astronaut_hp -= 10
                    damage_cooldown = .65

                for bullet in bullets[:]:
                    if bullet["pos"].distance_to(alien["pos"]) < 25:
                        alien["hp"] -= 1
                        bullets.remove(bullet)
                        if alien["hp"] <= 0 and alien in aliens:
                            aliens.remove(alien)
                        break

            for bullet in bullets[:]:
                bullet["pos"] += bullet["vel"]*dt
                bullet["life"] -= dt
                if bullet["life"] <= 0:
                    bullets.remove(bullet)

            damage_cooldown = max(0, damage_cooldown-dt)

            camera = pygame.Vector2(
                max(0, min(WORLD_W-W, player.x-W/2)),
                max(0, min(WORLD_H-H, player.y-H/2))
            )

            draw_mars(camera, elapsed)

            if notice_time > 0:
                notice_time -= dt
                panel(W//2-255, 120, 510, 43)
                centered(notice, 130, YELLOW, SMALL)

            if astronaut_hp <= 0:
                phase = "lost"

        # ============== SPACE BATTLE ==============
        elif phase == "flight":
            if keys[pygame.K_w]:
                ship_y -= 240*dt
            if keys[pygame.K_s]:
                ship_y += 240*dt
            ship_y = max(55, min(H-55, ship_y))

            if keys[pygame.K_UP]:
                flight_aim = pygame.Vector2(0, -1)
            elif keys[pygame.K_DOWN]:
                flight_aim = pygame.Vector2(0, 1)
            elif keys[pygame.K_LEFT]:
                flight_aim = pygame.Vector2(-1, 0)
            elif keys[pygame.K_RIGHT]:
                flight_aim = pygame.Vector2(1, 0)

            spawn_timer -= dt
            if wave < 3 and spawn_timer <= 0:
                for _ in range(3):
                    flight_aliens.append({
                        "pos": pygame.Vector2(
                            W+random.randint(20, 150),
                            random.randint(65, H-65)),
                        "hp": 2,
                        "speed": random.randint(100, 150)
                    })
                wave += 1
                spawn_timer = 3

            for alien in flight_aliens[:]:
                target = pygame.Vector2(175, ship_y)
                delta = target-alien["pos"]

                if delta.length_squared() > 1:
                    alien["pos"] += delta.normalize()*alien["speed"]*dt

                if alien["pos"].distance_to(target) < 42:
                    if flight_damage <= 0:
                        ship_hp -= 10
                        flight_damage = .6
                    flight_aliens.remove(alien)
                    continue

                for bullet in flight_bullets[:]:
                    if bullet["pos"].distance_to(alien["pos"]) < 27:
                        alien["hp"] -= 1
                        flight_bullets.remove(bullet)
                        if alien["hp"] <= 0 and alien in flight_aliens:
                            flight_aliens.remove(alien)