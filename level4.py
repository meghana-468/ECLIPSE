import math
import random
import sys
import pygame

pygame.init()

# ==================== SETTINGS ====================
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
BLACK = (10, 12, 28)
ORANGE = (220, 100, 50)
RED = (245, 55, 65)
GREEN = (60, 230, 130)
BLUE = (65, 170, 255)
YELLOW = (255, 220, 65)
PURPLE = (175, 85, 240)
CYAN = (90, 230, 255)

# ==================== WORLD ====================
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
    for _ in range(150)
]


def draw_text(text, x, y, color=WHITE, font=FONT):
    image = font.render(str(text), True, color)
    screen.blit(image, (x, y))


def centered_text(text, y, color=WHITE, font=BIG):
    image = font.render(text, True, color)
    screen.blit(image, (WIDTH // 2 - image.get_width() // 2, y))


def health_bar(x, y, width, height, value, maximum, color):
    pygame.draw.rect(screen, (55, 35, 40), (x, y, width, height))

    ratio = max(0, min(1, value / maximum))
    if ratio > 0:
        pygame.draw.rect(
            screen, color,
            (x, y, int(width * ratio), height)
        )

    pygame.draw.rect(screen, WHITE, (x, y, width, height), 1)


def draw_astronaut(x, y):
    # Backpack
    pygame.draw.rect(screen, (70, 125, 165), (x - 16, y - 5, 9, 24))

    # Legs
    pygame.draw.line(screen, WHITE, (x - 5, y + 13), (x - 9, y + 25), 6)
    pygame.draw.line(screen, WHITE, (x + 5, y + 13), (x + 9, y + 25), 6)

    # Body
    pygame.draw.rect(
        screen, (220, 230, 240),
        (x - 11, y - 5, 22, 22), border_radius=5
    )

    # Helmet and visor
    pygame.draw.circle(screen, WHITE, (x, y - 12), 13)
    pygame.draw.circle(screen, (35, 100, 155), (x + 2, y - 12), 8)

    # Suit light
    pygame.draw.circle(screen, CYAN, (x - 4, y + 4), 3)


def draw_spaceship(x, y, scale=1.0):
    def p(px, py):
        return int(x + px * scale), int(y + py * scale)

    pygame.draw.polygon(
        screen, (165, 190, 220),
        [p(0, -38), p(27, 10), p(18, 30),
         p(-18, 30), p(-27, 10)]
    )

    pygame.draw.polygon(
        screen, (85, 125, 180),
        [p(-17, 5), p(-43, 27), p(-20, 24)]
    )

    pygame.draw.polygon(
        screen, (85, 125, 180),
        [p(17, 5), p(43, 27), p(20, 24)]
    )

    pygame.draw.circle(screen, CYAN, p(0, -12), max(3, int(9 * scale)))

    pygame.draw.polygon(
        screen, ORANGE,
        [p(-10, 28), p(0, 46), p(10, 28)]
    )


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

    pygame.draw.circle(screen, YELLOW, (x, y), 25 + pulse, 2)
    pygame.draw.rect(
        screen, (130, 75, 20), (x - 18, y - 4, 36, 24)
    )
    pygame.draw.rect(
        screen, YELLOW, (x - 18, y - 9, 36, 10)
    )
    pygame.draw.rect(screen, WHITE, (x - 3, y - 3, 6, 14))


def to_screen(pos, camera):
    return int(pos.x - camera.x), int(pos.y - camera.y)


# ==================== GAME RESET ====================
def reset_game():
    global player, ship_position, treasure_position
    global aliens, bullets, astronaut_health, ship_health
    global treasure_found, phase, last_direction
    global damage_timer, message, message_timer
    global flight_progress, flight_aliens, flight_bullets
    global flight_spawn_timer, flight_damage_timer, ship_y

    ship_position = pygame.Vector2(350, 900)
    player = pygame.Vector2(440, 900)
    last_direction = pygame.Vector2(1, 0)

    # The treasure is hidden until the astronaut approaches.
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


# ==================== MARS WORLD ====================
def draw_mars(camera):
    screen.fill((145, 62, 43))

    # Ground texture
    for x in range(-50, WIDTH + 50, 100):
        for y in range(-50, HEIGHT + 50, 90):
            pygame.draw.circle(
                screen, (165, 75, 48),
                (x + ((y // 90) % 2) * 35, y), 22, 1
            )

    # Stable rocks
    for rock in rocks:
        sx = int(rock["x"] - camera.x)
        sy = int(rock["y"] - camera.y)

        if -30 < sx < WIDTH + 30 and -30 < sy < HEIGHT + 30:
            shade = rock["shade"]
            pygame.draw.circle(
                screen, (shade, 65, 48),
                (sx, sy), rock["r"]
            )

    # Parked spaceship
    sx, sy = to_screen(ship_position, camera)
    draw_spaceship(sx, sy, 1.15)
    draw_text("YOUR SPACESHIP", sx - 80, sy + 55, CYAN, SMALL)

    # Treasure is completely hidden until nearby.
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
            health_bar(ax - 15, ay - 29, 30, 4, alien["health"], 2, RED)

    # Astronaut's bullets
    for bullet in bullets:
        bx, by = to_screen(bullet["pos"], camera)
        pygame.draw.circle(screen, CYAN, (bx, by), 5)

    # Astronaut
    px, py = to_screen(player, camera)
    draw_astronaut(px, py)

    # HUD
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

    draw_text("WASD/ARROWS: MOVE", 20, HEIGHT - 70, WHITE, SMALL)
    draw_text("SPACE: SHOOT", 20, HEIGHT - 48, WHITE, SMALL)
    draw_text("E: ENTER SHIP", 20, HEIGHT - 26, WHITE, SMALL)


# ==================== EARTH FLIGHT ====================
def draw_earth(x, y, radius):
    pygame.draw.circle(screen, (30, 95, 205), (x, y), radius)

    pygame.draw.ellipse(
        screen, (55, 180, 100),
        (x - radius // 2, y - radius // 2,
         radius, radius // 2)
    )
    pygame.draw.ellipse(
        screen, (55, 180, 100),
        (x, y, radius // 2, radius // 2)
    )
    pygame.draw.circle(screen, CYAN, (x, y), radius, 3)


def draw_flight():
    screen.fill((5, 8, 30))

    tick = pygame.time.get_ticks() // 10
    for i, (sx, sy) in enumerate(stars):
        x = (sx - tick * (1 + i % 3)) % WIDTH
        pygame.draw.circle(screen, WHITE, (x, sy), 1 + i % 2)

    radius = min(int(35 + flight_progress * 1.15), 145)
    draw_earth(850, 310, radius)

    draw_spaceship(175, int(ship_y), 1.25)

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
    draw_text("UP/DOWN: DODGE", 20, HEIGHT - 48, WHITE, SMALL)
    draw_text("SPACE: SHOOT ALIENS", 20, HEIGHT - 26, WHITE, SMALL)


# ==================== MAIN GAME LOOP ====================
def main():
    global player, aliens, bullets, astronaut_health
    global ship_health, treasure_found, phase, last_direction
    global damage_timer, message, message_timer
    global flight_progress, flight_aliens, flight_bullets
    global flight_spawn_timer, flight_damage_timer, ship_y

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

                if event.key == pygame.K_SPACE:
                    if phase == "explore":
                        bullets.append({
                            "pos": player.copy(),
                            "vel": last_direction * 520,
                            "life": 1.2
                        })

                    elif phase == "flight":
                        flight_bullets.append({
                            "pos": pygame.Vector2(210, ship_y),
                            "vel": pygame.Vector2(650, 0),
                            "life": 1.5
                        })

                if event.key == pygame.K_e and phase == "explore":
                    if player.distance_to(ship_position) < 90:
                        if treasure_found:
                            phase = "flight"
                            flight_progress = 0
                            flight_aliens.clear()
                            flight_bullets.clear()
                            flight_spawn_timer = 0
                            flight_damage_timer = 0
                            ship_y = HEIGHT // 2
                        else:
                            message = "Find the treasure before returning!"
                            message_timer = 2.5

        keys = pygame.key.get_pressed()

        # ---------- EXPLORE MARS ----------
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
                last_direction = movement.copy()
                player += movement * 230 * dt

            player.x = max(30, min(WORLD_W - 30, player.x))
            player.y = max(30, min(WORLD_H - 30, player.y))

            # Find treasure
            if (
                not treasure_found
                and player.distance_to(treasure_position) < 42
            ):
                treasure_found = True
                message = "TREASURE FOUND! RETURN TO YOUR SHIP!"
                message_timer = 4

            # Aliens chase and attack
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

                # Shooting aliens
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

                if bullet["life"] <= 0:
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

        # ---------- FLY BACK TO EARTH ----------
        elif phase == "flight":
            flight_progress += 8 * dt
            flight_spawn_timer -= dt

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                ship_y -= 260 * dt
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                ship_y += 260 * dt

            ship_y = max(55, min(HEIGHT - 55, ship_y))

            if flight_spawn_timer <= 0:
                flight_aliens.append({
                    "pos": pygame.Vector2(
                        WIDTH + 30, random.randint(70, HEIGHT - 70)
                    ),
                    "health": 2,
                    "speed": random.randint(130, 205)
                })
                flight_spawn_timer = random.uniform(0.65, 1.2)

            for alien in flight_aliens[:]:
                direction = pygame.Vector2(175, ship_y) - alien["pos"]

                if direction.length_squared() > 1:
                    alien["pos"] += direction.normalize() * alien["speed"] * dt

                if alien["pos"].distance_to(
                    pygame.Vector2(175, ship_y)
                ) < 48:
                    if flight_damage_timer <= 0:
                        ship_health -= 10
                        flight_damage_timer = 0.65

                    flight_aliens.remove(alien)
                    continue

                for bullet in flight_bullets[:]:
                    if bullet["pos"].distance_to(alien["pos"]) < 27:
                        alien["health"] -= 1
                        if bullet in flight_bullets:
                            flight_bullets.remove(bullet)

                        if alien["health"] <= 0 and alien in flight_aliens:
                            flight_aliens.remove(alien)
                        break

                if alien["pos"].x < -50 and alien in flight_aliens:
                    flight_aliens.remove(alien)

            for bullet in flight_bullets[:]:
                bullet["pos"] += bullet["vel"] * dt
                bullet["life"] -= dt

                if bullet["life"] <= 0:
                    flight_bullets.remove(bullet)

            flight_damage_timer = max(0, flight_damage_timer - dt)

            draw_flight()

            if ship_health <= 0:
                phase = "lost"
                message = "SPACESHIP DESTROYED!"
            elif flight_progress >= 100:
                phase = "won"
                message = "MISSION COMPLETE!"

        # ---------- END SCREENS ----------
        elif phase in ("won", "lost"):
            screen.fill(BLACK)

            for sx, sy in stars:
                pygame.draw.circle(screen, WHITE, (sx, sy), 2)

            if phase == "won":
                draw_earth(WIDTH // 2, 220, 110)
                centered_text("MISSION COMPLETE!", 380, GREEN)
                centered_text(
                    "TREASURE DELIVERED TO EARTH", 435, YELLOW, FONT
                )
            else:
                centered_text("MISSION FAILED", 235, RED)
                centered_text(message, 300, WHITE, FONT)

            centered_text("PRESS R TO PLAY AGAIN", 510, CYAN, FONT)
            centered_text("PRESS ESC TO QUIT", 550, WHITE, SMALL)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()