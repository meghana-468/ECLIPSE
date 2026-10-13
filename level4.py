"""ECLIPSE — LEVEL 4: THE RED LAKE
Standalone final level only. The previous level's first key is carried in.
Requires pygame: pip install pygame
Run: python ECLIPSE_level4.py
"""
import math
import random
import sys
import pygame

pygame.init()

# ================= SETTINGS =================
WIDTH, HEIGHT = 1000, 650
WORLD_W, WORLD_H = 2200, 1800
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Jet Adventure")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 22)
SMALL = pygame.font.SysFont("consolas", 16)
BIG = pygame.font.SysFont("consolas", 42, bold=True)

WHITE = (245, 245, 255)
BLACK = (8, 10, 28)
ORANGE = (240, 115, 45)
RED = (245, 55, 65)
GREEN = (60, 230, 130)
YELLOW = (255, 220, 65)
PURPLE = (175, 85, 240)
CYAN = (90, 230, 255)
BLUE = (55, 135, 245)

# ================= WORLD DECORATION =================
random.seed(12)

rocks = [
    {
        "x": random.randint(30, WORLD_W - 30),
        "y": random.randint(30, WORLD_H - 30),
        "r": random.randint(5, 18),
        "shade": random.randint(90, 140)
    }
    for _ in range(180)
]

stars = [
    (random.randrange(WIDTH), random.randrange(HEIGHT))
    for _ in range(180)
]


# ================= DRAWING HELPERS =================
def draw_text(text, x, y, color=WHITE, font=FONT):
    image = font.render(str(text), True, color)
    screen.blit(image, (x, y))


def centered_text(text, y, color=WHITE, font=BIG):
    image = font.render(text, True, color)
    screen.blit(
        image,
        (WIDTH // 2 - image.get_width() // 2, y)
    )


def health_bar(x, y, width, height, value, maximum, color):
    pygame.draw.rect(screen, (55, 35, 40), (x, y, width, height))

    ratio = max(0, min(1, value / maximum))
    if ratio > 0:
        pygame.draw.rect(
            screen, color,
            (x, y, int(width * ratio), height)
        )

    pygame.draw.rect(screen, WHITE, (x, y, width, height), 1)


def to_screen(position, camera):
    return (
        int(position.x - camera.x),
        int(position.y - camera.y)
    )


# ================= ASTRONAUT =================
def draw_astronaut(x, y, direction):
    # Draw the astronaut facing UP first, then rotate the sprite.
    sprite = pygame.Surface((64, 64), pygame.SRCALPHA)

    # Backpack
    pygame.draw.rect(
        sprite, (70, 125, 165),
        (17, 24, 9, 24), border_radius=3
    )

    # Legs
    pygame.draw.line(
        sprite, WHITE, (27, 43), (23, 54), 6
    )
    pygame.draw.line(
        sprite, WHITE, (37, 43), (41, 54), 6
    )

    # Body
    pygame.draw.rect(
        sprite, (220, 230, 240),
        (21, 25, 22, 22), border_radius=5
    )

    # Helmet and visor
    pygame.draw.circle(sprite, WHITE, (32, 17), 13)
    pygame.draw.circle(sprite, (35, 100, 155), (34, 17), 8)

    # Suit light
    pygame.draw.circle(sprite, CYAN, (27, 34), 3)

    # Base sprite faces up.
    if direction.x > 0.5:
        angle = -90
    elif direction.x < -0.5:
        angle = 90
    elif direction.y > 0.5:
        angle = 180
    else:
        angle = 0

    rotated = pygame.transform.rotate(sprite, angle)
    rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rect)


# ================= SPACESHIP =================
def draw_spaceship(x, y, angle=0, scale=1.0):
    sprite = pygame.Surface((100, 120), pygame.SRCALPHA)

    # Ship faces UP by default.
    pygame.draw.polygon(
        sprite, (165, 190, 220),
        [(50, 8), (75, 64), (68, 91), (32, 91), (25, 64)]
    )

    pygame.draw.polygon(
        sprite, (85, 125, 180),
        [(31, 57), (7, 88), (33, 81)]
    )

    pygame.draw.polygon(
        sprite, (85, 125, 180),
        [(69, 57), (93, 88), (67, 81)]
    )

    pygame.draw.circle(sprite, CYAN, (50, 42), 11)
    pygame.draw.polygon(
        sprite, ORANGE,
        [(39, 90), (50, 112), (61, 90)]
    )
    pygame.draw.polygon(
        sprite, YELLOW,
        [(45, 91), (50, 104), (55, 91)]
    )

    # Rotate ship to aim in the requested direction.
    rotated = pygame.transform.rotate(sprite, angle)
    new_size = (
        max(1, int(rotated.get_width() * scale)),
        max(1, int(rotated.get_height() * scale))
    )
    rotated = pygame.transform.smoothscale(rotated, new_size)

    rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rect)


# ================= ALIENS =================
def draw_alien(x, y):
    pygame.draw.line(
        screen, PURPLE, (x - 8, y + 10), (x - 13, y + 20), 5
    )
    pygame.draw.line(
        screen, PURPLE, (x + 8, y + 10), (x + 13, y + 20), 5
    )

    pygame.draw.ellipse(
        screen, (100, 40, 155), (x - 15, y - 3, 30, 28)
    )
    pygame.draw.ellipse(
        screen, (140, 65, 195), (x - 18, y - 19, 36, 29)
    )

    pygame.draw.ellipse(screen, RED, (x - 11, y - 10, 8, 6))
    pygame.draw.ellipse(screen, RED, (x + 3, y - 10, 8, 6))


def draw_treasure(x, y):
    pulse = int(2 * math.sin(pygame.time.get_ticks() / 180))

    pygame.draw.circle(
        screen, YELLOW, (x, y), 25 + pulse, 2
    )
    pygame.draw.rect(
        screen, (130, 75, 20), (x - 18, y - 4, 36, 24)
    )
    pygame.draw.rect(
        screen, YELLOW, (x - 18, y - 9, 36, 10)
    )
    pygame.draw.rect(screen, WHITE, (x - 3, y - 3, 6, 14))


# ================= EARTH =================
def draw_earth(x, y, radius):
    pygame.draw.circle(screen, (30, 95, 205), (x, y), radius)

    pygame.draw.ellipse(
        screen, (55, 180, 100),
        (x - radius // 2, y - radius // 2,
         max(1, radius), max(1, radius // 2))
    )
    pygame.draw.ellipse(
        screen, (55, 180, 100),
        (x, y, max(1, radius // 2), max(1, radius // 2))
    )
    pygame.draw.circle(screen, CYAN, (x, y), radius, 3)


# ================= RESET GAME =================
def reset_game():
    global player, ship_position, treasure_position
    global aliens, bullets, astronaut_health, ship_health
    global treasure_found, phase, last_direction
    global damage_timer, message, message_timer
    global flight_progress, flight_aliens, flight_bullets
    global flight_spawn_timer, flight_damage_timer
    global ship_y, ship_aim, waves_spawned, landing_timer

    ship_position = pygame.Vector2(350, 900)
    player = pygame.Vector2(440, 900)
    last_direction = pygame.Vector2(1, 0)

    treasure_position = pygame.Vector2(1660, 430)

    locations = [
        (750, 780), (1050, 1100), (1450, 650),
        (1750, 1050), (800, 1400), (1850, 1450),
        (1200, 350), (500, 500)
    ]

    aliens = [
        {
            "pos": pygame.Vector2(x, y),
            "health": 2,
            "speed": random.randint(65, 95)
        }
        for x, y in locations
    ]

    bullets = []
    astronaut_health = 100
    ship_health = 100
    treasure_found = False
    phase = "explore"

    damage_timer = 0
    message = "Explore Mars and find the hidden treasure!"
    message_timer = 4

    flight_progress = 0
    flight_aliens = []
    flight_bullets = []
    flight_spawn_timer = 0
    flight_damage_timer = 0

    ship_y = HEIGHT // 2
    ship_aim = pygame.Vector2(1, 0)
    waves_spawned = 0
    landing_timer = 0


# ================= MARS WORLD =================
def draw_mars(camera):
    screen.fill((145, 62, 43))

    for x in range(-50, WIDTH + 50, 100):
        for y in range(-50, HEIGHT + 50, 90):
            pygame.draw.circle(
                screen, (165, 75, 48),
                (x + ((y // 90) % 2) * 35, y), 22, 1
            )

    # Stable rock decoration
    for rock in rocks:
        sx = int(rock["x"] - camera.x)
        sy = int(rock["y"] - camera.y)

        if -30 < sx < WIDTH + 30 and -30 < sy < HEIGHT + 30:
            shade = rock["shade"]
            pygame.draw.circle(
                screen, (shade, 65, 48),
                (sx, sy), rock["r"]
            )

    # Parked ship
    sx, sy = to_screen(ship_position, camera)
    draw_spaceship(sx, sy, 0, 0.85)
    draw_text("YOUR SPACESHIP", sx - 80, sy + 65, CYAN, SMALL)

    # Treasure is invisible until the astronaut is nearby.
    distance = player.distance_to(treasure_position)

    if not treasure_found and distance < 75:
        tx, ty = to_screen(treasure_position, camera)
        draw_treasure(tx, ty)
        draw_text("TREASURE!", tx - 55, ty - 48, YELLOW, SMALL)

    # Aliens
    for alien in aliens:
        ax, ay = to_screen(alien["pos"], camera)

        if -50 < ax < WIDTH + 50 and -50 < ay < HEIGHT + 50:
            draw_alien(ax, ay)
            health_bar(
                ax - 15, ay - 29, 30, 4,
                alien["health"], 2, RED
            )

    # Astronaut bullets
    for bullet in bullets:
        bx, by = to_screen(bullet["pos"], camera)
        pygame.draw.circle(screen, CYAN, (bx, by), 5)

    # Astronaut faces the last movement/aim direction.
    px, py = to_screen(player, camera)
    draw_astronaut(px, py, last_direction)

    draw_text("SPACE JET ADVENTURE", 20, 15, YELLOW)
    draw_text("ASTRONAUT HEALTH", 20, 49, WHITE, SMALL)
    health_bar(195, 50, 180, 17, astronaut_health, 100, GREEN)

    if not treasure_found:
        draw_text("MISSION: FIND THE HIDDEN TREASURE", 20, 80, YELLOW, SMALL)

        if distance < 180:
            signal, color = "STRONG", GREEN
        elif distance < 380:
            signal, color = "MEDIUM", YELLOW
        elif distance < 600:
            signal, color = "WEAK", ORANGE
        else:
            signal, color = "NO SIGNAL", WHITE

        draw_text("TREASURE SIGNAL: " + signal, 20, 103, color, SMALL)
    else:
        draw_text("TREASURE COLLECTED!", 20, 80, YELLOW, SMALL)
        draw_text("RETURN TO YOUR SPACESHIP", 20, 103, CYAN, SMALL)

    draw_text("WASD/ARROWS: MOVE AND AIM", 20, HEIGHT - 70, WHITE, SMALL)
    draw_text("SPACE: SHOOT IN FACING DIRECTION", 20, HEIGHT - 48, WHITE, SMALL)
    draw_text("E: ENTER SHIP", 20, HEIGHT - 26, WHITE, SMALL)


# ================= FLIGHT SCREEN =================
def draw_flight():
    screen.fill((5, 8, 30))

    tick = pygame.time.get_ticks() // 10
    for i, (sx, sy) in enumerate(stars):
        x = (sx - tick * (1 + i % 3)) % WIDTH
        pygame.draw.circle(screen, WHITE, (x, sy), 1 + i % 2)

    radius = min(int(35 + flight_progress * 1.15), 145)
    draw_earth(850, 310, radius)

    # Angle for spaceship sprite: faces right when aiming right.
    angle = math.degrees(math.atan2(-ship_aim.y, ship_aim.x))
    draw_spaceship(175, int(ship_y), angle, 0.85)

    for alien in flight_aliens:
        draw_alien(int(alien["pos"].x), int(alien["pos"].y))

    for bullet in flight_bullets:
        pygame.draw.circle(
            screen, CYAN,
            (int(bullet["pos"].x), int(bullet["pos"].y)), 5
        )

    draw_text("RETURN TO EARTH", 20, 15, YELLOW)
    draw_text(
        f"FLIGHT PROGRESS: {int(flight_progress)}%",
        20, 50, WHITE, SMALL
    )
    health_bar(20, 78, 210, 18, ship_health, 100, GREEN)
    draw_text("SPACESHIP HEALTH", 240, 78, WHITE, SMALL)
    draw_text("W/S: DODGE UP/DOWN", 20, HEIGHT - 70, WHITE, SMALL)
    draw_text("ARROWS: AIM", 20, HEIGHT - 48, WHITE, SMALL)
    draw_text("SPACE: FIRE", 20, HEIGHT - 26, WHITE, SMALL)


# ================= EARTH LANDING =================
def draw_landing():
    screen.fill((5, 10, 35))

    for sx, sy in stars:
        pygame.draw.circle(screen, WHITE, (sx, sy), 1)

    # Earth fills more of the screen as the ship approaches.
    radius = min(180 + int(landing_timer * 95), 330)
    earth_x = WIDTH // 2
    earth_y = HEIGHT + radius - 50

    draw_earth(earth_x, earth_y, radius)

    # Landing platform on Earth
    pygame.draw.ellipse(
        screen, (180, 205, 225),
        (WIDTH // 2 - 115, HEIGHT - 105, 230, 24)
    )
    pygame.draw.ellipse(
        screen, CYAN,
        (WIDTH // 2 - 115, HEIGHT - 105, 230, 24), 2
    )

    # Ship gradually descends toward the landing platform.
    start_y = 125
    target_y = HEIGHT - 155
    ship_y_now = int(start_y + (target_y - start_y) * min(landing_timer / 3.5, 1))

    scale = 0.9 + min(landing_timer / 3.5, 1) * 0.25
    draw_spaceship(WIDTH // 2, ship_y_now, 0, scale)

    draw_text("EARTH APPROACH", 20, 15, YELLOW)
    draw_text("Landing sequence initiated...", 20, 50, WHITE, SMALL)

    if landing_timer > 3.5:
        draw_text("TOUCHDOWN!", WIDTH // 2 - 65, HEIGHT - 135, GREEN)


# ================= MAIN LOOP =================
def main():
    global player, aliens, bullets, astronaut_health
    global ship_health, treasure_found, phase, last_direction
    global damage_timer, message, message_timer
    global flight_progress, flight_aliens, flight_bullets
    global flight_spawn_timer, flight_damage_timer
    global ship_y, ship_aim, waves_spawned, landing_timer

    reset_game()
    running = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.04)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_r and phase in ("won", "lost"):
                    reset_game()

                # Astronaut shoots in the direction he is facing.
                if event.key == pygame.K_SPACE and phase == "explore":
                    bullets.append({
                        "pos": player.copy(),
                        "vel": last_direction * 520,
                        "life": 1.2
                    })

                # Spaceship fires in the direction of its aim.
                if event.key == pygame.K_SPACE and phase == "flight":
                    flight_bullets.append({
                        "pos": pygame.Vector2(175, ship_y),
                        "vel": ship_aim * 650,
                        "life": 1.5
                    })

                # Enter ship only after finding the treasure.
                if event.key == pygame.K_e and phase == "explore":
                    if player.distance_to(ship_position) < 90:
                        if treasure_found:
                            phase = "flight"
                            flight_progress = 0
                            flight_aliens.clear()
                            flight_bullets.clear()
                            flight_spawn_timer = 0.5
                            flight_damage_timer = 0
                            ship_y = HEIGHT // 2
                            ship_aim = pygame.Vector2(1, 0)
                            waves_spawned = 0
                        else:
                            message = "Find the treasure before returning!"
                            message_timer = 2.5

        keys = pygame.key.get_pressed()

        # ================= EXPLORE MARS =================
        if phase == "explore":
            movement = pygame.Vector2(0, 0)

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                movement.y -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                movement.y += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                movement.x -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                movement.x += 1

            if movement.length_squared() > 0:
                movement = movement.normalize()
                player += movement * 230 * dt
                last_direction = movement.copy()

            player.x = max(30, min(WORLD_W - 30, player.x))
            player.y = max(30, min(WORLD_H - 30, player.y))

            if (
                not treasure_found
                and player.distance_to(treasure_position) < 42
            ):
                treasure_found = True
                message = "TREASURE FOUND! RETURN TO YOUR SHIP!"
                message_timer = 4

            # Aliens pursue and attack the astronaut.
            for alien in aliens[:]:
                direction = player - alien["pos"]
                distance = direction.length()

                if distance < 480 and distance > 1:
                    alien["pos"] += direction.normalize() * alien["speed"] * dt

                if distance < 35 and damage_timer <= 0:
                    astronaut_health -= 12
                    damage_timer = 0.7
                    message = "ALIEN ATTACK! KEEP MOVING!"
                    message_timer = 1.2

                # Check projectile collision.
                for bullet in bullets[:]:
                    if bullet["pos"].distance_to(alien["pos"]) < 27:
                        alien["health"] -= 1
                        if bullet in bullets:
                            bullets.remove(bullet)

                        if alien["health"] <= 0 and alien in aliens:
                            aliens.remove(alien)
                        break

            for bullet in bullets[:]:
                bullet["pos"] += bullet["vel"] * dt
                bullet["life"] -= dt

                if bullet["life"] <= 0 and bullet in bullets:
                    bullets.remove(bullet)

            damage_timer = max(0, damage_timer - dt)
            message_timer = max(0, message_timer - dt)

            if astronaut_health <= 0:
                phase = "lost"
                message = "ASTRONAUT MISSION FAILED"

            camera = pygame.Vector2(
                player.x - WIDTH / 2,
                player.y - HEIGHT / 2
            )
            camera.x = max(0, min(WORLD_W - WIDTH, camera.x))
            camera.y = max(0, min(WORLD_H - HEIGHT, camera.y))

            draw_mars(camera)

            if message_timer > 0:
                image = FONT.render(message, True, YELLOW)
                screen.blit(
                    image,
                    (WIDTH // 2 - image.get_width() // 2, 145)
                )

        # ================= SPACE FLIGHT =================
        elif phase == "flight":
            # WASD moves/dodges. Arrow keys aim.
            if keys[pygame.K_w]:
                ship_y -= 240 * dt
            if keys[pygame.K_s]:
                ship_y += 240 * dt

            if keys[pygame.K_UP]:
                ship_aim = pygame.Vector2(0, -1)
            elif keys[pygame.K_DOWN]:
                ship_aim = pygame.Vector2(0, 1)
            elif keys[pygame.K_LEFT]:
                ship_aim = pygame.Vector2(-1, 0)
            elif keys[pygame.K_RIGHT]:
                ship_aim = pygame.Vector2(1, 0)

            ship_y = max(60, min(HEIGHT - 60, ship_y))

            flight_spawn_timer -= dt

            # Spawn three waves of alien hurdles.
            if (
                waves_spawned < 3
                and flight_spawn_timer <= 0
                and flight_progress < 85
            ):
                for _ in range(3):
                    flight_aliens.append({
                        "pos": pygame.Vector2(
                            WIDTH + random.randint(20, 180),
                            random.randint(80, HEIGHT - 80)
                        ),
                        "health": 2,
                        "speed": random.randint(120, 180)
                    })

                waves_spawned += 1
                flight_spawn_timer = 2.7

            # Aliens approach the ship.
            for alien in flight_aliens[:]:
                target = pygame.Vector2(175, ship_y)
                direction = target - alien["pos"]

                if direction.length_squared() > 1:
                    alien["pos"] += (
                        direction.normalize() * alien["speed"] * dt
                    )

                if alien["pos"].distance_to(target) < 48:
                    if flight_damage_timer <= 0:
                        ship_health -= 10
                        flight_damage_timer = 0.65

                    if alien in flight_aliens:
                        flight_aliens.remove(alien)
                    continue

                for bullet in flight_bullets[:]:
                    if bullet["pos"].distance_to(alien["pos"]) < 27:
                        alien["health"] -= 1
                        if bullet in flight_bullets:
                            flight_bullets.remove(bullet)

                        if alien["health"] <= 0 and alien in flight_aliens:
                            flight_aliens.remove(alien)
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


def draw_horizontal_ship(surf, cx, cy, scale, flame=0.0, hatch=1.0, pilot=False):
    """Draw the existing rocket rotated sideways, with its nose pointing right.

    The transparent canvas is large enough for the rocket and engine flame,
    preventing the artwork from being cropped during rotation.
    """
    canvas_w = max(8, int(6.0 * scale))
    canvas_h = max(16, int(14.0 * scale))
    ship_canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)

    # draw_ship's oy is the bottom of the engine nozzle; leave room for flame.
    draw_ship(
        ship_canvas,
        canvas_w // 2,
        int(10.0 * scale),
        scale,
        flame=flame,
        hatch=hatch,
        pilot=pilot,
    )

    # An upright rocket points up; -90 degrees makes its nose point right.
    rotated = pygame.transform.rotate(ship_canvas, -90)
    ship_rect = rotated.get_rect(center=(int(cx), int(cy)))
    surf.blit(rotated, ship_rect)


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

class FinalAdventure:
    WIDTH = 1100
    HEIGHT = 700
    WORLD_END = 4100
    LAKE_STONES = [(1450, 565), (1520, 535), (1590, 558), (1660, 526), (1730, 550), (1800, 535)]
    SHIP_X = 130
    LAKE_WEST = 1400
    LAKE_EAST = 1850
    TABLE_X = 2150
    TEMPLE_X = 2920
    DOOR_X = 3670

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 58)
        self.font_title = pygame.font.Font(None, 40)
        self.running = True
        self.state = 'briefing'
        self.stage = 'run_to_lake'
        self.player_x = 280.0
        self.player_y = 585.0
        self.facing = 1
        self.walk_phase = 0.0
        self.health = 3
        self.invulnerable = 0.0
        self.ammo = 42
        self.has_first_key = True
        self.has_second_key = False
        self.has_treasure = False
        self.message = 'The first key is secure. Move away from the spaceship.'
        self.message_timer = 4.0
        self.elapsed = 0.0
        self.landing_timer = 0.0
        self.landing_x = self.WIDTH / 2
        self.landing_asteroids = []
        self.landing_spawn_timer = 0.0
        self.landing_invulnerable = 0.0
        self.landing_hits = 0
        self.landing_status_timer = 0.0
        self.shot_flash = 0.0
        self.jump_timer = 0.0
        self.jump_from = 0
        self.jump_to = 1
        self.lake_direction = 1
        self.lake_index = 0
        self.boss_health = 14
        self.boss_x = 3400.0
        self.boss_attack_timer = 1.4
        self.projectiles = []
        self.camera_x = 0.0
        self.table_key_collected = False
        self.door_unlocked = False
        self.stars = [(random.randrange(self.WIDTH), random.randrange(40, 440), random.choice((1, 1, 2))) for _ in range(100)]

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
        surf = self.font_small.render(label, True, (245, 250, 255))
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def _say(self, text, duration=2.8):
        self.message = text
        self.message_timer = duration

    def _hurt(self, message='HIT! You have only three hits.'):
        if self.invulnerable > 0 or self.state != 'playing':
            return
        self.health -= 1
        self.invulnerable = 1.15
        self._say(message, 2.0)
        if self.health <= 0:
            self.state = 'game_over'
            self._say('MISSION FAILED — the astronaut could not survive.', 5.0)

    def _begin_lake(self, direction):
        self.stage = 'lake_out' if direction == 1 else 'lake_back'
        self.lake_direction = direction
        self.lake_index = 0 if direction == 1 else len(self.LAKE_STONES) - 1
        self.player_x = float(self.LAKE_STONES[self.lake_index][0])
        self.player_y = float(self.LAKE_STONES[self.lake_index][1])
        self.jump_timer = 0.0
        if direction == 1:
            self._say('Jump from pebble to pebble with SPACE. Falling into the red lake ends the mission!', 4.0)
        else:
            self._say('Cross the same pebbles carefully to return to the spaceship.', 4.0)

    def _jump(self):
        if self.stage not in ('lake_out', 'lake_back') or self.jump_timer > 0:
            return
        stable = ((self.elapsed + self.lake_index * 0.63) % 2.8) < 2.15
        if not stable:
            self.state = 'game_over'
            self._say('THE PEBBLE SANK! The astronaut fell into the red lake.', 4.0)
            return
        target = self.lake_index + self.lake_direction
        if target < 0 or target >= len(self.LAKE_STONES):
            if self.lake_direction == 1:
                self.stage = 'key_table'
                self.player_x = float(self.LAKE_EAST + 55)
                self.player_y = 585.0
                self._say('You made it! Look for the second key on the box on the table.', 4.0)
            else:
                self.stage = 'escape_run'
                self.player_x = float(self.LAKE_WEST - 10)
                self.player_y = 585.0
                self.facing = -1
                self._say('Lake crossed! Walk back to the spaceship with the treasure.', 4.0)
            return
        self.jump_from = self.lake_index
        self.jump_to = target
        self.jump_timer = 0.34

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if self.state == 'briefing' and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.state = 'playing'
                self._say('Move right toward the red lake. Jump carefully across the pebbles!', 3.0)
            elif self.state == 'game_over' and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.__init__(self.screen)
            elif self.state == 'success' and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.running = False
            elif self.state == 'playing':
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    self._jump()
                elif event.key == pygame.K_e:
                    if self.stage == 'key_table' and abs(self.player_x - self.TABLE_X) < 100 and not self.has_second_key:
                        self.has_second_key = True
                        self.stage = 'walk_to_temple'
                        self._say('SECOND KEY COLLECTED! Walk forward at least ten steps to the temple.', 4.0)
                    elif self.stage == 'walk_to_temple' and self.player_x >= self.TEMPLE_X - 45:
                        self.stage = 'boss'
                        self.player_x = self.TEMPLE_X + 90
                        self.facing = 1
                        self.boss_x = self.TEMPLE_X + 390
                        self._say('THE GIANT ALIEN OVERLORD! Dodge its energy blasts and fire your pulse rifle!', 4.0)
                    elif self.stage == 'temple_door' and self.has_first_key and self.has_second_key:
                        self.door_unlocked = True
                        self.stage = 'treasure'
                        self._say('BOTH KEYS ACCEPTED! The temple vault opens. Press E to take the treasure.', 4.0)
                    elif self.stage == 'temple_door':
                        self._say('The vault requires BOTH keys together.', 2.5)
                    elif self.stage == 'treasure' and self.door_unlocked:
                        self.has_treasure = True
                        self.stage = 'return_to_lake'
                        self.facing = -1
                        self._say('TREASURE SECURED! Walk back to the red lake, then cross to the spaceship.', 4.0)
                elif event.key in (pygame.K_j, pygame.K_f):
                    self._shoot()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == 'briefing' and pygame.Rect(385, 555, 330, 55).collidepoint(event.pos):
                self.state = 'playing'
                self._say('Move right toward the red lake. Jump carefully across the pebbles!', 3.0)
            elif self.state == 'playing':
                self._shoot()
            elif self.state == 'game_over' and pygame.Rect(385, 490, 330, 54).collidepoint(event.pos):
                self.__init__(self.screen)
            elif self.state == 'success' and pygame.Rect(385, 490, 330, 54).collidepoint(event.pos):
                self.running = False

    def _shoot(self):
        if self.state != 'playing':
            return
        if self.ammo <= 0:
            self._say('PULSE RIFLE EMPTY! Evade the alien and keep moving.', 1.8)
            return
        if self.stage != 'boss':
            return
        self.ammo -= 1
        self.shot_flash = 0.12
        if self.stage == 'boss' and abs(self.boss_x - self.player_x) < 520:
            self.boss_health -= 1
            if self.boss_health <= 0:
                self.stage = 'temple_door'
                self.player_x = self.DOOR_X - 190
                self.facing = 1
                self.projectiles.clear()
                self._say('THE ALIEN OVERLORD IS DEFEATED! Place both keys into the temple door.', 4.0)
            else:
                self._say(f'PULSE HIT! Alien energy: {self.boss_health}/14', 0.8)

    def update(self, dt):
        self.elapsed += dt
        self.message_timer = max(0.0, self.message_timer - dt)
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.shot_flash = max(0.0, self.shot_flash - dt)

        # Interactive Earth-return sequence: steer around asteroids, then land.
        if self.state == 'landing':
            keys = pygame.key.get_pressed()
            self.landing_timer += dt
            self.landing_invulnerable = max(0.0, self.landing_invulnerable - dt)
            self.landing_status_timer = max(0.0, self.landing_status_timer - dt)

            # The astronaut can steer during the asteroid field.
            steer = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
                keys[pygame.K_LEFT] or keys[pygame.K_a]
            )
            self.landing_x += steer * 330 * dt
            self.landing_x = max(100, min(self.WIDTH - 100, self.landing_x))

            # Asteroids cross the flight path until the final descent begins.
            self.landing_spawn_timer -= dt
            if self.landing_timer < 5.8 and self.landing_spawn_timer <= 0:
                radius = random.randint(17, 31)
                self.landing_asteroids.append({
                    'x': float(random.randint(45, self.WIDTH - 45)),
                    'y': float(random.randint(-100, -35)),
                    'r': radius,
                    'vx': random.choice((-1, 1)) * random.uniform(35, 115),
                    'vy': random.uniform(220, 340),
                    'spin': random.uniform(0, math.tau),
                })
                self.landing_spawn_timer = random.uniform(0.42, 0.72)

            # Move rocks and detect collisions with the ship. A hit causes a
            # short recovery window, but never traps the player in the sequence.
            landing_progress = max(0.0, min((self.landing_timer - 0.2) / 7.3, 1.0))
            eased_landing = 1.0 - (1.0 - landing_progress) * (1.0 - landing_progress)
            landing_ground_y = int(self.HEIGHT + 100 - max(
                0.0, min((self.landing_timer - 4.0) / 2.0, 1.0)) * 145)
            landing_ground_y = min(self.HEIGHT - 75, landing_ground_y)
            ship_bottom = -300 + (landing_ground_y - 5 + 300) * eased_landing
            ship_center_y = ship_bottom - 112
            for rock in self.landing_asteroids[:]:
                rock['x'] += rock['vx'] * dt
                rock['y'] += rock['vy'] * dt
                rock['spin'] += dt * 1.8
                if rock['x'] < 20 or rock['x'] > self.WIDTH - 20:
                    rock['vx'] *= -1
                if rock['y'] > self.HEIGHT + 60:
                    self.landing_asteroids.remove(rock)
                    continue
                if (self.landing_timer < 5.8 and self.landing_invulnerable <= 0
                        and math.hypot(rock['x'] - self.landing_x,
                                       rock['y'] - ship_center_y) < rock['r'] + 17):
                    self.landing_asteroids.remove(rock)
                    self.landing_hits += 1
                    self.landing_invulnerable = 0.9
                    self.landing_status_timer = 1.0

            # Give the asteroid field time to clear, then descend to the pad.
            if self.landing_timer >= 7.5:
                self.state = 'success'
            return

        if self.state != 'playing':
            return
        keys = pygame.key.get_pressed()
        moving = False
        dx = 0
        if self.stage in ('run_to_lake', 'key_table', 'walk_to_temple', 'boss', 'temple_door', 'return_to_lake', 'escape_run'):
            dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
            speed = 280 if self.stage in ('run_to_lake', 'escape_run') else 220
            self.player_x += dx * speed * dt
            moving = dx != 0
            if dx:
                self.facing = 1 if dx > 0 else -1
        self.player_x = max(35, min(self.WORLD_END - 40, self.player_x))
        if moving:
            self.walk_phase += dt * 10
        if self.jump_timer > 0:
            self.jump_timer -= dt
            start = self.LAKE_STONES[self.jump_from]
            end = self.LAKE_STONES[self.jump_to]
            progress = 1.0 - max(0.0, self.jump_timer) / 0.34
            self.player_x = start[0] + (end[0] - start[0]) * progress
            base_y = start[1] + (end[1] - start[1]) * progress
            self.player_y = base_y - math.sin(progress * math.pi) * 72
            if self.jump_timer <= 0:
                self.lake_index = self.jump_to
                self.player_x, self.player_y = float(end[0]), float(end[1])

        # The outdoor route contains only the lake obstacle; the giant is the sole enemy.
        if self.stage == 'run_to_lake':
            if self.player_x >= self.LAKE_WEST - 8:
                self._begin_lake(1)
        elif self.stage in ('lake_out', 'lake_back'):
            if self.jump_timer <= 0:
                self.player_x, self.player_y = map(float, self.LAKE_STONES[self.lake_index])
        elif self.stage == 'key_table':
            if self.player_x >= self.TABLE_X - 45 and not self.has_second_key:
                self._say('A small box is sitting on the table. Press E to collect the second key.', 2.2)
        elif self.stage == 'walk_to_temple':
            if self.player_x >= self.TEMPLE_X - 45:
                self.player_x = self.TEMPLE_X - 45
                self._say('The temple entrance is here. Press E to enter.', 2.5)
        elif self.stage == 'return_to_lake':
            if self.player_x <= self.LAKE_EAST + 25:
                self._begin_lake(-1)
        elif self.stage == 'boss':
            self.boss_attack_timer -= dt
            if self.boss_attack_timer <= 0:
                self.boss_attack_timer = random.uniform(1.2, 1.8)
                # Telegraph before a blue energy bolt is launched.
                self.projectiles.append({'x': self.boss_x - 65, 'y': 520.0, 'vx': -330.0, 'warn': 0.35})
            for shot in self.projectiles[:]:
                shot['warn'] -= dt
                if shot['warn'] <= 0:
                    shot['x'] += shot['vx'] * dt
                    if abs(shot['x'] - self.player_x) < 24 and self.invulnerable <= 0:
                        self.projectiles.remove(shot)
                        self._hurt('ALIEN ENERGY BLAST HIT! Dodge the next one!')
                    elif shot['x'] < self.player_x - 700:
                        self.projectiles.remove(shot)
        elif self.stage == 'temple_door':
            self.player_x = min(self.player_x, self.DOOR_X - 150)
        elif self.stage == 'treasure':
            self.player_x = min(self.player_x, self.DOOR_X - 150)
        elif self.stage == 'escape_run':
            if self.player_x <= self.SHIP_X + 75:
                self.state = 'landing'
                self.landing_timer = 0.0
                self._say('TREASURE SECURED! Launching from Mars and returning to Earth...', 5.0)

        self.camera_x = max(0.0, min(self.WORLD_END - self.WIDTH, self.player_x - self.WIDTH * 0.43))

    def _sx(self, world_x):
        return int(world_x - self.camera_x)

    def draw_boss(self):
        # Alien overlord B: tall, armored silhouette with a glowing blue core and crown.
        bx, by = self._sx(self.boss_x), 590
        armor = (48, 65, 88)
        edge = (115, 163, 196)
        glow = (65, 205, 255)
        # broad lower body and segmented chest
        pygame.draw.polygon(self.screen, armor, [(bx-64, by-30), (bx-76, by-108), (bx-50, by-165), (bx-36, by-200), (bx+35, by-200), (bx+57, by-160), (bx+78, by-103), (bx+62, by-30)])
        pygame.draw.polygon(self.screen, edge, [(bx-47, by-151), (bx-28, by-191), (bx+28, by-191), (bx+48, by-151), (bx+35, by-94), (bx-35, by-94)], 3)
        # shoulders and blade-like arms
        pygame.draw.polygon(self.screen, armor, [(bx-43, by-173), (bx-95, by-185), (bx-125, by-136), (bx-99, by-111), (bx-57, by-130)])
        pygame.draw.polygon(self.screen, armor, [(bx+43, by-173), (bx+95, by-185), (bx+125, by-136), (bx+99, by-111), (bx+57, by-130)])
        pygame.draw.polygon(self.screen, edge, [(bx-95, by-185), (bx-125, by-136), (bx-99, by-111)], 3)
        pygame.draw.polygon(self.screen, edge, [(bx+95, by-185), (bx+125, by-136), (bx+99, by-111)], 3)
        # neck, angular head, and crown horns
        pygame.draw.rect(self.screen, armor, (bx-25, by-231, 50, 42), border_radius=8)
        pygame.draw.polygon(self.screen, armor, [(bx-39, by-235), (bx-30, by-279), (bx, by-296), (bx+30, by-279), (bx+39, by-235), (bx+22, by-216), (bx-22, by-216)])
        pygame.draw.polygon(self.screen, edge, [(bx-39, by-235), (bx-30, by-279), (bx, by-296), (bx+30, by-279), (bx+39, by-235)], 3)
        pygame.draw.polygon(self.screen, edge, [(bx-22, by-276), (bx-49, by-317), (bx-9, by-289)])
        pygame.draw.polygon(self.screen, edge, [(bx+22, by-276), (bx+49, by-317), (bx+9, by-289)])
        pygame.draw.line(self.screen, glow, (bx-20, by-265), (bx-5, by-260), 5)
        pygame.draw.line(self.screen, glow, (bx+5, by-260), (bx+20, by-265), 5)
        pygame.draw.circle(self.screen, glow, (bx, by-154), 23)
        pygame.draw.circle(self.screen, (205, 250, 255), (bx, by-154), 10)
        # armored legs
        pygame.draw.polygon(self.screen, armor, [(bx-48, by-43), (bx-34, by-100), (bx-8, by-98), (bx-10, by-30), (bx-55, by-20)])
        pygame.draw.polygon(self.screen, armor, [(bx+48, by-43), (bx+34, by-100), (bx+8, by-98), (bx+10, by-30), (bx+55, by-20)])
        pygame.draw.line(self.screen, edge, (bx-31, by-73), (bx-29, by-34), 4)
        pygame.draw.line(self.screen, edge, (bx+31, by-73), (bx+29, by-34), 4)
        # boss health bar
        pygame.draw.rect(self.screen, (20, 25, 38), (bx-78, 278, 156, 14), border_radius=6)
        pygame.draw.rect(self.screen, glow, (bx-78, 278, int(156 * max(0, self.boss_health)/14), 14), border_radius=6)
        for shot in self.projectiles:
            if shot['warn'] > 0:
                pygame.draw.circle(self.screen, (255, 190, 95), (self._sx(shot['x']), int(shot['y'])), 17, 2)
            else:
                pygame.draw.ellipse(self.screen, glow, (self._sx(shot['x'])-15, int(shot['y'])-7, 30, 14))

    def draw_background(self):
        self.screen.fill((8, 12, 29))
        for x, y, r in self.stars:
            pygame.draw.circle(self.screen, (125, 150, 180), (x, y), r)
        # Mars in the distance
        pygame.draw.circle(self.screen, (95, 38, 45), (890, 130), 70)
        pygame.draw.circle(self.screen, (135, 54, 52), (875, 112), 20)
        # Far mountains
        pygame.draw.polygon(self.screen, (45, 34, 49), [(0, 465), (140, 385), (270, 454), (420, 370), (565, 455), (730, 390), (900, 455), (1100, 380), (1100, 700), (0, 700)])
        pygame.draw.rect(self.screen, (154, 66, 52), (0, 485, self.WIDTH, 215))
        pygame.draw.rect(self.screen, (202, 89, 58), (0, 485, self.WIDTH, 7))
        # Lake and same six pebbles, visible throughout both crossings.
        lx1, lx2 = self._sx(self.LAKE_WEST), self._sx(self.LAKE_EAST)
        pygame.draw.rect(self.screen, (126, 10, 32), (lx1, 485, lx2-lx1, 215))
        pygame.draw.rect(self.screen, (245, 45, 55), (lx1, 485, lx2-lx1, 8))
        for i, (wx, wy) in enumerate(self.LAKE_STONES):
            x = self._sx(wx)
            stable = ((self.elapsed + i * 0.63) % 2.8) < 2.15
            rim = (70, 245, 225) if stable else (245, 65, 75)
            pygame.draw.ellipse(self.screen, (87, 80, 85), (x-25, wy-8, 50, 17))
            pygame.draw.ellipse(self.screen, rim, (x-22, wy-8, 44, 9))
            pygame.draw.line(self.screen, (230, 245, 240), (x-10, wy-5), (x+8, wy-6), 2)
        # Original rocket artwork is reused unchanged.
        ship_x = self._sx(self.SHIP_X)
        if -100 < ship_x < self.WIDTH + 100:
            draw_ship(self.screen, ship_x, 590, 12, flame=0.8 if self.state == 'success' else 0.0, hatch=1.0, pilot=False)
        # Table and second key
        tx = self._sx(self.TABLE_X)
        if -150 < tx < self.WIDTH + 150:
            pygame.draw.rect(self.screen, (92, 58, 42), (tx-53, 510, 106, 13), border_radius=3)
            pygame.draw.line(self.screen, (75, 45, 35), (tx-42, 520), (tx-47, 583), 7)
            pygame.draw.line(self.screen, (75, 45, 35), (tx+42, 520), (tx+47, 583), 7)
            pygame.draw.rect(self.screen, (132, 85, 51), (tx-25, 482, 50, 28), border_radius=3)
            pygame.draw.rect(self.screen, (208, 155, 74), (tx-25, 482, 50, 28), 2, border_radius=3)
            if not self.has_second_key:
                pygame.draw.circle(self.screen, (255, 220, 100), (tx+3, 477), 8, 3)
                pygame.draw.line(self.screen, (255, 220, 100), (tx+10, 477), (tx+23, 477), 3)
                pygame.draw.line(self.screen, (255, 220, 100), (tx+18, 477), (tx+18, 483), 2)
        # Temple exterior and entrance
        temple_x = self._sx(self.TEMPLE_X)
        if -250 < temple_x < self.WIDTH + 250 and self.stage not in ('boss', 'temple_door', 'treasure'):
            pygame.draw.polygon(self.screen, (54, 54, 73), [(temple_x-190, 500), (temple_x-155, 365), (temple_x-80, 300), (temple_x, 260), (temple_x+80, 300), (temple_x+155, 365), (temple_x+190, 500)])
            pygame.draw.polygon(self.screen, (115, 112, 133), [(temple_x-190, 500), (temple_x-155, 365), (temple_x-80, 300), (temple_x, 260), (temple_x+80, 300), (temple_x+155, 365), (temple_x+190, 500)], 5)
            pygame.draw.rect(self.screen, (15, 20, 36), (temple_x-58, 390, 116, 110), border_radius=5)
            pygame.draw.rect(self.screen, (78, 180, 220), (temple_x-58, 390, 116, 110), 3, border_radius=5)
        # Temple chamber and vault door
        if self.stage in ('boss', 'temple_door', 'treasure'):
            self.screen.fill((8, 10, 25))
            for i in range(12):
                x = i * 100 - int(self.camera_x * 0.2) % 100
                pygame.draw.polygon(self.screen, (26, 35, 55), [(x, 0), (x+35, 0), (x+80, 490), (x+40, 490)])
            pygame.draw.rect(self.screen, (35, 39, 58), (0, 490, self.WIDTH, 210))
            pygame.draw.line(self.screen, (64, 90, 117), (0, 490), (self.WIDTH, 490), 5)
            door_x = self._sx(self.DOOR_X)
            pygame.draw.rect(self.screen, (25, 36, 58), (door_x-72, 345, 144, 205), border_radius=8)
            pygame.draw.rect(self.screen, (220, 180, 80), (door_x-72, 345, 144, 205), 4, border_radius=8)
            pygame.draw.circle(self.screen, (255, 210, 75), (door_x-27, 435), 9, 3)
            pygame.draw.circle(self.screen, (255, 210, 75), (door_x+27, 435), 9, 3)
            if self.stage == 'treasure':
                pygame.draw.rect(self.screen, (255, 190, 55), (door_x-37, 455, 74, 62), border_radius=7)
                pygame.draw.circle(self.screen, (255, 240, 160), (door_x, 480), 17, 3)
                pygame.draw.circle(self.screen, (255, 240, 160), (door_x, 480), 5)
                self._text('TREASURE', 555, self.font_small, (255, 230, 130), x=max(50, min(self.WIDTH-50, door_x)))
        if self.stage == 'boss':
            self.draw_boss()
        if self.state == 'playing' and (self.invulnerable <= 0 or int(self.invulnerable * 12) % 2 == 0):
            px = self._sx(self.player_x)
            py = int(self.player_y)
            draw_astronaut(self.screen, px, py, sc=0.9, phase=self.walk_phase, face=self.facing)
            # Make the pulse rifle visibly held during the giant-alien battle.
            if self.stage == 'boss':
                gun_y = py - 43
                gun_start = px + self.facing * 7
                gun_end = px + self.facing * 42
                pygame.draw.line(self.screen, (75, 95, 115), (gun_start, gun_y + 4), (gun_end, gun_y + 4), 9)
                pygame.draw.line(self.screen, (150, 185, 205), (gun_start, gun_y), (gun_end, gun_y), 5)
                pygame.draw.line(self.screen, (75, 235, 255), (gun_end - self.facing * 7, gun_y), (gun_end, gun_y), 2)
        if self.shot_flash > 0:
            muzzle_x = self._sx(self.player_x + self.facing * 28)
            pygame.draw.line(self.screen, (105, 235, 255), (muzzle_x, int(self.player_y)-43), (muzzle_x+self.facing*35, int(self.player_y)-43), 5)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (12, 18, 34), (14, 12, 285, 98), border_radius=9)
        pygame.draw.rect(self.screen, (100, 160, 195), (14, 12, 285, 98), 2, border_radius=9)
        self.screen.blit(self.font_small.render(f'SUIT: {self.health}/3 HITS', True, (255, 130, 130)), (27, 22))
        self.screen.blit(self.font_small.render(f'PULSE AMMO: {self.ammo}', True, (110, 230, 255)), (27, 48))
        keys = ('KEY 1: YES' if self.has_first_key else 'KEY 1: NO') + '   ' + ('KEY 2: YES' if self.has_second_key else 'KEY 2: NO')
        self.screen.blit(self.font_small.render(keys, True, (255, 220, 125)), (27, 74))
        objectives = {
            'run_to_lake': 'WALK RIGHT TO THE RED LAKE',
            'lake_out': 'FIRST CROSSING: JUMP WHEN PEBBLES GLOW CYAN',
            'key_table': 'FIND THE KEY ON THE TABLE — PRESS E',
            'walk_to_temple': 'WALK FORWARD TO THE TEMPLE — THEN PRESS E',
            'boss': 'DEFEAT THE ALIEN OVERLORD — FIRE WITH J / F',
            'temple_door': 'PLACE BOTH KEYS IN THE DOOR — PRESS E',
            'treasure': 'PRESS E TO TAKE THE TREASURE',
            'return_to_lake': 'CARRY THE TREASURE BACK TO THE RED LAKE ←',
            'lake_back': 'RETURN CROSSING: JUMP BACK ACROSS THE SAME PEBBLES',
            'escape_run': 'RETURN TO THE SPACESHIP WITH THE TREASURE',
        }
        self._text(objectives.get(self.stage, ''), 128, self.font_small, (255, 225, 160))

    def draw_earth_landing(self):
        """Earth-return landing, paced like the Level 1 Moon descent."""
        self.screen.fill((3, 5, 18))

        # Space backdrop and distant stars.
        for sx, sy, radius in self.stars:
            pygame.draw.circle(self.screen, (165, 195, 245), (sx, sy), radius)

        t = self.landing_timer
        approach = min(t / 4.8, 1.0)
        descent = max(0.0, min((t - 0.2) / 7.3, 1.0))
        cx = self.WIDTH // 2
        earth_radius = int(55 + approach * 430)
        earth_cy = int(HEIGHT + 190 - approach * 100)

        # Earth grows into view during the approach, just as the Moon does
        # in Level 1. The blue atmosphere remains visible behind the surface.
        pygame.draw.circle(self.screen, (22, 75, 165), (cx, earth_cy), earth_radius)
        pygame.draw.ellipse(
            self.screen, (53, 157, 91),
            (cx - int(earth_radius * 0.63), earth_cy - int(earth_radius * 0.43),
             max(2, int(earth_radius * 0.80)), max(2, int(earth_radius * 0.46)))
        )
        pygame.draw.ellipse(
            self.screen, (39, 132, 82),
            (cx + int(earth_radius * 0.04), earth_cy + int(earth_radius * 0.05),
             max(2, int(earth_radius * 0.52)), max(2, int(earth_radius * 0.34)))
        )
        pygame.draw.circle(self.screen, (92, 205, 255), (cx, earth_cy), earth_radius, 4)

        # Re-entry streaks stop as the rocket reaches the landing zone.
        if t < 5.2:
            for i in range(12):
                sx = (i * 127 + int(t * 240)) % self.WIDTH
                sy = (i * 71 + int(t * 330)) % self.HEIGHT
                pygame.draw.line(self.screen, (65, 100, 155),
                                 (sx, sy), (sx - 11, sy + 25), 1)

        # Keep the asteroid field active during the approach, then clear it
        # before the final controlled descent.
        for rock in self.landing_asteroids:
            rx, ry, r = int(rock['x']), int(rock['y']), rock['r']
            pygame.draw.circle(self.screen, (78, 76, 91), (rx, ry), r)
            pygame.draw.circle(self.screen, (135, 130, 145),
                               (rx - r // 3, ry - r // 4), max(3, r // 4))
            pygame.draw.circle(self.screen, (42, 43, 57),
                               (rx + r // 3, ry + r // 4), max(3, r // 5))

        # A clear Earth ground/horizon comes up beneath the rocket.
        ground_y = int(self.HEIGHT + 100 - max(0.0, min((t - 4.0) / 2.0, 1.0)) * 145)
        ground_y = min(self.HEIGHT - 75, ground_y)
        if t >= 4.0:
            pygame.draw.rect(self.screen, (30, 78, 48),
                             (0, ground_y, self.WIDTH, self.HEIGHT - ground_y))
            pygame.draw.rect(self.screen, (80, 155, 78),
                             (0, ground_y, self.WIDTH, 8))
            # Distant green hills make the landing clearly take place on Earth.
            pygame.draw.ellipse(self.screen, (43, 105, 62),
                                (-120, ground_y - 48, 440, 100))
            pygame.draw.ellipse(self.screen, (51, 122, 68),
                                (280, ground_y - 58, 520, 115))
            pygame.draw.ellipse(self.screen, (43, 105, 62),
                                (730, ground_y - 42, 420, 90))

        # Wide landing pad placed directly on the ground.
        pad_y = ground_y - 3
        if t >= 4.0:
            pad = pygame.Rect(cx - 170, pad_y - 3, 340, 24)
            pygame.draw.rect(self.screen, (28, 38, 56), pad, border_radius=6)
            pygame.draw.rect(self.screen, (115, 145, 158), pad, 2, border_radius=6)
            pygame.draw.line(self.screen, (85, 235, 255),
                             (pad.left + 12, pad.top + 4),
                             (pad.right - 12, pad.top + 4), 2)
            for px in range(pad.left + 28, pad.right - 18, 48):
                pygame.draw.line(self.screen, (220, 180, 85),
                                 (px, pad.top + 12), (px + 18, pad.top + 12), 2)

        # The rocket uses the same upright, bottom-anchored drawing and
        # steady easing descent as Level 1's Moon landing.
        ship_scale = 25.0
        ship_x = int(self.landing_x)
        start_bottom = -300.0
        target_bottom = float(pad_y - 2)
        eased = 1.0 - (1.0 - descent) * (1.0 - descent)
        ship_bottom = int(start_bottom + (target_bottom - start_bottom) * eased)
        landed = t >= 7.5
        if landed:
            ship_bottom = int(target_bottom)

        flame = 1.0 if not landed else 0.0
        draw_ship(self.screen, ship_x, ship_bottom, ship_scale,
                  flame=flame * random.uniform(0.9, 1.15), hatch=1.0, pilot=True)

        # Dust puffs spread along the pad after the rocket touches down.
        if landed:
            pulse = 8 + int(abs(math.sin(t * 5.0)) * 10)
            pygame.draw.ellipse(self.screen, (155, 170, 155),
                                (ship_x - 95 - pulse, pad_y - 7, 65 + pulse, 16))
            pygame.draw.ellipse(self.screen, (155, 170, 155),
                                (ship_x + 30, pad_y - 7, 65 + pulse, 16))

        if t < 0.8:
            headline = 'LEAVING MARS — EARTH RETURN'
            subline = 'Returning to Earth...'
        elif t < 4.0:
            headline = 'EARTH APPROACH'
            subline = 'Steer with A / D or LEFT / RIGHT to avoid asteroids'
        elif t < 7.5:
            headline = 'FINAL DESCENT'
            subline = 'Rocket descending toward the Earth landing ground'
        else:
            headline = 'TOUCHDOWN!'
            subline = 'Rocket is fully landed upright on Earth ground'

        self._text(headline, 36, self.font_large,
                   (255, 190, 120) if t < 4.0 else (125, 225, 255))
        self._text(subline, 76, self.font_small, (240, 245, 255))

        if self.landing_status_timer > 0:
            self._text('ASTEROID IMPACT — STABILIZING!', 112, self.font_medium,
                       (255, 125, 100))
        self._text(f'ASTEROID HITS: {self.landing_hits}', self.HEIGHT - 38,
                   self.font_small, (255, 220, 145))
        if landed:
            self._text('LANDING GEAR LOCKED — ROCKET ON GROUND',
                       self.HEIGHT - 64, self.font_small, (120, 255, 180))

    def draw(self):
        if self.state == 'landing':
            self.draw_earth_landing()
            return
        self.draw_background()
        if self.state == 'briefing':
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((3, 6, 20, 225))
            self.screen.blit(overlay, (0, 0))
            self._text('ECLIPSE — LEVEL 4', 95, self.font_large, (255, 180, 120))
            self._text('THE TEMPLE OF THE OVERLORD', 145, self.font_title, (100, 220, 255))
            lines = [
                'Move away from the spaceship and travel toward the red lake.',
                'Cross the red lake by jumping between the glowing pebbles; falling means Game Over.',
                'Cross the pebbles, collect the second key from the box on the table.',
                'Walk ten or more steps to the temple and defeat the giant alien with your gun.',
                'Use BOTH keys on the vault door, take the treasure, cross the lake again, and return to Earth.',
                'Move: A/D or arrows   Jump: SPACE/W/UP   Pulse rifle: J/F or left click',
            ]
            for i, line in enumerate(lines):
                self._text(line, 220 + i*45, self.font_small if i == 5 else self.font_medium)
            self._button(pygame.Rect(385, 555, 330, 55), 'PRESS ENTER / CLICK TO START')
        elif self.state == 'playing':
            self.draw_hud()
            if self.message_timer > 0:
                self._text(self.message, 164, self.font_small, (255, 235, 150))
            if self.stage == 'temple_door':
                self._text('PRESS E — BOTH KEYS ARE REQUIRED', 190, self.font_small, (255, 220, 120))
            elif self.stage == 'treasure':
                self._text('PRESS E TO COLLECT THE TREASURE', 190, self.font_small, (255, 220, 120))
            elif self.stage == 'key_table' and abs(self.player_x - self.TABLE_X) < 100:
                self._text('SECOND KEY ON THE BOX — PRESS E', 190, self.font_small, (255, 220, 120))
            elif self.stage == 'walk_to_temple' and self.player_x >= self.TEMPLE_X - 45:
                self._text('TEMPLE ENTRANCE — PRESS E', 190, self.font_small, (130, 220, 255))
        elif self.state == 'game_over':
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((3, 5, 15, 235))
            self.screen.blit(overlay, (0, 0))
            self._text('MISSION FAILED', 220, self.font_large, (255, 90, 100))
            self._text('Three hits or a fall into the red lake ends the mission.', 290, self.font_medium)
            self._text('Press ENTER or click to restart Level 4.', 345, self.font_medium, (180, 220, 255))
            self._button(pygame.Rect(385, 490, 330, 54), 'TRY AGAIN')
        elif self.state == 'success':
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((2, 8, 20, 238))
            self.screen.blit(overlay, (0, 0))
            self._text('SUCCESSFULLY COMPLETED!', 185, self.font_large, (100, 255, 200))
            self._text('TREASURE RECOVERED • GIANT ALIEN DEFEATED', 255, self.font_medium)
            self._text('The astronaut returns safely to Earth.', 305, self.font_medium, (255, 220, 120))
            self._text('ECLIPSE', 385, self.font_large, (180, 220, 255))
            self._text('THE END', 435, self.font_title, (240, 245, 255))
            self._button(pygame.Rect(385, 490, 330, 54), 'FINISH')

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
    screen = pygame.display.set_mode((FinalAdventure.WIDTH, FinalAdventure.HEIGHT))
    pygame.display.set_caption('ECLIPSE — Level 4: The Temple of the Overlord')
    game = FinalAdventure(screen)
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
