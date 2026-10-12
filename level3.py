import pygame
import random

pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ECLIPSE - Space Jet Adventure")
clock = pygame.time.Clock()

# Colors
BLACK = (5, 5, 25)
WHITE = (255, 255, 255)
CYAN = (50, 220, 255)
RED = (255, 65, 65)
ORANGE = (255, 150, 40)
GREEN = (70, 255, 120)
PURPLE = (180, 80, 255)
YELLOW = (255, 230, 60)

# Fonts
font = pygame.font.SysFont("arial", 25)
small_font = pygame.font.SysFont("arial", 18)
big_font = pygame.font.SysFont("arial", 48, bold=True)

# Player settings
PLAYER_SPEED = 6
POWERUP_SIZE = 28
BOSS_MAX_HEALTH = 100

# Game states
MENU = "MENU"
PLAYING = "PLAYING"
BOSS = "BOSS"
GAME_OVER = "GAME_OVER"
WIN = "WIN"

state = MENU

# Background stars
stars = [
    [random.randrange(WIDTH), random.randrange(HEIGHT),
     random.choice([1, 2, 3])]
    for _ in range(120)
]

# Game objects
player = pygame.Rect(100, 280, 50, 35)
bullets = []
aliens = []
alien_bullets = []
powerups = []

# Game stats
score = 0
lives = 3
boss_health = BOSS_MAX_HEALTH

# Timers
spawn_timer = 0
boss_shot_timer = 0
invincible_timer = 0
rapid_timer = 0
shield_timer = 0
shoot_timer = 0
powerup_timer = 0

# Boss
boss = pygame.Rect(790, 230, 130, 110)
boss_direction = 1


def draw_text(text, font_obj, color, x, y):
    image = font_obj.render(text, True, color)
    screen.blit(image, (x, y))


def draw_background():
    screen.fill(BLACK)

    for star in stars:
        star[0] -= star[2]

        if star[0] < 0:
            star[0] = WIDTH
            star[1] = random.randrange(HEIGHT)

        pygame.draw.circle(
            screen, WHITE,
            (star[0], star[1]), star[2] // 2 + 1
        )

    # Mars
    pygame.draw.circle(screen, RED, (850, 100), 55)
    pygame.draw.circle(screen, ORANGE, (832, 88), 10)
    pygame.draw.circle(screen, ORANGE, (870, 118), 13)


def draw_player():
    # Engine flame
    pygame.draw.polygon(
        screen, ORANGE,
        [
            (player.left, player.centery - 7),
            (player.left - random.randint(10, 22), player.centery),
            (player.left, player.centery + 7)
        ]
    )

    # Spaceship body
    pygame.draw.polygon(
        screen, CYAN,
        [
            (player.right, player.centery),
            (player.left + 12, player.top),
            (player.left, player.centery),
            (player.left + 12, player.bottom)
        ]
    )

    # Cockpit
    pygame.draw.ellipse(
        screen, WHITE,
        (player.x + 12, player.y + 10, 17, 12)
    )

    # Shield effect
    if shield_timer > 0:
        pygame.draw.circle(
            screen, YELLOW, player.center, 32, 3
        )


def draw_alien(alien):
    pygame.draw.polygon(
        screen, PURPLE,
        [
            (alien.left, alien.top + 5),
            (alien.right, alien.centery),
            (alien.left, alien.bottom - 5),
            (alien.left + 10, alien.centery)
        ]
    )

    pygame.draw.circle(
        screen, RED, alien.center, 5
    )


def draw_boss():
    pygame.draw.ellipse(screen, PURPLE, boss)
    pygame.draw.ellipse(
        screen, RED,
        (boss.x + 25, boss.y + 25, 80, 60)
    )

    # Eyes
    pygame.draw.circle(
        screen, WHITE, (boss.x + 45, boss.y + 48), 12
    )
    pygame.draw.circle(
        screen, WHITE, (boss.x + 88, boss.y + 48), 12
    )
    pygame.draw.circle(
        screen, BLACK, (boss.x + 45, boss.y + 48), 5
    )
    pygame.draw.circle(
        screen, BLACK, (boss.x + 88, boss.y + 48), 5
    )

    # Boss health bar
    pygame.draw.rect(screen, RED, (300, 75, 400, 22))

    health_width = int(
        400 * max(0, boss_health) / BOSS_MAX_HEALTH
    )

    pygame.draw.rect(
        screen, GREEN, (300, 75, health_width, 22)
    )
    pygame.draw.rect(
        screen, WHITE, (300, 75, 400, 22), 2
    )

    draw_text("MARS BOSS", font, WHITE, 425, 40)


def draw_powerups():
    for item in powerups:
        kind = item["type"]
        rect = item["rect"]

        color = {
            "HEALTH": GREEN,
            "RAPID": YELLOW,
            "SHIELD": CYAN
        }[kind]

        pygame.draw.circle(screen, color, rect.center, 17)
        pygame.draw.circle(screen, WHITE, rect.center, 17, 2)

        symbol = {
            "HEALTH": "+",
            "RAPID": "R",
            "SHIELD": "S"
        }[kind]

        image = font.render(symbol, True, BLACK)
        screen.blit(image, image.get_rect(center=rect.center))


def reset_game():
    global player, bullets, aliens, alien_bullets, powerups
    global score, lives, boss_health, boss_direction
    global spawn_timer, boss_shot_timer, invincible_timer
    global rapid_timer, shield_timer, shoot_timer, powerup_timer
    global boss

    player = pygame.Rect(100, 280, 50, 35)

    bullets = []
    aliens = []
    alien_bullets = []
    powerups = []

    score = 0
    lives = 3
    boss_health = BOSS_MAX_HEALTH

    spawn_timer = 0
    boss_shot_timer = 0
    invincible_timer = 0
    rapid_timer = 0
    shield_timer = 0
    shoot_timer = 0
    powerup_timer = 0

    boss = pygame.Rect(790, 230, 130, 110)
    boss_direction = 1


def take_damage():
    global lives, invincible_timer

    if invincible_timer == 0 and shield_timer == 0:
        lives -= 1
        invincible_timer = 60


def spawn_powerup():
    kind = random.choice(["HEALTH", "RAPID", "SHIELD"])

    powerups.append({
        "type": kind,
        "rect": pygame.Rect(
            WIDTH,
            random.randint(70, HEIGHT - 50),
            POWERUP_SIZE,
            POWERUP_SIZE
        )
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

            if state == MENU:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
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
        # Move spaceship
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += PLAYER_SPEED

        player.clamp_ip(screen.get_rect())

        # Update timers
        if invincible_timer > 0:
            invincible_timer -= 1
        if rapid_timer > 0:
            rapid_timer -= 1
        if shield_timer > 0:
            shield_timer -= 1

        # Hold SPACE to shoot
        shoot_timer += 1
        shoot_delay = 6 if rapid_timer > 0 else 15

        if keys[pygame.K_SPACE] and shoot_timer >= shoot_delay:
            bullets.append(
                pygame.Rect(
                    player.right,
                    player.centery - 3,
                    18, 6
                )
            )
            shoot_timer = 0

        # Move player bullets
        for bullet in bullets[:]:
            bullet.x += 11

            if bullet.left > WIDTH:
                bullets.remove(bullet)

        # Spawn power-ups
        powerup_timer += 1

        if powerup_timer >= 600:
            powerup_timer = 0
            spawn_powerup()

        # Move and collect power-ups
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

            # Spawn small aliens
            if spawn_timer >= max(18, 55 - score // 20):
                spawn_timer = 0

                aliens.append(
                    pygame.Rect(
                        WIDTH,
                        random.randint(60, HEIGHT - 50),
                        42, 32
                    )
                )

            # Move aliens and handle collisions
            for alien in aliens[:]:
                alien.x -= 3 + score // 100

                if alien.right < 0:
                    aliens.remove(alien)

                elif alien.colliderect(player):
                    aliens.remove(alien)
                    take_damage()

            # Shoot small aliens
            for bullet in bullets[:]:
                hit_alien = None

                for alien in aliens:
                    if bullet.colliderect(alien):
                        hit_alien = alien
                        break

                if hit_alien is not None:
                    aliens.remove(hit_alien)

                    if bullet in bullets:
                        bullets.remove(bullet)

                    # Each small alien gives 10 points
                    score += 10

            # Boss appears after 10 alien defeats (100 points)
            if score >= 100:
                aliens.clear()
                alien_bullets.clear()
                state = BOSS

        elif state == BOSS:
            # Boss movement
            boss.y += 3 * boss_direction

            if boss.top <= 100:
                boss_direction = 1
            elif boss.bottom >= HEIGHT - 40:
                boss_direction = -1

            # Boss shoots
            boss_shot_timer += 1

            if boss_shot_timer >= 75:
                boss_shot_timer = 0

                alien_bullets.append(
                    pygame.Rect(
                        boss.left - 10,
                        boss.centery - 4,
                        18, 8
                    )
                )

            # Move boss projectiles
            for shot in alien_bullets[:]:
                shot.x -= 7

                if shot.right < 0:
                    alien_bullets.remove(shot)

                elif shot.colliderect(player):
                    alien_bullets.remove(shot)
                    take_damage()

            # Player bullets damage boss
            for bullet in bullets[:]:
                if bullet.colliderect(boss):
                    bullets.remove(bullet)
                    boss_health -= 5

            if boss_health <= 0:
                boss_health = 0
                state = WIN

        if lives <= 0:
            state = GAME_OVER

    # Draw everything
    draw_background()

    if state == MENU:
        draw_text(
            "SPACE JET ADVENTURE",
            big_font, CYAN, 245, 190
        )
        draw_text(
            "ECLIPSE - LEVEL 4: MARS MISSION",
            font, ORANGE, 260, 275
        )
        draw_text(
            "Press ENTER to Start",
            font, WHITE, 355, 350
        )
        draw_text(
            "Move: WASD / Arrows | Hold SPACE to Shoot",
            small_font, WHITE, 290, 405
        )
        draw_text(
            "Collect + Health, R Rapid Fire, S Shield",
            small_font, YELLOW, 280, 440
        )

    elif state in (PLAYING, BOSS):
        # Blink after damage
        if invincible_timer == 0 or invincible_timer // 6 % 2 == 0:
            draw_player()

        for bullet in bullets:
            pygame.draw.rect(screen, GREEN, bullet)

        for alien in aliens:
            draw_alien(alien)

        for shot in alien_bullets:
            pygame.draw.rect(screen, RED, shot)

        draw_powerups()

        draw_text(f"Score: {score}", font, WHITE, 20, 15)
        draw_text(f"Lives: {lives}", font, WHITE, 20, 50)

        if rapid_timer > 0:
            draw_text("RAPID FIRE!", small_font, YELLOW, 20, 125)

        if shield_timer > 0:
            draw_text("SHIELD ACTIVE!", small_font, CYAN, 20, 150)

        if state == PLAYING:
            draw_text(
                "Destroy 10 aliens to summon the boss!",
                small_font, WHITE, 20, 95
            )
        else:
            draw_boss()
            draw_text(
                "Defeat the Mars boss!",
                small_font, WHITE, 20, 95
            )

    elif state == GAME_OVER:
        draw_text("MISSION FAILED", big_font, RED, 320, 220)
        draw_text(
            f"Final Score: {score}",
            font, WHITE, 400, 300
        )
        draw_text(
            "Press R to Retry or ENTER for Menu",
            small_font, WHITE, 320, 370
        )

    elif state == WIN:
        draw_text("BOSS DEFEATED!", big_font, GREEN, 310, 200)
        draw_text("LEVEL 4 COMPLETE!", big_font, CYAN, 285, 275)
        draw_text(
            f"Final Score: {score}",
            font, WHITE, 410, 350
        )
        draw_text(
            "Press R to Play Again or ENTER for Menu",
            small_font, WHITE, 300, 410
        )

    pygame.display.flip()

pygame.quit()