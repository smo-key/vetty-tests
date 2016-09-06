import pygame
import os
import time
import pygame.freetype as freetype
import pygame.font as font
from time import strftime

GAMMA = 2
COLOR_BLUE900 = pygame.Color(13,71,161).correct_gamma(GAMMA)
COLOR_WHITE = pygame.Color(255,255,255)
COLOR_BLACK = pygame.Color(0,0,0)
COLOR_BG = COLOR_BLACK

#Initialization
os.putenv('SDL_FBDEV', '/dev/fb0')
pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((480, 320))

myimage = pygame.image.load("/home/pi/vetty/boot.png").convert()
imagerect = myimage.get_rect()
lcd.blit(myimage, imagerect)
pygame.display.update()
time.sleep(60)
