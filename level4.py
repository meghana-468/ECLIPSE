import math
import random
import sys
import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 650
FPS = 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Jet Adventure - Mars Rescue")
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 25, bold=True)
SMALL = pygame.font.SysFont("arial", 18)
TINY = pygame.font.SysFont("arial", 14)
BIG = pygame.font.SysFont("arial", 48, bold=True)

WHITE = (245, 248, 255)
CYAN = (65, 220, 255)
GOLD = (255, 205, 55)
RED = (245, 65, 65)
GREEN = (95, 235, 150)
BLACK = (5, 8, 24)

WORLD_W, WORLD_H = 2400, 2400
HORIZON = 165


def text(msg, font, color, x, y, center=False):
    image = font.render(str(msg), True, color)
    rect = image.get_rect()
    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    SCREEN.blit(image, rect)


def clamp(v, low, high):
    return max(low, min(high, v))


def reset_game():
    return {
        "player": pygame.Vector2(1200, 1200),
        "treasure": pygame.Vector2(
            random.randint(250, WORLD_W - 250),
            random.randint(250, WORLD_H - 250)
        ),
        "astronaut": pygame.Vector2(1850, 1750),
        "earth": pygame.Vector2(120, 120),
        "collected": False,
        "rescued": False,
        "won": False,
        "over": False,
        "reason": "",
        "astronaut_hp": 100,
        "ship_hp": 100,
        "deadline": None,
        "timer_length": 40,
        "aliens": [],
        "bullets": [],
        "facing": pygame.Vector2(1, 0),
        "shot_time": 0,
        "damage_time": 0,
        "ship_damage_time": 0,
        "message": "Explore Mars. Find the hidden treasure!",
        "message_until": pygame.time.get_ticks() + 4000,
        "return_spawned": False,
    }


def message(g, msg, duration=2500):
    g["message"] = msg
    g["message_until"] = pygame.time.get_ticks() + duration


def new_alien(player, distance_min=180, distance_max=550):
    angle = random.random() * math.tau
    distance = random.randint(distance_min, distance_max)
    pos = player + pygame.Vector2(
        math.cos(angle) * distance,
        math.sin(angle) * distance
    )
    pos.x = clamp(pos.x, 40, WORLD_W - 40)
    pos.y = clamp(pos.y, 40, WORLD_H - 40)
    return pos


def spawn_aliens(g, count, distance_min=180, distance_max=550):
    for _ in range(count):
        g["aliens"].append(
            new_alien(g["player"], distance_min, distance_max)
        )


def draw_health(x, y, width, hp):
    hp = clamp(hp, 0, 100)
    color = GREEN if hp > 60 else (255, 160, 55) if hp > 30 else RED
    pygame.draw.rect(SCREEN, (35, 40, 55), (x, y, width, 17))
    if hp:
        pygame.draw.rect(
            SCREEN, color, (x, y, int(width * hp / 100), 17)
        )
    pygame.draw.rect(SCREEN, WHITE, (x, y, width, 17), 2)


def project(pos, player, depth_adjust=0):
    """Camera follows the player; distant objects appear smaller."""
    dx = pos.x - player.x
    dy = pos.y - player.y

    # Perspective-like scale: objects farther away shrink.
    distance = math.hypot(dx, dy)
    scale = clamp(1.15 - distance / 1500, 0.38, 1.0)

    sx = WIDTH / 2 + dx * 0.78
    sy = HEIGHT * 0.70 + dy * 0.43

    return int(sx), int(sy), scale


def draw_ship(x, y, angle, scale=1.0):
    w, h = int(68 * scale), int(44 * scale)
    surf = pygame.Surface((max(w, 20), max(h, 15)), pygame.SRCALPHA)
    w, h = surf.get_size()

    pygame.draw.polygon(surf, (195, 230, 250), [
        (int(w*.08), int(h*.5)),
        (int(w*.72), int(h*.10)),
        (int(w*.98), int(h*.5)),
        (int(w*.72), int(h*.90))
    ])
    pygame.draw.polygon(surf, (45, 130, 205), [
        (int(w*.30), int(h*.5)),
        (int(w*.68), int(h*.30)),
        (int(w*.80), int(h*.5)),
        (int(w*.68), int(h*.70))
    ])
    pygame.draw.polygon(surf, (255, 145, 65), [
        (int(w*.10), int(h*.36)),
        (0, int(h*.5)),
        (int(w*.10), int(h*.64))
    ])

    rotated = pygame.transform.rotate(surf, angle)
    SCREEN.blit(rotated, rotated.get_rect(center=(int(x), int(y))))


def draw_astronaut(x, y, scale=1, rescued=False):
    suit = GREEN if rescued else (230, 235, 245)
    s = scale

    pygame.draw.ellipse(
        SCREEN, (65, 30, 30),
        (int(x-17*s), int(y+17*s), int(34*s), max(3, int(8*s)))
    )
    pygame.draw.rect(
        SCREEN, (80, 95, 115),
        (int(x-15*s), int(y-3*s), max(3, int(8*s)), int(21*s))
    )
    pygame.draw.rect(
        SCREEN, suit,
        (int(x-8*s), int(y-3*s), max(5, int(16*s)), int(22*s)),
        border_radius=max(2, int(4*s))
    )
    pygame.draw.circle(
        SCREEN, WHITE, (int(x), int(y-13*s)), max(4, int(12*s)), 2
    )
    pygame.draw.ellipse(
        SCREEN, (50, 145, 195),
        (int(x-7*s), int(y-18*s), max(4, int(14*s)), max(3, int(10*s)))
    )
    pygame.draw.line(
        SCREEN, suit, (int(x-5*s), int(y+5*s)),
        (int(x-12*s), int(y+13*s)), max(2, int(4*s))
    )
    pygame.draw.line(
        SCREEN, suit, (int(x+5*s), int(y+5*s)),
        (int(x+12*s), int(y+13*s)), max(2, int(4*s))
    )


def draw_alien(x, y, scale=1):
    s = scale
    w, h = max(10, int(30*s)), max(8, int(27*s))
    pygame.draw.ellipse(
        SCREEN, (60, 20, 20),
        (int(x-w/2), int(y+h/3), w, max(3, h//3))
    )
    pygame.draw.ellipse(
        SCREEN, (85, 220, 100),
        (int(x-w/2), int(y-h/2), w, h)
    )
    eye = max(2, int(5*s))
    pygame.draw.ellipse(
        SCREEN, WHITE,
        (int(x-9*s), int(y-5*s), eye*2, eye*2)
    )
    pygame.draw.ellipse(
        SCREEN, WHITE,
        (int(x+2*s), int(y-5*s), eye*2, eye*2)
    )
    pygame.draw.circle(
        SCREEN, BLACK, (int(x-6*s), int(y-2*s)), max(1, int(2*s))
    )
    pygame.draw.circle(
        SCREEN, BLACK, (int(x+5*s), int(y-2*s)), max(1, int(2*s))
    )


def draw_mars_world(g, now):
    SCREEN.fill((5, 8, 24))

    # Stars only in the distant sky. No extra red planet.
    for i in range(100):
        x = (i * 137 + 29) % WIDTH
        y = (i * 61 + 13) % HORIZON
        brightness = 140 + int(70 * (0.5 + 0.5 * math.sin(now/400+i)))
        pygame.draw.circle(
            SCREEN, (brightness, brightness, min(255, brightness+20)),
            (x, y), 1 if i % 3 else 2
        )

    # Mars mountains on the horizon.
    pygame.draw.polygon(SCREEN, (70, 32, 38), [
        (0, HORIZON+45), (0, HORIZON+10), (130, HORIZON+32),
        (240, HORIZON-8), (360, HORIZON+35),
        (500, HORIZON-12), (650, HORIZON+30),
        (790, HORIZON-3), (900, HORIZON+25),
        (WIDTH, HORIZON+5), (WIDTH, HORIZON+50)
    ])

    # Continuous rocky Mars ground.
    pygame.draw.rect(
        SCREEN, (133, 52, 42),
        (0, HORIZON+25, WIDTH, HEIGHT-HORIZON)
    )
    pygame.draw.polygon(SCREEN, (155, 62, 44), [
        (0, HORIZON+85), (WIDTH, HORIZON+70),
        (WIDTH, HEIGHT), (0, HEIGHT)
    ])

    # Perspective travel grid.
    for i in range(13):
        x = i * WIDTH // 12
        pygame.draw.line(
            SCREEN, (170, 72, 48),
            (WIDTH//2 + (x-WIDTH//2)//5, HORIZON+25),
            (x, HEIGHT), 1
        )

    for i in range(9):
        t = i / 8
        y = int(HORIZON + 30 + t*t*(HEIGHT-HORIZON-20))
        pygame.draw.line(SCREEN, (165, 66, 47), (0, y), (WIDTH, y), 1)

    # Rocks drift according to camera position, making exploration visible.
    player = g["player"]
    for i in range(45):
        wx = (i * 191 + 73) % WORLD_W
        wy = (i * 307 + 97) % WORLD_H
        rock_pos = pygame.Vector2(wx, wy)
        sx, sy, scale = project(rock_pos, player)
        if HORIZON < sy < HEIGHT and -40 < sx < WIDTH+40:
            size = max(2, int((i % 7 + 4) * scale))
            color = random.choice([
                (91, 42, 39), (105, 47, 40), (115, 53, 43)
            ])
            pygame.draw.ellipse(
                SCREEN, color,
                (sx-size, sy-size//2, size*2, max(3, size))
            )


def main():
    g = reset_game()
    spawn_aliens(g, 8, 240, 600)
    running = True

    while running:
        dt = CLOCK.tick(FPS) / 1000
        now = pygame.time.get_ticks()
        player = g["player"]
        astronaut = g["astronaut"]
        active = not g["won"] and not g["over"]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (g["won"] or g["over"]):
                    g = reset_game()
                    spawn_aliens(g, 8, 240, 600)
                    player = g["player"]

        keys = pygame.key.get_pressed()

        if active:
            move = pygame.Vector2(0, 0)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move.x -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move.x += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                move.y -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                move.y += 1

            if move.length_squared():
                move = move.normalize()
                g["facing"] = move.copy()
                player += move * 260 * dt

            player.x = clamp(player.x, 30, WORLD_W-30)
            player.y = clamp(player.y, 30, WORLD_H-30)

            # Treasure is hidden until the player gets close enough.
            if not g["collected"] and player.distance_to(g["treasure"]) < 65:
                g["collected"] = True
                g["deadline"] = now + g["timer_length"] * 1000
                message(g, "TREASURE FOUND! Rescue the astronaut quickly!", 5000)
                spawn_aliens(g, 4, 160, 350)

            # Spacebar fires in the direction of travel.
            if keys[pygame.K_SPACE] and now-g["shot_time"] > 240:
                direction = g["facing"].normalize()
                g["bullets"].append({
                    "pos": pygame.Vector2(player),
                    "vel": direction * 540
                })
                g["shot_time"] = now

            # Move shots in world space.
            for bullet in g["bullets"][:]:
                bullet["pos"] += bullet["vel"] * dt
                p = bullet["pos"]
                if not (0 <= p.x <= WORLD_W and 0 <= p.y <= WORLD_H):
                    g["bullets"].remove(bullet)

            # Aliens hide around the map until the player comes near.
            # Once the treasure is found, some pursue the astronaut.
            for alien in g["aliens"][:]:
                target = astronaut if g["collected"] and not g["rescued"] else player
                delta = target - alien
                distance = delta.length()

                if distance < 700 and distance > 1:
                    speed = 78 if g["collected"] else 48
                    alien += delta.normalize() * speed * dt

                # Shoot aliens by hitting them with a bolt.
                hit = False
                for bullet in g["bullets"][:]:
                    if alien.distance_to(bullet["pos"]) < 32:
                        g["aliens"].remove(alien)
                        g["bullets"].remove(bullet)
                        hit = True
                        break
                if hit:
                    continue

                # Aliens attack the astronaut before rescue.
                if (g["collected"] and not g["rescued"]
                        and alien.distance_to(astronaut) < 45
                        and now-g["damage_time"] > 800):
                    g["astronaut_hp"] = max(0, g["astronaut_hp"]-10)
                    g["damage_time"] = now
                    message(g, "ALERT! Aliens are attacking the astronaut!", 1200)

                # During the return trip, aliens damage the ship.
                if (g["rescued"] and player.distance_to(alien) < 60
                        and now-g["ship_damage_time"] > 900):
                    g["ship_hp"] = max(0, g["ship_hp"]-8)
                    g["ship_damage_time"] = now
                    message(g, "ALIEN ATTACK! Protect your spaceship!", 1300)

            # Health / timer failure.
            if g["collected"] and not g["rescued"] and g["astronaut_hp"] <= 0:
                g["over"] = True
                g["reason"] = "The astronaut's health reached zero."

            if (g["collected"] and not g["rescued"]
                    and now >= g["deadline"]):
                g["over"] = True
                g["reason"] = "The rescue countdown expired."

            if g["ship_hp"] <= 0:
                g["over"] = True
                g["reason"] = "Alien attacks destroyed your ship."

            # Rescue is only possible after finding the treasure.
            if (g["collected"] and not g["rescued"]
                    and player.distance_to(astronaut) < 75):
                g["rescued"] = True
                message(g, "ASTRONAUT RESCUED! Return to the Earth landing zone!", 4500)
                g["aliens"] = g["aliens"][:]
                # More enemies arrive to chase the ship during the return.
                spawn_aliens(g, 7, 250, 600)
                g["return_spawned"] = True

            # Earth is a landing zone on the far side of the world.
            if (g["collected"] and g["rescued"]
                    and player.distance_to(g["earth"]) < 85):
                g["won"] = True

        draw_mars_world(g, now)

        # Draw objects in camera space.
        # The treasure is deliberately invisible until it is found.
        if not g["collected"]:
            sx, sy, scale = project(g["treasure"], player)
            if HORIZON < sy < HEIGHT and -50 < sx < WIDTH+50:
                pulse = int(5*math.sin(now/140))
                pygame.draw.circle(
                    SCREEN, (255, 170, 35), (sx, sy),
                    max(8, int(22*scale)+pulse), 2
                )
                # Only a subtle shimmer appears at very close range.
                if player.distance_to(g["treasure"]) < 240:
                    pygame.draw.polygon(SCREEN, GOLD, [
                        (sx, sy-int(13*scale)), (sx+int(10*scale), sy),
                        (sx, sy+int(13*scale)), (sx-int(10*scale), sy)
                    ])
                    text("TREASURE SIGNAL", TINY, GOLD, sx, sy+18, True)

        # Earth marker is shown only once the astronaut has been rescued.
        if g["rescued"]:
            ex, ey, es = project(g["earth"], player)
            if HORIZON < ey < HEIGHT and -40 < ex < WIDTH+40:
                pygame.draw.circle(SCREEN, CYAN, (ex, ey), max(12, int(22*es)), 3)
                text("EARTH LANDING ZONE", TINY, CYAN, ex, ey+25, True)
            else:
                dx = g["earth"].x-player.x
                dy = g["earth"].y-player.y
                text(
                    f"EARTH DIRECTION: {'LEFT' if dx < -60 else 'RIGHT' if dx > 60 else 'AHEAD'}",
                    SMALL, CYAN, WIDTH-300, 88
                )

        # Astronaut
        if not g["rescued"]:
            ax, ay, ass = project(astronaut, player)
            if -40 < ax < WIDTH+40 and HORIZON < ay < HEIGHT+40:
                draw_astronaut(ax, ay, ass)
                text("ASTRONAUT", TINY, WHITE, ax, ay+27, True)

        # Aliens
        for alien in g["aliens"]:
            ax, ay, scale = project(alien, player)
            if -50 < ax < WIDTH+50 and HORIZON < ay < HEIGHT+40:
                draw_alien(ax, ay, scale)
                # Red warning ring for nearby enemies.
                if alien.distance_to(player) < 160:
                    pygame.draw.circle(SCREEN, RED, (ax, ay), max(13, int(23*scale)), 1)

        # Projectiles
        for bullet in g["bullets"]:
            bx, by, scale = project(bullet["pos"], player)
            if -10 < bx < WIDTH+10 and HORIZON < by < HEIGHT+10:
                pygame.draw.circle(SCREEN, CYAN, (bx, by), max(2, int(4*scale)))
                pygame.draw.circle(SCREEN, WHITE, (bx, by), max(1, int(2*scale)))

        # Spaceship is visible near the camera, with perspective shadow.
        ship_angle = -math.degrees(math.atan2(g["facing"].y, g["facing"].x))
        pygame.draw.ellipse(
            SCREEN, (65, 25, 25), (WIDTH//2-35, HEIGHT-95, 70, 17)
        )
        draw_ship(WIDTH//2, HEIGHT-105, ship_angle, 1.15)

        # HUD
        pygame.draw.rect(SCREEN, (12, 18, 40), (12, 12, 480, 135), border_radius=12)
        pygame.draw.rect(SCREEN, (75, 105, 155), (12, 12, 480, 135), 2, border_radius=12)
        text("SPACE JET ADVENTURE - MARS", SMALL, WHITE, 26, 20)

        if not g["collected"]:
            objective = "Explore Mars and find the hidden treasure"
            objective_color = GOLD
        elif not g["rescued"]:
            objective = "Rescue the astronaut before time runs out!"
            objective_color = RED
        else:
            objective = "Return to Earth while aliens attack!"
            objective_color = GREEN
        text(objective, TINY, objective_color, 26, 47)

        text("ASTRONAUT", TINY, WHITE, 26, 72)
        draw_health(122, 73, 185, g["astronaut_hp"])
        text(f'{g["astronaut_hp"]} HP', TINY, WHITE, 315, 73)

        text("SHIP", TINY, WHITE, 26, 99)
        draw_health(122, 100, 185, g["ship_hp"])
        text(f'{g["ship_hp"]} HP', TINY, WHITE, 315, 100)

        if g["collected"] and not g["rescued"] and not g["over"]:
            seconds = max(0, math.ceil((g["deadline"]-now)/1000))
            color = RED if seconds <= 10 else GOLD
            text(f"RESCUE: {seconds}s", FONT, color, 850, 35, True)

        if now < g["message_until"] and active:
            text(g["message"], SMALL, WHITE, WIDTH//2, 165, True)

        text(
            "MOVE: WASD / ARROWS     SHOOT: SPACE     RESTART: R     QUIT: ESC",
            TINY, WHITE, WIDTH//2, HEIGHT-18, True
        )

        if g["won"] or g["over"]:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((3, 4, 15, 215))
            SCREEN.blit(overlay, (0, 0))

            if g["won"]:
                text("MISSION COMPLETE!", BIG, GOLD, WIDTH//2, HEIGHT//2-55, True)
                text(
                    "Treasure secured. Astronaut rescued. Earth reached!",
                    SMALL, WHITE, WIDTH//2, HEIGHT//2+2, True
                )
            else:
                text("MISSION FAILED", BIG, RED, WIDTH//2, HEIGHT//2-55, True)
                text(g["reason"], SMALL, WHITE, WIDTH//2, HEIGHT//2+2, True)

            text("Press R to play again  |  ESC to quit",
                 SMALL, CYAN, WIDTH//2, HEIGHT//2+52, True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()