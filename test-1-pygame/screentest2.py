import pygame
import os
import time
import pygame.freetype as freetype
import pygame.font as font
from pygame.locals import *
import time
from time import strftime
import threading

GAMMA = 2
COLOR_BLUE900 = pygame.Color(13,71,161).correct_gamma(GAMMA)
COLOR_WHITE = pygame.Color(255,255,255)
COLOR_BLACK = pygame.Color(0,0,0)
COLOR_BG = COLOR_BLACK

#Initialization
os.putenv('SDL_FBDEV', '/dev/fb0')
#os.putenv('SDL_MOUSEDRV', 'TSLIB')
#os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
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

def scanForTouch():
	# Scan touchscreen events
    	for event in pygame.event.get():
        	if(event.type is MOUSEBUTTONDOWN):
			pos = pygame.mouse.get_pos()
			return (pos, 0)
		elif(event.type is MOUSEBUTTONUP):
            		pos = pygame.mouse.get_pos()
           		return (pos, 1)
	return ((-1, -1), -1)

clearScreen(COLOR_BLUE900)
drawBigIcon(u"\uf237")

thread_time_run = True;
touch_pos = None
touch_state = -1 #-1: no touch, 0: pressed, 1: released, 2: pressed and releasd 
touch_lock = threading.Lock()
threads = []

class StoppableThread(threading.Thread):
	"""Thread class with a stop() method. The thread itself has to check regularly for the stopped() condition."""
	def __init__(self):
        	super(StoppableThread, self).__init__()
        	self._stop = threading.Event()

    	def stop(self):
        	self._stop.set()

    	def stopped(self):
        	return self._stop.isSet()

def has_touch():
	global touch_pos
	if touch_pos is not None:
		return True
	return False

def get_touch():
	global touch_pos
	global touch_state
	touch_lock.acquire()
	ret = None
	if touch_pos is not None:
		ret = (touch_pos, touch_state)
	if touch_state == 1:
		touch_state = -1
	elif touch_state == 0:
		touch_state = 1
	touch_pos = None
	touch_lock.release()
	return ret

class thread_touch(StoppableThread):
        def __init__(self):
		super(thread_touch, self).__init__()
        def run(self):
		global touch_pos
		global touch_state
		while self.stopped() is False:
			touch_lock.acquire()
			ret = scanForTouch()
			if (touch_state is 0) and (ret[1] is 1):
				#If the touch response is too fast, we both press and release
				ret = (ret[0], 2)
			if (ret[1] is not -1):		
				#Just made sure that we don't override any state if there is one
				touch_pos = ret[0]
				touch_state = ret[1]
				if (touch_pos is (-1,-1)):
					touch_pos = None
				else:
					print ret
			touch_lock.release()
			time.sleep(0.05)
		print "Exiting touch thread."

#Start touch event thread
touch_thread = thread_touch()
touch_thread.start()
threads.append(touch_thread)

def exitThreads():
        #Exit threads
        print "Exiting..."
        for t in threads:
                t.stop()
        for t in threads:
                t.join()
        print "Exited."

def ui_main():
	while True:
        	updateTimeBottom()
                update()
		if (has_touch() is True):
			print "TOUCH: " + str(get_touch())
                time.sleep(1)

try:
	ui_main()
except (KeyboardInterrupt, SystemExit):
	exitThreads()
exitThreads()
