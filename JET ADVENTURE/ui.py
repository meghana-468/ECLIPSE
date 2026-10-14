"""Heads-up display, buttons, and mouse controls."""
import pygame
import settings as S

class Button:
    def __init__(self,rect,label): self.rect=pygame.Rect(rect); self.label=label
    def hit(self,pos): return self.rect.collidepoint(pos)
    def draw(self,surface,font,mouse=None,enabled=True):
        hover=mouse is not None and self.hit(mouse)
        color=(35,105,145) if hover and enabled else ((25,61,87) if enabled else (45,48,58))
        pygame.draw.rect(surface,color,self.rect,border_radius=10)
        pygame.draw.rect(surface,S.CYAN if enabled else (90,95,105),self.rect,2,border_radius=10)
        img=font.render(self.label,True,S.WHITE if enabled else (145,145,155)); surface.blit(img,img.get_rect(center=self.rect.center))

class HUD:
    def __init__(self): self.font=pygame.font.SysFont("arial",20,bold=True); self.small=pygame.font.SysFont("arial",15,bold=True)
    def draw(self,surface,oxygen,parts,distance,world_length,score,elapsed):
        w,h=surface.get_size(); pygame.draw.rect(surface,(8,13,27),(12,10,420,95),border_radius=12); pygame.draw.rect(surface,(72,90,115),(12,10,420,95),2,border_radius=12)
        self._text(surface,"OXYGEN",(27,24),S.WHITE,self.small)
        bar=pygame.Rect(104,20,250,19); pygame.draw.rect(surface,(45,50,62),bar,border_radius=6)
        fill=bar.copy(); fill.width=int(bar.width*max(0,oxygen)/S.OXYGEN_MAX)
        color=S.RED if oxygen<25 else (70,220,155)
        pygame.draw.rect(surface,color,fill,border_radius=6)
        if oxygen<25 and int(elapsed*5)%2==0: pygame.draw.rect(surface,S.WHITE,bar,2,border_radius=6)
        self._text(surface,f"{int(max(0,oxygen))}%",(365,20),S.WHITE,self.small)
        self._text(surface,f"PARTS: {parts}/5",(27,53),S.GOLD,self.font); self._text(surface,f"SCORE: {score}",(205,56),S.WHITE,self.small)
        self._text(surface,"MARS ROCKET",(27,82),S.WHITE,self.small)
        p=max(0,min(1,distance/world_length)); pr=pygame.Rect(150,82,245,9); pygame.draw.rect(surface,(50,55,67),pr,border_radius=4); pygame.draw.rect(surface,S.CYAN,(pr.x,pr.y,int(pr.width*p),pr.height),border_radius=4)
        # Controls panel with key-like icons.
        panel=pygame.Rect(w-330,12,318,94); pygame.draw.rect(surface,(8,13,27),panel,border_radius=12); pygame.draw.rect(surface,(72,90,115),panel,2,border_radius=12)
        self._text(surface,"CONTROLS",(panel.x+14,panel.y+9),S.CYAN,self.small)
        self._key(surface,"← / A",panel.x+18,panel.y+34,57); self._key(surface,"→ / D",panel.x+83,panel.y+34,57); self._key(surface,"SPACE",panel.x+148,panel.y+34,66)
        self._text(surface,"Move       Move       Jump",(panel.x+17,panel.y+66),S.WHITE,self.small)
        self._text(surface,"ESC pause  •  M mute",(panel.x+174,panel.y+66),S.WHITE,self.small)
    @staticmethod
    def _text(surface,text,pos,color,font): surface.blit(font.render(text,True,color),pos)
    @staticmethod
    def _key(surface,label,x,y,width):
        r=pygame.Rect(x,y,width,25); pygame.draw.rect(surface,(42,54,72),r,border_radius=5); pygame.draw.rect(surface,(145,174,198),r,1,border_radius=5)
        f=pygame.font.SysFont("arial",12,bold=True); img=f.render(label,True,S.WHITE); surface.blit(img,img.get_rect(center=r.center))

class TouchControls:
    """Clickable on-screen controls. Holding a button keeps moving/jumping."""
    def __init__(self):
        self.left=Button((20,0,78,48),"◀ LEFT"); self.right=Button((106,0,84,48),"RIGHT ▶"); self.jump_btn=Button((0,0,100,48),"JUMP ↑")
    def layout(self,w,h):
        self.left.rect.topleft=(20,h-68); self.right.rect.topleft=(106,h-68); self.jump_btn.rect.topleft=(w-120,h-68)
    def draw(self,surface,mouse):
        for b in (self.left,self.right,self.jump_btn): b.draw(surface,pygame.font.SysFont("arial",15,bold=True),mouse)
    def direction(self,pos):
        if self.left.hit(pos):return -1
        if self.right.hit(pos):return 1
        return 0
