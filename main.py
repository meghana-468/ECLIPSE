import pygame
from levels.level2 import run_level2

pygame.init()

WIDTH = 1000
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Jet Adventure - ECLIPSE")

clock = pygame.time.Clock()

result = run_level2(screen, clock)

pygame.quit()


