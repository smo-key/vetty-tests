import pygame
import os
import time
import pygame.freetype as freetype
import pygame.font as font
from pygame.locals import *
import time
from time import strftime
import threading
import sys
import traceback
import math
from PyTouch import pytouch
from PyTouch.pytouch import TouchThread as TouchThread

#from signal import alarm, signal, SIGALRM, SIGKILL
#
#def alarm_handler(signum, frame):
#        pygame.quit()
#        sys.exit(0)
#signal(SIGKILL, alarm_handler)

GAMMA = 2
COLOR_BLUE900 = pygame.Color(13,71,161).correct_gamma(GAMMA)
COLOR_BLUE800 = pygame.Color(21, 101, 192).correct_gamma(GAMMA)
COLOR_WHITE = pygame.Color(255,255,255)
COLOR_BLACK = pygame.Color(0,0,0)
COLOR_GRAY600 = pygame.Color(117, 117, 117)
COLOR_GREEN500 = pygame.Color(76, 175, 80)
COLOR_BG = COLOR_BLACK

#Initialization
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_VIDEODRIVER', 'fbcon')
#os.putenv('SDL_MOUSEDRV', 'TSLIB')
#os.putenv('SDL_MOUSEDEV', '/dev/input/event0')
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
	str_time = FONT_LT.render(strftime("%I:%M"), fgcolor=COLOR_WHITE, size=48);
	str_time[1].center = (240, 240)
	str_form = FONT_LT.render(strftime("%p"), fgcolor=COLOR_WHITE, size=32)
	str_form[1].center = (240, 240)
	str_form[1].bottom = str_time[1].bottom
	str_time_width = str_time[1].width + str_form[1].width
	str_time_center = str_time_width/2
	str_time[1].centerx += (str_time_center - str_time[1].centerx)/4 + 12
	str_form[1].centerx -= (str_time_center - str_form[1].centerx)/4 - 24
	
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

def flip():
	pygame.display.flip()

def enable_vsync():
    if sys.platform != 'darwin':
        return
    try:
        import ctypes
        import ctypes.util
        ogl = ctypes.cdll.LoadLibrary(ctypes.util.find_library("OpenGL"))
        # set v to 1 to enable vsync, 0 to disable vsync
        v = ctypes.c_int(1)
        ogl.CGLSetParameter(ogl.CGLGetCurrentContext(), ctypes.c_int(222), ctypes.pointer(v))
    except:
        print "Unable to set vsync mode, using driver defaults"

threads = []

#Start touch event thread
touch = TouchThread(debug=True, device="/dev/input/event0")
touch.start()
threads.append(touch)

#Wait for touch thread
while(not touch.isInitialized()):
	if (touch.hasError()):
		exit(1)
	time.sleep(0.1)

print "READY!"

#Enable VSync
enable_vsync()

def exitThreads():
        #Exit threads
        print "Exiting..."
        for t in threads:
                t.stop()
        for t in threads:
                t.join()
        print "Exited."

def ui_clear(color, pos=(240,160)):
	r = (10, 20, 40, 70, 110, 160, 240, 320)
	dist = math.sqrt((240-pos[0])*(240-pos[0]) + (160-pos[1])*(160-pos[1]))
	for i in range(0, len(r)):
		radius = int(r[i] + dist)
		pygame.draw.circle(SURFACE, color, pos, radius)
		update()
		time.sleep(0.05)
	lcd.fill(color)
	update()

def ui_numpad_key(i, color, bgcolor=COLOR_BLUE900):
	btn_exit = u"\uf156"
        btn_backspace = u"\uf06e"
        btn_check = u"\uf12c"
        btn_n = ('1', '2', '3', '4', '5', '6', '7', '8', '9', btn_exit, '0', btn_check)
        btn_icon = (0,0,0,0,0,0,0,0,0,1,0,1)

        str = btn_n[i]
        x = i % 3
        y = (i - x) / 3
        pos = (240 + (x - 1)*80, 360-70-5 - (3-y)*70)
        font = FONT_ICONS if (btn_icon[i] is 1) else FONT_LT
        
	str_icon = font.render(str, fgcolor=color, bgcolor=bgcolor, size=40)
        str_icon[1].center = pos
        lcd.blit(str_icon[0], str_icon[1])

def ui_numpad_disp(done, color, pos=0, colordone=COLOR_GREEN500, colorbg=None):
	#pos = (int(round(240 + (i-2.5)*40)), 25)
	#pygame.draw.circle(SURFACE, color, pos, 20)
	width = 40
	for i in range(0, 6):
		pos = (int(round(240 + (i-2.5)*(width+5))), 10)
		rect = Rect(pos[0]-(width/2), pos[1], width, 20)
		if colorbg is not None:
			lcd.fill(colorbg, rect)
		lcd.fill(color, rect)

def ui_numpad():
	for alpha in (50, 100, 150, 200, 230, 255):
		blue = COLOR_BLUE800
		blue.a = alpha
		ui_numpad_disp(0, blue, 0, colorbg=COLOR_BLUE900)
		for i in range(0,11):
			ui_numpad_key(i, Color(255, 255, 255, alpha))
		gray = COLOR_GRAY600
		gray.a = alpha
		ui_numpad_key(11, gray)
		update()
		time.sleep(0.01)
	
	update()
	
	key = 0
	#while key is 0
	#while True:
	time.sleep(5)

def ui_main():
	
	clearScreen(COLOR_BLUE900)
	drawBigIcon(u"\uf341")
	
	state = 0

	while state is 0:
        	updateTimeBottom()
                update()
		if (touch.hasUpdate() is True):
			state = 1
			break
                time.sleep(0.1)
	if state is 1:
		event = touch.getState()
		event = (event[0],event[1])
		ui_clear(COLOR_BLUE900, event)
		ui_numpad()

try:
	ui_main()
except (Exception,KeyboardInterrupt,SystemExit) as e:
	traceback.print_exc()
	exitThreads()
exitThreads()
