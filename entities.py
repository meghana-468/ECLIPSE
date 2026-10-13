"""Game objects drawn entirely with Pygame primitives."""
import math, random
import pygame
import settings as S
from settings import (
    BLACK,
    WHITE,
    CYAN,
    GOLD,
    RED,
    GREEN,
    DARK,
    PANEL,
    MOON,
    MOON_LIGHT,
    MOON_DARK,
)


def draw_astronaut(surface, x, feet_y, phase=0.0, jumping=False, falling=False):
    """Draw a simple animated astronaut; x and feet_y are world coordinates."""
    x, feet_y = int(x), int(feet_y)
    suit, shade, visor = (239, 241, 247), (160, 168, 184), (37, 91, 125)
    # Backpack and body
    pygame.draw.rect(surface, (135, 145, 161), (x-19, feet_y-54, 13, 29), border_radius=4)
    pygame.draw.rect(surface, suit, (x-10, feet_y-51, 22, 28), border_radius=7)
    pygame.draw.rect(surface, (115, 132, 150), (x-4, feet_y-46, 10, 8), border_radius=2)
    swing = 0 if jumping or falling else math.sin(phase) * 9
    # Arms and legs use alternating angles while running.
    pygame.draw.line(surface, shade, (x-7, feet_y-46), (x-14-swing*.35, feet_y-29), 6)
    pygame.draw.line(surface, suit, (x+8, feet_y-45), (x+14+swing*.35, feet_y-31), 6)
    pygame.draw.line(surface, shade, (x-3, feet_y-25), (x-7+swing, feet_y-11), 7)
    pygame.draw.line(surface, suit, (x+5, feet_y-25), (x+7-swing, feet_y-10), 7)
    pygame.draw.ellipse(surface, suit, (x-12, feet_y-69, 25, 25))
    pygame.draw.ellipse(surface, visor, (x-5, feet_y-63, 15, 13))
    pygame.draw.line(surface, (190, 236, 250), (x-2, feet_y-61), (x+3, feet_y-58), 2)
    if falling:
        pygame.draw.line(surface, GOLD, (x-15, feet_y-48), (x-27, feet_y-40), 3)


class Player:
    def __init__(self, x=S.PLAYER_START_X):
        self.x = float(x); self.y = float(S.GROUND_Y); self.vy = 0.0
        self.jumps_left = 2; self.phase = 0.0; self.on_ground = True
        self.hit_timer = 0.0; self.falling = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x-15), int(self.y-S.PLAYER_HEIGHT), 30, S.PLAYER_HEIGHT-3)

    def jump(self):
        if self.jumps_left > 0 and not self.falling:
            self.vy = -S.JUMP_FORCE if self.jumps_left == 2 else -S.JUMP_FORCE * 0.82
            self.jumps_left -= 1; self.on_ground = False

    def update(self, dt, speed, world_length):
        self.x = min(world_length-100, self.x + speed*dt)
        self.vy += S.GRAVITY*dt; self.y += self.vy*dt
        if self.y >= S.GROUND_Y:
            self.y = S.GROUND_Y; self.vy = 0; self.jumps_left = 2; self.on_ground = True
        else: self.on_ground = False
        self.phase += dt * (12 if self.on_ground else 4)
        self.hit_timer = max(0.0, self.hit_timer-dt)

    def draw(self, surface, camera_x):
        if self.hit_timer and int(self.hit_timer*18)%2 == 0: return
        draw_astronaut(surface, self.x-camera_x, self.y, self.phase, not self.on_ground, self.falling)


class Obstacle:
    def __init__(self, x, kind=None, size=None):
        self.x=float(x); self.kind=kind or random.choice(("rock", "crater", "boulder"))
        self.size=size or random.randint(34, 65); self.phase=random.random()*6.28
        self.y=S.GROUND_Y
        if self.kind == "crater": self.rect=pygame.Rect(int(x), S.GROUND_Y-13, self.size+28, 18)
        else: self.rect=pygame.Rect(int(x), S.GROUND_Y-self.size, self.size, self.size)

    def update(self, dt):
        self.phase += dt*3.0
        if self.kind == "boulder":
            self.rect.x = int(self.x + math.sin(self.phase)*18)

    def draw(self, surface, sx):
        r=self.rect.move(-int(sx),0)
        if self.kind == "crater":
            pygame.draw.ellipse(surface, (65,67,77), r)
            pygame.draw.arc(surface, (190,191,199), r, 0.1, math.pi-0.1, 3)
        elif self.kind == "boulder":
            pygame.draw.circle(surface, (102,104,116), r.center, max(8,r.width//2))
            pygame.draw.circle(surface, (166,168,178), (r.centerx-7,r.centery-8), max(3,r.width//7))
            pygame.draw.circle(surface, (65,67,77), r.center, max(8,r.width//2), 2)
        else:
            pts=[(r.left,r.bottom),(r.left+4,r.top+12),(r.left+r.width//3,r.top),(r.right-5,r.top+8),(r.right,r.bottom)]
            pygame.draw.polygon(surface,(105,108,120),pts); pygame.draw.lines(surface,(177,179,188),False,pts,2)


class OxygenTank:
    def __init__(self,x,y=None):
        self.x=float(x); self.y=float(y if y is not None else S.GROUND_Y-105); self.collected=False
        self.rect=pygame.Rect(int(x-13),int(self.y-19),26,38); self.pulse=random.random()*6.28
    def update(self,dt): self.pulse += dt*4
    def draw(self,surface,sx):
        if self.collected:return
        x=int(self.x-sx); y=int(self.y+math.sin(self.pulse)*3)
        pygame.draw.circle(surface,(30,115,145),(x,y),24,2)
        pygame.draw.rect(surface,(180,226,238),(x-10,y-16,20,32),border_radius=5)
        pygame.draw.rect(surface,(80,170,196),(x-6,y-10,12,20),border_radius=3)
        pygame.draw.rect(surface,WHITE,(x-5,y-21,10,6),border_radius=2)
        pygame.draw.line(surface,WHITE,(x,y-4),(x,y+7),3)
        pygame.draw.line(surface,WHITE,(x-5,y+1),(x+5,y+1),3)


class RocketPart:
    COLORS={"engine":(255,142,72),"fuel tank":(83,205,245),"wing":(255,211,95),"nose cone":(238,115,137),"control panel":(139,238,164)}
    def __init__(self,name,x,y=None):
        self.name=name; self.x=float(x); self.y=float(y if y is not None else S.GROUND_Y-72)
        self.collected=False; self.phase=random.random()*6.28
        self.rect=pygame.Rect(int(x-22),int(self.y-22),44,44)
        self.color=self.COLORS[name]
    def update(self,dt): self.phase += dt*3
    def draw(self,surface,sx):
        if self.collected:return
        x=int(self.x-sx); y=int(self.y+math.sin(self.phase)*4); c=self.color
        pygame.draw.circle(surface,c,(x,y),29,1)
        if self.name=="engine":
            pygame.draw.polygon(surface,c,[(x-16,y-13),(x+16,y-13),(x+11,y+7),(x+6,y+17),(x-6,y+17),(x-11,y+7)])
            pygame.draw.ellipse(surface,(255,230,170),(x-7,y+5,14,9))
        elif self.name=="fuel tank":
            pygame.draw.rect(surface,c,(x-10,y-19,20,38),border_radius=7)
            pygame.draw.line(surface,WHITE,(x-8,y-7),(x+8,y-7),2); pygame.draw.line(surface,WHITE,(x-8,y+7),(x+8,y+7),2)
        elif self.name=="wing":
            pygame.draw.polygon(surface,c,[(x-21,y+14),(x-5,y-17),(x+5,y-17),(x+20,y+14),(x+4,y+8),(x-4,y+8)])
        elif self.name=="nose cone":
            pygame.draw.polygon(surface,c,[(x,y-21),(x+15,y+12),(x,y+18),(x-15,y+12)])
        else:
            pygame.draw.rect(surface,c,(x-19,y-14,38,28),border_radius=4)
            pygame.draw.rect(surface,(38,55,72),(x-12,y-8,24,16),border_radius=2)
            pygame.draw.circle(surface,GOLD,(x+13,y-9),3)
