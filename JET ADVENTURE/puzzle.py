"""Drag-and-drop repair puzzle. The puzzle only opens after all five parts are found."""
import pygame
import settings as S
from entities import RocketPart

SLOT_ORDER = list(S.PART_NAMES)

class Puzzle:
    def __init__(self):
        self.reset()
    def reset(self):
        self.placed=set(); self.dragging=None; self.drag_pos=(0,0); self.shakes={}; self.message="Drag each part into its matching outline."
        self.slots={name:pygame.Rect(0,0,0,0) for name in SLOT_ORDER}
        self.part_rects={name:pygame.Rect(0,0,0,0) for name in SLOT_ORDER}
    @property
    def solved(self): return len(self.placed)==len(SLOT_ORDER)
    def _layout(self):
        # Positions are recalculated each frame so any supported window size works.
        return
    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            pos=event.pos
            for name in SLOT_ORDER:
                if name not in self.placed and self.part_rects[name].collidepoint(pos):
                    self.dragging=name; self.drag_pos=pos; return
        elif event.type==pygame.MOUSEMOTION and self.dragging:
            self.drag_pos=event.pos
        elif event.type==pygame.MOUSEBUTTONUP and event.button==1 and self.dragging:
            name=self.dragging; slot=self.slots[name]
            if slot.inflate(20,20).collidepoint(event.pos):
                self.placed.add(name); self.message=f"{name.title()} secured!"
            else:
                self.shakes[name]=0.35; self.message="Wrong slot! The part snapped back. Match the shapes."
            self.dragging=None
    def update(self,dt):
        for name in list(self.shakes):
            self.shakes[name]-=dt
            if self.shakes[name]<=0: del self.shakes[name]
    def draw(self,surface,font_small,font_medium):
        w,h=surface.get_size(); surface.fill((5,8,20))
        # Stars and the damaged rocket silhouette
        for i in range(75):
            x=(i*137+23)%w; y=(i*79+17)%(h//2)
            pygame.draw.circle(surface,(100+(i%5)*25,110+(i%5)*25,135+(i%5)*22),(x,y),1+(i%3==0))
        title=font_medium.render("MARS ROCKET REPAIR",True,S.CYAN); surface.blit(title,title.get_rect(center=(w//2,48)))
        help_img=font_small.render("Drag each recovered component into the matching glowing outline",True,S.WHITE); surface.blit(help_img,help_img.get_rect(center=(w//2,83)))
        # Main rocket outline is a silhouette, slots are distinct shapes.
        cx,cy=w//2, h//2+5
        pygame.draw.polygon(surface,(35,48,68),[(cx-45,cy+120),(cx-45,cy-90),(cx,cy-165),(cx+45,cy-90),(cx+45,cy+120)])
        pygame.draw.polygon(surface,(130,150,177),[(cx-45,cy+120),(cx-45,cy-90),(cx,cy-165),(cx+45,cy-90),(cx+45,cy+120)],3)
        pygame.draw.polygon(surface,(50,70,95),[(cx-45,cy+60),(cx-95,cy+115),(cx-45,cy+105)])
        pygame.draw.polygon(surface,(50,70,95),[(cx+45,cy+60),(cx+95,cy+115),(cx+45,cy+105)])
        # Slot layout around rocket
        self.slots={
          "nose cone":pygame.Rect(cx-29,cy-148,58,48),
          "fuel tank":pygame.Rect(cx-26,cy-86,52,90),
          "control panel":pygame.Rect(cx-26,cy+15,52,37),
          "engine":pygame.Rect(cx-28,cy+77,56,38),
          "wing":pygame.Rect(cx+52,cy+61,60,48)}
        for name,rect in self.slots.items():
            color=RocketPart.COLORS[name]
            pygame.draw.rect(surface,(22,32,49),rect,border_radius=7)
            pygame.draw.rect(surface,color if name in self.placed else (90,110,132),rect,3,border_radius=7)
            if name in self.placed:
                self._draw_shape(surface,name,rect.center,color)
            else:
                label=font_small.render(name.upper(),True,S.WHITE)
                surface.blit(label,label.get_rect(center=(rect.centerx,rect.bottom+15)))
        # Recovered pieces sit in a tray along the bottom; the dragged one follows the mouse.
        tray_y=h-100; gap=w//6
        for i,name in enumerate(SLOT_ORDER):
            if name in self.placed: continue
            r=pygame.Rect(gap*(i+1)-27,tray_y-24,54,48); self.part_rects[name]=r
            if name in self.shakes: r.x+=int(7*((int(self.shakes[name]*60)%2)*2-1))
            if self.dragging==name:
                r.center=self.drag_pos
            self._draw_shape(surface,name,r.center,RocketPart.COLORS[name])
            pygame.draw.circle(surface,RocketPart.COLORS[name],r.center,31,1)
            label=font_small.render(name.title(),True,S.WHITE); surface.blit(label,label.get_rect(center=(r.centerx,tray_y+38)))
        msg=font_small.render(self.message,True,S.GOLD if "Wrong" in self.message else S.WHITE)
        surface.blit(msg,msg.get_rect(center=(w//2,h-25)))
    @staticmethod
    def _draw_shape(surface,name,center,color):
        x,y=center
        if name=="engine": pygame.draw.polygon(surface,color,[(x-20,y-15),(x+20,y-15),(x+13,y+8),(x+7,y+18),(x-7,y+18),(x-13,y+8)])
        elif name=="fuel tank": pygame.draw.rect(surface,color,(x-13,y-22,26,44),border_radius=8)
        elif name=="wing": pygame.draw.polygon(surface,color,[(x-26,y+16),(x-6,y-19),(x+6,y-19),(x+26,y+16),(x+4,y+8),(x-4,y+8)])
        elif name=="nose cone": pygame.draw.polygon(surface,color,[(x,y-24),(x+20,y+18),(x,y+12),(x-20,y+18)])
        else:
            pygame.draw.rect(surface,color,(x-23,y-17,46,34),border_radius=4); pygame.draw.rect(surface,(35,48,66),(x-14,y-9,28,18),border_radius=2)
