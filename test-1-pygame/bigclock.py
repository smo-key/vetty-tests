import pygame
import os
import time
import pygame.freetype as freetype
import pygame.font as font
import time
from time import strftime

GAMMA = 2
COLOR_BLUE900 = pygame.Color(13,71,161).correct_gamma(GAMMA)
COLOR_WHITE = pygame.Color(255,255,255)
COLOR_BLACK = pygame.Color(0,0,0)
COLOR_BG = COLOR_BLACK

#Initialization
os.putenv('SDL_FBDEV', '/dev/fb0')
pygame.init()

#LCD Fill test
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((480, 320))

#Font drawing
SURFACE = pygame.display.get_surface()
FONT_LT = freetype.Font("../fonts/HelveticaNeueLTStd-Lt.otf", size=64);
FONT_ICONS = freetype.Font("../fonts/materialdesignicons-webfont.ttf", size=64, ucs4=True);

def clearScreen(color):
	global COLOR_BG
	COLOR_BG = color
	lcd.fill(COLOR_BG)

def updateTimeBottom():
	#Get current time
	str_time = FONT_LT.render(strftime("%I:%M"), fgcolor=COLOR_WHITE, size=80);
	str_time[1].center = (240, 160)
	str_form = FONT_LT.render(strftime("%p"), fgcolor=COLOR_WHITE, size=50)
	str_form[1].center = (240, 160)
	str_form[1].bottom = str_time[1].bottom
	str_time_width = str_time[1].width + str_form[1].width
	str_time_center = str_time_width/2
	str_time[1].centerx += (str_time_center - str_time[1].centerx)/2 + 12
	str_form[1].centerx -= (str_time_center - str_form[1].centerx)/2 - 40
	
	#Clear part of screen
	blit_clear = pygame.Rect(str_time[1].left - 8, str_time[1].top - 1,
	 str_time_width + 32, str_time[1].height + 2)

	lcd.fill(COLOR_BG, blit_clear)
	lcd.blit(str_time[0], str_time[1])
	lcd.blit(str_form[0], str_form[1])

def drawBigIcon(string):
	#Draw fingerprint image
	str_icon = FONT_ICONS.render(string,fgcolor=COLOR_WHITE, size=140)
	str_icon[1].center = (240, 120)
	lcd.blit(str_icon[0], str_icon[1])

def update():
	pygame.display.update()

clearScreen(COLOR_BLUE900)

while True:
	updateTimeBottom()
	update()
	time.sleep(1)
	
