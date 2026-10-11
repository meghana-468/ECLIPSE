import math
import random
import sys
import pygame


# ECLIPSE - LEVEL 2: LUNAR SURVIVAL
# Controls:
#   WASD / Arrow keys : Move
#   Left mouse button : Fire toward the cursor
#   SPACE             : Fire at the nearest alien
#   P                 : Pause / resume
#   R                 : Restart after game over
#   ESC               : Exit this level
#
# Uses Pygame only; all visuals are drawn with Pygame primitives.


class Level2:
    WIDTH = 1100
    HEIGHT = 700

    def __init__(self, screen, on_complete=None, on_exit=None):
        self.screen = screen
        self.on_complete = on_complete
        self.on_exit = on_exit
        self.world = pygame.Surface((self.WIDTH, self.HEIGHT)).convert()
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.state = "playing"

        self.rng = random.Random(21)
        self.stars = [
            (self.rng.randrange(self.WIDTH), self.rng.randrange(10, 455),
             self.rng.choice((1, 1, 1, 2)), self.rng.randrange(95, 220))
            for _ in range(180)
        ]
        self.distant_craters = [
            (110, 612, 45, 13), (315, 655, 63, 17),
            (560, 605, 38, 12), (815, 660, 72, 18),
            (1015, 615, 47, 14), (680, 681, 29, 8),
        ]
        self.rocks = [
            (150, 642, 1.0), (390, 626, 0.8), (735, 650, 1.15),
            (955, 638, 0.9), (535, 671, 0.7), (1040, 676, 0.65),
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
        self.state = "playing"
        self.paused = False
        self.message_timer = 3.5

    # Level interface: the parent game loop should pass each event here.
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            if self.on_exit:
                self.on_exit()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
                if self.on_exit:
                    self.on_exit()
            elif event.key == pygame.K_p and self.state == "playing":
                self.paused = not self.paused
            elif event.key == pygame.K_r and self.state == "game_over":
                self.reset_game()
            elif event.key == pygame.K_SPACE and self.state == "playing" and not self.paused:
                self.fire_at_nearest()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "playing" and not self.paused:
                mx, my = self._mouse_to_world(event.pos)
                self.fire_toward(mx, my)

        if event.type == pygame.MOUSEMOTION and self.state == "playing":
            mx, _ = self._mouse_to_world(event.pos)
            if mx < self.player_x:
                self.facing = -1
            elif mx > self.player_x:
                self.facing = 1

    def _mouse_to_world(self, pos):
        target_w, target_h = self.screen.get_size()
        if target_w <= 0 or target_h <= 0:
            return pos
        return pos[0] * self.WIDTH / target_w, pos[1] * self.HEIGHT / target_h

    def update(self, dt):
        dt = min(max(dt, 0.0), 0.04)
        if self.state != "playing" or self.paused:
            return

        self.elapsed += dt
        self.walk_time += dt * 9.0
        self.shot_cooldown = max(0.0, self.shot_cooldown - dt)
        self.damage_cooldown = max(0.0, self.damage_cooldown - dt)
        self.hit_flash = max(0.0, self.hit_flash - dt)
        self.shake = max(0.0, self.shake - dt * 18.0)
        self.message_timer = max(0.0, self.message_timer - dt)

        keys = pygame.key.get_pressed()
        dx = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        dy = float(keys[pygame.K_s] or keys[pygame.K_DOWN]) - float(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
        if dx or dy:
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length
            self.player_x += dx * self.player_speed * dt
            self.player_y += dy * self.player_speed * dt
            if dx:
                self.facing = 1 if dx > 0 else -1

        # Keep the astronaut in the playable lunar-surface area.
        self.player_x = max(34, min(self.WIDTH - 34, self.player_x))
        self.player_y = max(465, min(650, self.player_y))

        self._update_spawning(dt)
        self._update_aliens(dt)
        self._update_bullets(dt)
        self._update_particles(dt)

        if self.player_health <= 0:
            self.player_health = 0
            self.state = "game_over"

    def _update_spawning(self, dt):
        self.spawn_timer -= dt
        # Difficulty increases gradually, with a hard cap to keep combat readable.
        self.alien_spawn_interval = max(0.9, 2.15 - self.elapsed * 0.012)
        if self.spawn_timer <= 0 and len(self.aliens) < 9:
            self.spawn_alien()
            self.spawn_timer = self.alien_spawn_interval * random.uniform(0.78, 1.22)

    def spawn_alien(self):
        side = random.choice(("left", "right", "back"))
        if side == "left":
            x = random.randint(35, 100)
            y = random.randint(490, 640)
        elif side == "right":
            x = random.randint(self.WIDTH - 100, self.WIDTH - 35)
            y = random.randint(490, 640)
        else:
            x = random.randint(100, self.WIDTH - 100)
            y = random.randint(475, 520)

        # A few sturdier aliens appear as the encounter progresses.
        heavy = self.elapsed > 35 and random.random() < 0.28
        self.aliens.append({
            "x": float(x),
            "y": float(y),
            "hp": 2 if heavy else 1,
            "max_hp": 2 if heavy else 1,
            "speed": random.uniform(43, 61) + min(22, self.elapsed * 0.12),
            "radius": 19 if heavy else 15,
            "phase": random.uniform(0, math.tau),
            "heavy": heavy,
            "flash": 0.0,
        })

    def _update_aliens(self, dt):
        for alien in self.aliens[:]:
            alien["flash"] = max(0.0, alien["flash"] - dt)
            dx = self.player_x - alien["x"]
            dy = self.player_y - alien["y"]
            distance = math.hypot(dx, dy)
            if distance > 0.001:
                speed = alien["speed"]
                alien["x"] += (dx / distance) * speed * dt
                alien["y"] += (dy / distance) * speed * dt
            alien["phase"] += dt * 4.0

            if distance < alien["radius"] + 19 and self.damage_cooldown <= 0:
                self.player_health = max(0.0, self.player_health - 18.0)
                self.damage_cooldown = 0.7
                self.hit_flash = 0.22
                self.shake = 7.0
                self._burst(self.player_x, self.player_y, (255, 90, 75), 9)
                # Push the alien away a little so contact doesn't drain health instantly.
                if distance > 0.001:
                    alien["x"] -= (dx / distance) * 35
                    alien["y"] -= (dy / distance) * 35

    def _update_bullets(self, dt):
        for bullet in self.bullets[:]:
            bullet["x"] += bullet["vx"] * dt
            bullet["y"] += bullet["vy"] * dt
            bullet["life"] -= dt
            if bullet["life"] <= 0 or not (
                -20 <= bullet["x"] <= self.WIDTH + 20
                and 0 <= bullet["y"] <= self.HEIGHT
            ):
                self.bullets.remove(bullet)
                continue

            for alien in self.aliens[:]:
                if math.hypot(alien["x"] - bullet["x"], alien["y"] - bullet["y"]) < alien["radius"] + 5:
                    alien["hp"] -= 1
                    alien["flash"] = 0.12
                    self._burst(bullet["x"], bullet["y"], (100, 235, 255), 5)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if alien["hp"] <= 0:
                        self.aliens.remove(alien)
                        self.kills += 1
                        self._burst(alien["x"], alien["y"], (105, 255, 155), 17)
                    break

    def _update_particles(self, dt):
        for particle in self.particles[:]:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["vx"] *= max(0.0, 1.0 - dt * 1.8)
            particle["vy"] *= max(0.0, 1.0 - dt * 1.8)
            particle["life"] -= dt
            if particle["life"] <= 0:
                self.particles.remove(particle)

    def _burst(self, x, y, color, count):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(45, 185)
            life = random.uniform(0.18, 0.55)
            self.particles.append({
                "x": float(x), "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": life, "max_life": life,
                "size": random.randint(2, 4), "color": color,
            })

    def fire_at_nearest(self):
        if self.shot_cooldown > 0:
            return
        if self.aliens:
            target = min(
                self.aliens,
                key=lambda a: math.hypot(a["x"] - self.player_x, a["y"] - self.player_y)
            )
            self.fire_toward(target["x"], target["y"])
        else:
            self.fire_toward(self.player_x + self.facing * 100, self.player_y)

    def fire_toward(self, target_x, target_y):
        if self.shot_cooldown > 0 or self.state != "playing" or self.paused:
            return
        start_x = self.player_x + self.facing * 20
        start_y = self.player_y - 5
        dx, dy = target_x - start_x, target_y - start_y
        length = math.hypot(dx, dy)
        if length < 0.001:
            dx, dy, length = float(self.facing), 0.0, 1.0
        speed = 560.0
        self.bullets.append({
            "x": start_x, "y": start_y,
            "vx": dx / length * speed, "vy": dy / length * speed,
            "life": 1.15,
        })
        self.shot_cooldown = 0.22
        self._burst(start_x, start_y, (90, 225, 255), 3)

    def draw(self, target=None):
        surface = self.world
        self._draw_background(surface)
        self._draw_lunar_surface(surface)

        # Enemies and projectiles appear in front of the terrain.
        for alien in sorted(self.aliens, key=lambda a: a["y"]):
            self._draw_alien(surface, alien)
        for bullet in self.bullets:
            tail_x = bullet["x"] - bullet["vx"] * 0.025
            tail_y = bullet["y"] - bullet["vy"] * 0.025
            pygame.draw.line(surface, (45, 155, 220), (int(tail_x), int(tail_y)),
                             (int(bullet["x"]), int(bullet["y"])), 5)
            pygame.draw.circle(surface, (180, 250, 255),
                               (int(bullet["x"]), int(bullet["y"])), 3)

        self._draw_astronaut(surface)
        self._draw_particles(surface)
        self._draw_hud(surface)

        if self.hit_flash > 0:
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 35, 35, int(65 * self.hit_flash / 0.22)))
            surface.blit(overlay, (0, 0))

        if self.paused:
            self._draw_center_panel(surface, "MISSION PAUSED", "Press P to resume")
        elif self.state == "game_over":
            self._draw_center_panel(
                surface, "SUIT FAILURE",
                f"Aliens eliminated: {self.kills}   |   Press R to retry   |   ESC to exit"
            )
        elif self.message_timer > 0:
            self._draw_mission_message(surface)

        target = target or self.screen
        if target.get_size() == (self.WIDTH, self.HEIGHT):
            target.blit(surface, (0, 0))
        else:
            scaled = pygame.transform.smoothscale(surface, target.get_size())
            target.blit(scaled, (0, 0))

    def _draw_background(self, surface):
        surface.fill((3, 5, 16))
        # Soft space glow behind the Moon.
        glow = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (25, 42, 73, 55), (170, 250, 780, 320))
        pygame.draw.ellipse(glow, (45, 70, 100, 25), (280, 300, 560, 220))
        surface.blit(glow, (0, 0))

        for x, y, radius, brightness in self.stars:
            pulse = 0.88 + 0.12 * math.sin(self.elapsed * 1.7 + x * 0.03)
            c = int(brightness * pulse)
            pygame.draw.circle(surface, (c, c, min(255, c + 8)), (x, y), radius)

        # Earth hanging above the lunar horizon.
        earth_x, earth_y = 865, 150
        pygame.draw.circle(surface, (16, 47, 92), (earth_x, earth_y), 51)
        pygame.draw.circle(surface, (40, 111, 183), (earth_x - 5, earth_y - 3), 46)
        pygame.draw.ellipse(surface, (70, 151, 112), (832, 119, 24, 19))
        pygame.draw.ellipse(surface, (73, 157, 118), (858, 143, 28, 17))
        pygame.draw.ellipse(surface, (50, 127, 97), (842, 163, 18, 22))
        pygame.draw.arc(surface, (115, 190, 235), (814, 99, 102, 102), 0.4, 2.8, 3)
        pygame.draw.circle(surface, (160, 210, 245), (849, 130), 3)

        # Distant jagged ridge.
        ridge = [(0, 505), (0, 478), (70, 459), (135, 486), (205, 450),
                 (280, 483), (355, 463), (430, 493), (510, 454), (585, 481),
                 (655, 451), (720, 480), (790, 459), (875, 486), (945, 453),
                 (1030, 482), (1100, 463), (1100, 545), (0, 545)]
        pygame.draw.polygon(surface, (34, 39, 54), ridge)
        pygame.draw.lines(surface, (70, 76, 91), False, ridge[1:-2], 2)

    def _draw_lunar_surface(self, surface):
        # Main surface with a subtle horizon glow.
        pygame.draw.rect(surface, (42, 43, 53), (0, 525, self.WIDTH, 175))
        pygame.draw.line(surface, (104, 106, 119), (0, 526), (self.WIDTH, 526), 2)
        pygame.draw.polygon(surface, (54, 55, 65),
                            [(0, 550), (140, 538), (280, 558), (425, 542),
                             (560, 554), (730, 539), (880, 559), (1100, 542),
                             (1100, 700), (0, 700)])
        # Fine ground striations.
        for i in range(36):
            x = (i * 83 + 29) % self.WIDTH
            y = 565 + ((i * 37) % 125)
            length = 9 + (i % 5) * 5
            pygame.draw.line(surface, (67, 68, 78), (x, y), (x + length, y - 2), 1)

        for x, y, w, h in self.distant_craters:
            pygame.draw.ellipse(surface, (28, 29, 37), (x - w // 2, y - h // 2, w, h))
            pygame.draw.arc(surface, (93, 94, 105), (x - w // 2, y - h // 2, w, h),
                            0.1, math.pi - 0.1, 2)

        for x, y, scale in self.rocks:
            self._draw_rock(surface, x, y, scale)

        # A damaged lander in the distance gives the area a story.
        pygame.draw.ellipse(surface, (25, 27, 35), (77, 548, 104, 20))
        pygame.draw.polygon(surface, (82, 91, 101), [(98, 543), (113, 515),
                                                     (144, 512), (162, 543)])
        pygame.draw.polygon(surface, (45, 54, 66), [(113, 515), (128, 505),
                                                     (144, 512), (139, 536)])
        pygame.draw.line(surface, (117, 125, 132), (105, 541), (88, 559), 3)
        pygame.draw.line(surface, (117, 125, 132), (151, 540), (170, 557), 3)
        pygame.draw.circle(surface, (255, 107, 61), (132, 529), 3)

    def _draw_rock(self, surface, x, y, scale):
        points = [
            (x - 23 * scale, y), (x - 19 * scale, y - 13 * scale),
            (x - 7 * scale, y - 23 * scale), (x + 8 * scale, y - 20 * scale),
            (x + 21 * scale, y - 8 * scale), (x + 24 * scale, y),
        ]
        points = [(int(px), int(py)) for px, py in points]
        shadow = [(px + 5, py + 5) for px, py in points]
        pygame.draw.polygon(surface, (28, 29, 36), shadow)
        pygame.draw.polygon(surface, (86, 88, 99), points)
        pygame.draw.polygon(surface, (118, 120, 130), points[:4])
        pygame.draw.line(surface, (139, 141, 150), points[2], points[3], 2)

    def _draw_alien(self, surface, alien):
        x, y = int(alien["x"]), int(alien["y"])
        r = alien["radius"]
        bob = math.sin(alien["phase"]) * 2.5
        y = int(y + bob)
        body = (91, 203, 127) if not alien["heavy"] else (179, 132, 77)
        dark = (30, 83, 67) if not alien["heavy"] else (92, 58, 40)
        highlight = (156, 247, 170) if not alien["heavy"] else (242, 194, 118)

        # Ground shadow.
        pygame.draw.ellipse(surface, (23, 25, 32), (x - r - 7, y + r - 1, 2 * r + 14, 8))
        # Legs and arms.
        leg_sway = int(math.sin(alien["phase"] * 1.5) * 3)
        pygame.draw.line(surface, dark, (x - 5, y + 9), (x - 9 + leg_sway, y + r + 8), 5)
        pygame.draw.line(surface, dark, (x + 5, y + 9), (x + 10 - leg_sway, y + r + 8), 5)
        pygame.draw.line(surface, body, (x - r + 2, y + 1), (x - r - 7, y + 11), 5)
        pygame.draw.line(surface, body, (x + r - 2, y + 1), (x + r + 7, y + 10), 5)

        # Spines / silhouette.
        spikes = [(x - 11, y - 7), (x - 8, y - 18), (x - 1, y - 10),
                  (x + 5, y - 20), (x + 9, y - 8)]
        pygame.draw.polygon(surface, dark, [(x - r, y + 3), *spikes, (x + r, y + 4)])
        pygame.draw.ellipse(surface, dark, (x - r, y - r + 1, 2 * r, 2 * r + 5))
        pygame.draw.ellipse(surface, body, (x - r + 3, y - r + 3, 2 * r - 6, 2 * r - 3))
        pygame.draw.arc(surface, highlight, (x - r + 4, y - r + 3, 2 * r - 8, 2 * r - 5),
                        3.5, 5.6, 2)

        # Bright eyes look toward the astronaut.
        eye_dir = 1 if self.player_x >= x else -1
        pygame.draw.ellipse(surface, (255, 65, 77), (x - 9 + eye_dir, y - 4, 7, 8))
        pygame.draw.ellipse(surface, (255, 65, 77), (x + 2 + eye_dir, y - 4, 7, 8))
        pygame.draw.circle(surface, (255, 225, 205), (x - 6 + eye_dir, y - 1), 2)
        pygame.draw.circle(surface, (255, 225, 205), (x + 5 + eye_dir, y - 1), 2)
        pygame.draw.arc(surface, dark, (x - 6, y + 3, 12, 7), 0.1, math.pi - 0.1, 2)

        if alien["hp"] > 1:
            bar_w = 36
            pygame.draw.rect(surface, (35, 35, 42), (x - bar_w // 2, y - r - 11, bar_w, 4))
            pygame.draw.rect(surface, (246, 183, 89),
                             (x - bar_w // 2, y - r - 11, bar_w * alien["hp"] / alien["max_hp"], 4))
        if alien["flash"] > 0:
            pygame.draw.circle(surface, (230, 255, 255), (x, y), r + 5, 2)

    def _draw_astronaut(self, surface):
        x, y = int(self.player_x), int(self.player_y)
        moving = pygame.key.get_pressed()
        is_moving = any(moving[k] for k in (
            pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
            pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
        ))
        stride = math.sin(self.walk_time) * 5 if is_moving else 0
        bob = abs(math.sin(self.walk_time)) * 2 if is_moving else 0
        y = int(y - bob)
        direction = self.facing

        # Shadow.
        pygame.draw.ellipse(surface, (23, 24, 31), (x - 23, y + 24, 47, 12))
        # Legs and boots.
        pygame.draw.line(surface, (91, 103, 116), (x - 7, y + 10),
                         (x - 10 + stride, y + 29), 8)
        pygame.draw.line(surface, (91, 103, 116), (x + 7, y + 10),
                         (x + 10 - stride, y + 29), 8)
        pygame.draw.ellipse(surface, (35, 42, 53), (x - 19 + stride, y + 23, 17, 9))
        pygame.draw.ellipse(surface, (35, 42, 53), (x + 3 - stride, y + 23, 17, 9))

        # Backpack.
        pack_x = x - 20 if direction > 0 else x + 7
        pygame.draw.rect(surface, (96, 111, 126), (pack_x, y - 18, 14, 27), border_radius=4)
        pygame.draw.rect(surface, (45, 58, 73), (pack_x + 3, y - 13, 8, 16), border_radius=2)
        pygame.draw.circle(surface, (84, 224, 255), (pack_x + 7, y - 7), 2)

        # Torso, arm and chest control panel.
        pygame.draw.roundrect if hasattr(pygame.draw, "roundrect") else None
        pygame.draw.rect(surface, (196, 205, 211), (x - 13, y - 17, 26, 31), border_radius=7)
        pygame.draw.rect(surface, (115, 130, 144), (x - 9, y - 11, 18, 13), border_radius=3)
        pygame.draw.circle(surface, (88, 232, 255), (x, y - 5), 3)
        arm_y = y - 8
        pygame.draw.line(surface, (200, 207, 213), (x - 10, arm_y), (x - 18, arm_y + 11), 7)
        pygame.draw.line(surface, (200, 207, 213), (x + 10, arm_y), (x + 19, arm_y + 7), 7)
        pygame.draw.circle(surface, (73, 87, 101), (x - 19, arm_y + 12), 5)
        pygame.draw.circle(surface, (73, 87, 101), (x + 20, arm_y + 8), 5)

        # Helmet with reflective visor.
        pygame.draw.circle(surface, (118, 136, 153), (x, y - 27), 17)
        pygame.draw.circle(surface, (221, 229, 233), (x, y - 28), 14)
        visor_x = x + 3 * direction
        pygame.draw.ellipse(surface, (26, 59, 81), (visor_x - 10, y - 36, 19, 15))
        pygame.draw.arc(surface, (126, 227, 246), (visor_x - 9, y - 36, 17, 14),
                        3.5, 5.9, 2)
        pygame.draw.circle(surface, (240, 251, 255), (visor_x - 3, y - 32), 2)

    def _draw_particles(self, surface):
        for particle in self.particles:
            ratio = max(0.0, particle["life"] / particle["max_life"])
            color = tuple(int(c * ratio) for c in particle["color"])
            radius = max(1, int(particle["size"] * ratio))
            pygame.draw.circle(surface, color,
                               (int(particle["x"]), int(particle["y"])), radius)

    def _draw_hud(self, surface):
        # Dark glass-like header panel.
        panel = pygame.Surface((self.WIDTH, 82), pygame.SRCALPHA)
        panel.fill((4, 9, 20, 218))
        surface.blit(panel, (0, 0))
        pygame.draw.line(surface, (42, 113, 145), (0, 81), (self.WIDTH, 81), 2)

        title = self.font_title.render("E C L I P S E  //  LUNAR SURVIVAL", True, (205, 235, 247))
        surface.blit(title, (24, 14))
        subtitle = self.font_small.render("MISSION 02  •  LANDING ZONE SECURITY", True, (109, 177, 202))
        surface.blit(subtitle, (26, 49))

        health_label = self.font_small.render("SUIT INTEGRITY", True, (185, 207, 219))
        surface.blit(health_label, (530, 16))
        bar_x, bar_y, bar_w, bar_h = 530, 42, 225, 14
        pygame.draw.rect(surface, (34, 43, 55), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * self.player_health / 100)
        if self.player_health > 55:
            health_color = (72, 219, 156)
        elif self.player_health > 25:
            health_color = (245, 183, 81)
        else:
            health_color = (255, 81, 86)
        if fill_w > 0:
            pygame.draw.rect(surface, health_color, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        health_text = self.font_small.render(f"{int(self.player_health):03d}%", True, (235, 244, 248))
        surface.blit(health_text, (bar_x + bar_w + 10, bar_y - 3))

        kills_text = self.font_medium.render(f"HOSTILES  {self.kills:02d}", True, (133, 245, 180))
        surface.blit(kills_text, (875, 20))
        objective = self.font_small.render("OBJECTIVE: SURVIVE THE ALIEN ATTACK", True, (218, 220, 226))
        surface.blit(objective, (24, 94))

        controls = self.font_small.render("MOVE  WASD/ARROWS     FIRE  CLICK / SPACE     PAUSE  P",
                                          True, (151, 165, 180))
        surface.blit(controls, (self.WIDTH - controls.get_width() - 22, self.HEIGHT - 31))

        # A restrained targeting reticle around the nearest hostile.
        if self.aliens:
            target = min(self.aliens, key=lambda a: math.hypot(
                a["x"] - self.player_x, a["y"] - self.player_y
            ))
            tx, ty = int(target["x"]), int(target["y"])
            pygame.draw.circle(surface, (110, 225, 255), (tx, ty), target["radius"] + 11, 1)
            pygame.draw.line(surface, (110, 225, 255), (tx - 22, ty), (tx - 15, ty), 1)
            pygame.draw.line(surface, (110, 225, 255), (tx + 15, ty), (tx + 22, ty), 1)
            pygame.draw.line(surface, (110, 225, 255), (tx, ty - 22), (tx, ty - 15), 1)
            pygame.draw.line(surface, (110, 225, 255), (tx, ty + 15), (tx, ty + 22), 1)

    def _draw_mission_message(self, surface):
        text = self.font_medium.render("CONTACT!  Hostiles approaching the landing zone.",
                                       True, (236, 226, 188))
        plate = pygame.Surface((text.get_width() + 28, 42), pygame.SRCALPHA)
        plate.fill((5, 10, 20, 190))
        px = (self.WIDTH - plate.get_width()) // 2
        surface.blit(plate, (px, 112))
        surface.blit(text, (px + 14, 121))

    def _draw_center_panel(self, surface, heading, detail):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((1, 3, 12, 175))
        surface.blit(overlay, (0, 0))
        title = self.font_large.render(heading, True, (220, 239, 248))
        subtitle = self.font_medium.render(detail, True, (165, 202, 220))
        surface.blit(title, title.get_rect(center=(self.WIDTH // 2, 305)))
        surface.blit(subtitle, subtitle.get_rect(center=(self.WIDTH // 2, 365)))

    def run(self):
        # Standalone mode. When embedded in another game, its game loop can call
        # handle_event(), update(), and draw() directly instead.
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
            pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((1100, 700))
    pygame.display.set_caption("ECLIPSE - Level 2: Lunar Survival")
    level = Level2(screen)
    level.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
