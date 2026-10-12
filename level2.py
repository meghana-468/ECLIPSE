"""Level 2 controller. Import Level2 and call run(screen) from another level."""
import math, random
import pygame
import settings as S
from entities import Player, Obstacle, OxygenTank, RocketPart, draw_astronaut
from puzzle import Puzzle
from ui import HUD, Button, TouchControls

INTRO, PLAYING, PUZZLE, COMPLETE, GAME_OVER, PAUSED = "INTRO", "PLAYING", "PUZZLE", "COMPLETE", "GAME_OVER", "PAUSED"


def start_level3():
    """Placeholder: replace this with your Level 3 transition later."""
    print("Level 3 hook called. Add your Level 3 scene here!")

class Level2:
    def __init__(self):
        pygame.font.init()
        self.font_small=pygame.font.SysFont("arial",18,bold=True); self.font=pygame.font.SysFont("arial",25,bold=True)
        self.font_big=pygame.font.SysFont("arial",54,bold=True)
        self.hud=HUD(); self.puzzle=Puzzle(); self.touch=TouchControls()
        self.restart_btn=Button((S.WIDTH//2-140,420,280,54),"PLAY AGAIN")
        self.continue_btn=Button((S.WIDTH//2-215,430,205,56),"CONTINUE TO LEVEL 3")
        self.quit_btn=Button((S.WIDTH//2+10,430,205,56),"QUIT GAME")
        self.resume_btn=Button((S.WIDTH//2-130,340,260,52),"RESUME")
        self.pause_restart_btn=Button((S.WIDTH//2-130,405,260,52),"RESTART LEVEL")
        self.muted=False; self._make_background(); self.reset()

    def _make_background(self):
        rng=random.Random(42)
        self.stars=[(rng.randrange(S.WIDTH),rng.randrange(15,S.GROUND_Y-90),rng.choice((1,1,2)),rng.uniform(.25,1)) for _ in range(180)]
        self.far_hills=[(x,rng.randint(60,135),rng.randint(130,280)) for x in range(-100,2400,210)]
        self.near_hills=[(x,rng.randint(35,85),rng.randint(110,230)) for x in range(-100,2500,170)]
        self.earth=(82,105,42)

    def reset(self):
        self.state=INTRO; self.state_time=0.0; self.elapsed=0.0; self.oxygen=S.OXYGEN_MAX
        self.player=Player(); self.camera_x=0.0; self.score=0; self.parts_found=set(); self.obstacles=[]; self.tanks=[]; self.parts=[]; self.dust=[]
        self.next_obstacle=440; self.next_tank=360; self.next_part=680; self.part_index=0
        self.rocket_x=S.WORLD_LENGTH-250; self.death_time=0.0; self.puzzle=Puzzle(); self._spawn_initial_ahead()

    def _spawn_initial_ahead(self):
        # One early tank and one early component introduce the collection loop.
        self.tanks.append(OxygenTank(390,S.GROUND_Y-105))
        self.parts.append(RocketPart(S.PART_NAMES[0],700,S.GROUND_Y-72))
        self.part_index=1; self.next_part=700+random.randint(*S.PART_SPACING_MIN if False else (S.PART_SPACING_MIN,S.PART_SPACING_MAX))

    def _speed(self):
        time_bonus=min(S.MAX_SPEED_BONUS,self.elapsed*2.0)
        return S.PLAYER_SPEED+time_bonus+len(self.parts_found)*18

    def _spawn_ahead(self):
        # Always spawn ahead of the camera/player; tank placement is not tied to obstacle placement.
        while self.next_obstacle < self.player.x+S.WIDTH*1.8 and self.next_obstacle < self.rocket_x-300:
            progress=self.player.x/S.WORLD_LENGTH
            gap=random.randint(*((S.OBSTACLE_LATER_MIN,S.OBSTACLE_LATER_MAX) if progress>.4 else (S.OBSTACLE_FIRST_MIN,S.OBSTACLE_FIRST_MAX)))
            self.obstacles.append(Obstacle(self.next_obstacle))
            self.next_obstacle += gap
        while self.next_tank < self.player.x+S.WIDTH*2.0 and self.next_tank < self.rocket_x-180:
            # Tanks are placed in reachable ground/low-air lanes and never too far apart.
            y=random.choice((S.GROUND_Y-74,S.GROUND_Y-105))
            self.tanks.append(OxygenTank(self.next_tank,y))
            self.next_tank += random.randint(*S.TANK_SPACING_MIN if False else (S.TANK_SPACING_MIN,S.TANK_SPACING_MAX))
        while self.next_part < self.player.x+S.WIDTH*1.8 and self.part_index<len(S.PART_NAMES):
            name=S.PART_NAMES[self.part_index]
            self.parts.append(RocketPart(name,self.next_part,S.GROUND_Y-76))
            self.part_index+=1; self.next_part+=random.randint(S.PART_SPACING_MIN,S.PART_SPACING_MAX)
        # Make sure remaining parts can appear before the rocket, even on unusual random rolls.
        if self.part_index<len(S.PART_NAMES) and self.next_part>self.rocket_x-500:
            name=S.PART_NAMES[self.part_index]; self.parts.append(RocketPart(name,self.rocket_x-350,S.GROUND_Y-75)); self.part_index+=1

    def run(self,screen):
        """Run until completion or quit; game over stays open so the player can retry."""
        clock=pygame.time.Clock(); result="quit"; running=True
        self.exit_requested=None
        while running:
            dt=min(clock.tick(S.FPS)/1000.0,0.05)
            for event in pygame.event.get():
                if event.type==pygame.QUIT: return "quit"
                self._event(event)
                if self.exit_requested is not None:
                    result=self.exit_requested
                    running=False
                    break
            if not running:
                break
            self.update(dt)
            self.draw(screen)
            pygame.display.flip()
        return result

    def _event(self,event):
        if self.state==PUZZLE:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            self.puzzle.handle_event(event); return
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_m: self.muted=not self.muted
            if event.key==pygame.K_ESCAPE:
                if self.state==PLAYING:self.state=PAUSED
                elif self.state==PAUSED:self.state=PLAYING
            elif self.state==INTRO and event.key in (pygame.K_SPACE,pygame.K_RETURN): self.state=PLAYING; self.state_time=0
            elif self.state==GAME_OVER and event.key==pygame.K_r:
                self.reset(); self.state=PLAYING; self.state_time=0
            elif self.state==COMPLETE and event.key in (pygame.K_SPACE,pygame.K_RETURN):
                start_level3()
                self.exit_requested="continue"
            elif self.state==COMPLETE and event.key==pygame.K_ESCAPE:
                self.exit_requested="quit"
            elif self.state==PLAYING and event.key in (pygame.K_SPACE,pygame.K_UP,pygame.K_w):self.player.jump()
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            pos=event.pos
            if self.state==INTRO:self.state=PLAYING; self.state_time=0
            elif self.state==GAME_OVER and self.restart_btn.hit(pos):
                self.reset(); self.state=PLAYING; self.state_time=0
            elif self.state==COMPLETE:
                if self.continue_btn.hit(pos):
                    start_level3()
                    self.exit_requested="continue"
                elif self.quit_btn.hit(pos):
                    self.exit_requested="quit"
            elif self.state==PAUSED:
                if self.resume_btn.hit(pos):self.state=PLAYING
                elif self.pause_restart_btn.hit(pos):self.reset()
            elif self.state==PLAYING:
                self.touch.layout(S.WIDTH,S.HEIGHT)
                if self.touch.jump_btn.hit(pos):self.player.jump()

    def update(self,dt):
        self.state_time+=dt
        if self.state==INTRO:return
        if self.state==PUZZLE:
            self.puzzle.update(dt)
            if self.puzzle.solved:
                self.state=COMPLETE; self.state_time=0
            return
        if self.state==PAUSED or self.state in (COMPLETE,GAME_OVER):
            if self.state==GAME_OVER:self.death_time+=dt
            return
        if self.state!=PLAYING:return
        self.elapsed+=dt
        self.oxygen=max(0,self.oxygen-S.OXYGEN_DRAIN*dt)
        if self.oxygen<=0:
            self.state=GAME_OVER; self.death_time=0; self.player.falling=True; self.state_time=0; return
        keys=pygame.key.get_pressed(); speed=self._speed()
        # Mouse buttons can be held for continuous movement.
        mouse=pygame.mouse.get_pos(); self.touch.layout(S.WIDTH,S.HEIGHT)
        direction=(1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0)-(1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        if pygame.mouse.get_pressed()[0]:direction=self.touch.direction(mouse) or direction
        self.player.x=min(self.rocket_x-70,self.player.x+direction*speed*dt)
        previous_x=self.player.x
        self.player.update(dt,0,self.rocket_x)
        # Player.update's forward movement is disabled above; manual direction preserves stopping/backtracking.
        self.player.x=previous_x
        self._spawn_ahead()
        for ob in self.obstacles:ob.update(dt)
        for tank in self.tanks:tank.update(dt)
        for part in self.parts:part.update(dt)
        # Obstacle collisions only count while the astronaut is near ground level.
        for ob in self.obstacles:
            if self.player.rect.colliderect(ob.rect) and self.player.hit_timer<=0 and self.player.on_ground:
                self.oxygen=max(0,self.oxygen-S.OBSTACLE_DAMAGE); self.player.hit_timer=1.0
                self.player.vy=-S.JUMP_FORCE*.48; self.player.on_ground=False; self.player.jumps_left=max(0,self.player.jumps_left-1)
                self.score=max(0,self.score-15)
        for tank in self.tanks:
            if not tank.collected and self.player.rect.colliderect(tank.rect):
                tank.collected=True; self.oxygen=min(S.OXYGEN_MAX,self.oxygen+S.TANK_REFILL); self.score+=100
        for part in self.parts:
            if not part.collected and self.player.rect.colliderect(part.rect):
                part.collected=True; self.parts_found.add(part.name); self.score+=250
        # Remove old objects to keep memory bounded.
        self.obstacles=[o for o in self.obstacles if o.rect.right>self.camera_x-120]
        self.tanks=[t for t in self.tanks if not t.collected and t.x>self.camera_x-120]
        self.parts=[p for p in self.parts if not p.collected and p.x>self.camera_x-120]
        self.camera_x=max(0,min(self.player.x-S.WIDTH*.30,S.WORLD_LENGTH-S.WIDTH))
        if self.player.x>=self.rocket_x-85 and len(self.parts_found)==5:
            self.state=PUZZLE; self.state_time=0; self.puzzle.reset()
        elif self.player.x>=self.rocket_x-85 and len(self.parts_found)<5:
            # The player cannot enter the puzzle until all components are recovered.
            self.player.x=self.rocket_x-86

    def draw(self,screen):
        if self.state==PUZZLE:
            self.puzzle.draw(screen,self.font_small,self.font); return
        self._draw_world(screen)
        mouse=pygame.mouse.get_pos()
        if self.state in (PLAYING,PAUSED,GAME_OVER):
            self.hud.draw(screen,self.oxygen,len(self.parts_found),self.player.x,S.WORLD_LENGTH,self.score,self.elapsed)
            if self.state==PLAYING:self.touch.draw(screen,mouse)
        if self.state==INTRO:self._overlay(screen,"LUNAR SURVIVAL","Find the Mars rocket. Collect broken parts. Stay alive.","Press SPACE or click to begin")
        elif self.state==PAUSED:
            self._dim(screen); self._center_text(screen,"PAUSED",230,self.font_big,S.CYAN)
            self.resume_btn.draw(screen,self.font,mouse); self.pause_restart_btn.draw(screen,self.font,mouse)
        elif self.state==GAME_OVER:
            self._dim(screen); self._center_text(screen,"GAME OVER",250,self.font_big,S.RED); self._center_text(screen,"Oxygen depleted",315,self.font,S.WHITE)
            self._center_text(screen,f"Score: {self.score}",365,self.font,S.GOLD); self.restart_btn.draw(screen,self.font,mouse)
            self._center_text(screen,"Click PLAY AGAIN or press R to try again",490,self.font_small,S.WHITE)
        elif self.state==COMPLETE:
            self._dim(screen)
            panel=pygame.Rect(S.WIDTH//2-300,190,600,340)
            pygame.draw.rect(screen,(13,22,39),panel,border_radius=22)
            pygame.draw.rect(screen,S.CYAN,panel,2,border_radius=22)
            self._center_text(screen,"LEVEL 2 COMPLETED!",245,self.font_big,S.GREEN)
            self._center_text(screen,"Moon mission successful!",305,self.font,S.WHITE)
            self._center_text(screen,"Your rocket parts are assembled.",342,self.font_small,S.MOON_LIGHT)
            self._center_text(screen,f"FINAL SCORE: {self.score}",385,self.font,S.GOLD)
            self.continue_btn.draw(screen,self.font_small,mouse)
            self.quit_btn.draw(screen,self.font,mouse)
            self._center_text(screen,"Choose what you want to do next",510,self.font_small,S.MOON_LIGHT)

    def _draw_world(self,screen):
        w,h=screen.get_size(); screen.fill(S.BLACK)
        # Parallax star field
        for x,y,r,depth in self.stars:
            sx=int((x-self.camera_x*depth*.08)%w); pygame.draw.circle(screen,(100,110,137),(sx,y),r)
        # Blue Earth in the sky
        ex=int(80-self.camera_x*.025); pygame.draw.circle(screen,(38,104,207),(ex,102),39); pygame.draw.arc(screen,(115,190,255),(ex-39,63,78,78),.2,4.8,3)
        pygame.draw.ellipse(screen,(62,169,110),(ex-24,79,18,11)); pygame.draw.ellipse(screen,(62,169,110),(ex+2,98,21,15))
        # Parallax mountains/hills
        for x,height,width in self.far_hills:
            sx=int(x-self.camera_x*.22)
            if -width<sx<w:pygame.draw.polygon(screen,(54,57,70),[(sx,S.GROUND_Y),(sx+width//2,S.GROUND_Y-height),(sx+width,S.GROUND_Y)])
        for x,height,width in self.near_hills:
            sx=int(x-self.camera_x*.42)
            if -width<sx<w:pygame.draw.ellipse(screen,(74,77,89),(sx,S.GROUND_Y-height//2,width,height))
        pygame.draw.rect(screen,(119,121,132),(0,S.GROUND_Y,w,h-S.GROUND_Y)); pygame.draw.line(screen,S.MOON_LIGHT,(0,S.GROUND_Y),(w,S.GROUND_Y),4)
        # Surface seams and small stones scroll with the world.
        for i in range(int(self.camera_x//130)-1,int((self.camera_x+w)//130)+2):
            x=int(i*130-self.camera_x); pygame.draw.line(screen,(98,100,112),(x,S.GROUND_Y+25),(x+40,S.GROUND_Y+25),2)
            pygame.draw.circle(screen,(91,93,105),(x+72,S.GROUND_Y+46),4)
        for ob in self.obstacles:ob.draw(screen,self.camera_x)
        for tank in self.tanks:tank.draw(screen,self.camera_x)
        for part in self.parts:part.draw(screen,self.camera_x)
        # Signpost appears after every part has been collected.
        if len(self.parts_found)==5:
            sx=int(self.rocket_x-230-self.camera_x)
            pygame.draw.line(screen,(75,78,88),(sx,S.GROUND_Y),(sx,S.GROUND_Y-90),6)
            pygame.draw.rect(screen,(32,100,123),(sx,S.GROUND_Y-90,150,36),border_radius=5)
            self._text(screen,"MARS ROCKET  →",(sx+8,S.GROUND_Y-83),S.WHITE,self.font_small)
        # Mars rocket at the world end
        rx=int(self.rocket_x-self.camera_x)
        if -180<rx<w+180:self._draw_rocket(screen,rx,S.GROUND_Y-5,damaged=len(self.parts_found)<5)
        self.player.draw(screen,self.camera_x)
        # Dust puffs when running/landing
        if self.player.on_ground and self.state==PLAYING and random.random()<.22:
            self.dust.append([self.player.x-10,self.player.y-3,random.uniform(-45,-10),random.uniform(-30,-5),.35])
        alive=[]
        for x,y,vx,vy,life in self.dust:
            x+=vx*(1/60); y+=vy*(1/60); life-=1/60
            if life>0:
                pygame.draw.circle(screen,(175,176,185),(int(x-self.camera_x),int(y)),max(1,int(life*10)));alive.append([x,y,vx,vy,life])
        self.dust=alive

    @staticmethod
    def _draw_rocket(surface,x,bottom,damaged):
        body=(125,139,158) if damaged else (205,218,233); accent=(214,95,82) if damaged else (74,210,150)
        pygame.draw.polygon(surface,body,[(x-30,bottom),(x-30,bottom-135),(x,bottom-185),(x+30,bottom-135),(x+30,bottom)])
        pygame.draw.polygon(surface,accent,[(x-30,bottom-35),(x-60,bottom),(x-30,bottom-5)])
        pygame.draw.polygon(surface,accent,[(x+30,bottom-35),(x+60,bottom),(x+30,bottom-5)])
        pygame.draw.ellipse(surface,(25,58,89),(x-14,bottom-125,28,29)); pygame.draw.ellipse(surface,(125,219,246),(x-14,bottom-125,28,29),2)
        if damaged:
            pygame.draw.line(surface,(255,93,85),(x-20,bottom-65),(x+20,bottom-45),5);pygame.draw.line(surface,(255,93,85),(x+18,bottom-75),(x-10,bottom-55),4)
        else:
            pygame.draw.polygon(surface,(255,167,58),[(x-15,bottom),(x+15,bottom),(x,bottom+40)])
            pygame.draw.polygon(surface,(255,235,120),[(x-7,bottom),(x+7,bottom),(x,bottom+25)])

    def _overlay(self,screen,title,subtitle,hint):
        self._dim(screen); self._center_text(screen,title,230,self.font_big,S.CYAN); self._center_text(screen,subtitle,310,self.font,S.WHITE); self._center_text(screen,hint,370,self.font_small,S.GOLD)
    @staticmethod
    def _dim(screen):
        layer=pygame.Surface(screen.get_size(),pygame.SRCALPHA);layer.fill((0,0,0,185));screen.blit(layer,(0,0))
    @staticmethod
    def _center_text(screen,text,y,font,color):
        img=font.render(text,True,color);screen.blit(img,img.get_rect(center=(screen.get_width()//2,y)))
    @staticmethod
    def _text(screen,text,pos,color,font):screen.blit(font.render(text,True,color),pos)
