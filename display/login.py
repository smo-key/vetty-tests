import pygame
import os
import time
import re
import pygame.freetype as freetype
import pygame.font as font
from pygame.locals import *
from time import strftime
import threading
import sys
import traceback
import math
from PyTouch import pytouch
from PyTouch.pytouch import TouchThread as TouchThread
from timeit import default_timer as timer
import requests

GAMMA = 2
COLOR_BLUE900 = pygame.Color(13,71,161).correct_gamma(GAMMA)
COLOR_BLUE800 = pygame.Color(21, 101, 192).correct_gamma(GAMMA)
COLOR_RED900 = pygame.Color(191,54,12).correct_gamma(GAMMA)
COLOR_RED800 = pygame.Color(216,67,21).correct_gamma(GAMMA)
COLOR_GREEN900 = pygame.Color(27,94,32).correct_gamma(GAMMA)
COLOR_GREEN800 = pygame.Color(46,125,50) #.correct_gamma(GAMMA)
COLOR_WHITE = pygame.Color(255,255,255)
COLOR_BLACK = pygame.Color(0,0,0)
COLOR_GRAY600 = pygame.Color(117, 117, 117)
COLOR_GREEN500 = pygame.Color(76, 175, 80)
COLOR_BG = COLOR_BLACK

usleep = lambda x: time.sleep(x/1000000.0)

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
FONT_MD = freetype.Font("../fonts/HelveticaNeueLTStd-Md.otf", size=64);
FONT_ICONS = freetype.Font("../fonts/materialdesignicons-webfont.ttf", size=64, ucs4=True);

def clearScreen(color):
	global COLOR_BG
	COLOR_BG = color
	lcd.fill(COLOR_BG)

def colorAlphaMult(color, alpha):
    return pygame.Color(color.r, color.g, color.b, int(math.floor(color.a * alpha)))

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

def touch_coord():
	if (not touch.isInitialized() or touch.hasError()):
		return (240, 160)
	state = touch.getState()
	return (state[0], state[1])

#Enable VSync
enable_vsync()

def ui_clear(color=COLOR_BLUE900, pos=(240,160)):
	r = (10, 20, 40, 70, 110, 160, 240, 320)
	dist = math.sqrt((240-pos[0])*(240-pos[0]) + (160-pos[1])*(160-pos[1]))
	for i in range(0, len(r)):
		radius = int(r[i] + dist)
		pygame.draw.circle(SURFACE, color, pos, radius)
		update()
		time.sleep(0.05)
	lcd.fill(color)
	update()

def ui_numpad_key(i, color, bgcolor=COLOR_BLUE900, touchcolor=COLOR_BLUE800, touched=False):
	if i is -1: return

	btn_exit = u"\uf156"
	btn_backspace = u"\uf06e"
	btn_check = u"\uf12c"
	btn_n = ('1', '2', '3', '4', '5', '6', '7', '8', '9', btn_exit, '0', btn_check, btn_backspace)
	btn_icon = (0,0,0,0,0,0,0,0,0,1,0,1,1)
	
	font = FONT_ICONS if (btn_icon[i] is 1) else FONT_LT
	str = btn_n[i]
	if (i is 12): i = 9
        x = i % 3
        y = (i - x) / 3
	pos = (240 + (x - 1)*80, 360-70-5 - (3-y)*70)
	
	str_icon = font.render(str, fgcolor=color, bgcolor=bgcolor, size=40)
        str_icon[1].center = pos

	if touched is True:
		#for alpha in (100, 200, 230, 250, 255, 250, 230, 200, 100, 0):
		pygame.draw.circle(SURFACE, touchcolor, pos, 40)
		str_icon = font.render(str, fgcolor=color, bgcolor=touchcolor, size=40)
        	str_icon[1].center = pos
		lcd.blit(str_icon[0], str_icon[1])
		update()
		state = touch.getState()
		while not (state[2] is 3 or state[2] is 2):
			time.sleep(0.001)
			state = touch.getState()
		pygame.draw.circle(SURFACE, bgcolor, pos, 40)
		str_icon = font.render(str, fgcolor=color, bgcolor=bgcolor, size=40)
                str_icon[1].center = pos
                lcd.blit(str_icon[0], str_icon[1])
		update()
	else:
		pygame.draw.circle(SURFACE, bgcolor, pos, 40)
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
		pos = (int((240 + (i-2.5)*40)), 25)
		col = color
		if (i < done): 
			col = colordone
        	pygame.draw.circle(SURFACE, col, pos, 12)
		#lcd.fill(color, rect)

def dist(pos1, pos2):
	return math.sqrt((pos2[0] - pos1[0])*(pos2[0] - pos1[0]) + (pos2[1] - pos1[1])*(pos2[1] - pos1[1])) 

def ui_numpad_getkey(pos):
	keys = []
	padding = 5
	for i in range(0,12):
		x = i % 3
        	y = (i - x) / 3
        	keys.append((240 + (x - 1)*80, 360-70-5 - (3-y)*70))
	key = -1
	dx = 35 #maximum distance
	for i in range(0,12):
		dxi = dist(pos, keys[i])
		if (dxi < dx):
			dx = dxi
			key = i
	return key

def ui_numpad_loop(bigstart,color,colorback):
	key = -1
	text = "" 
	while True:
                start = timer()
                while touch.hasUpdate() is False:
                        usleep(10000) #10ms
                        if (timer() - start > 15): return None
                        if (timer() - bigstart > 120): return None
                event = touch.getState()
                pos = (event[0], event[1])
                action = event[2] #1=pressed, 2=released
                pressed = (action is 1) or (action is 3)
                if (pressed):
                        key = ui_numpad_getkey(pos)
                        print "User Key: " + str(key)
                        if key is -1: #no key
                                continue
                        if (key is 9 and len(text) > 0):
                                key = 12
                        if (key is 11 and len(text) is 0):
                                ui_numpad_key(key,COLOR_GRAY600,color,colorback)
                                continue
                        else:
                                ui_numpad_key(key,Color(255,255,255),color,colorback,touched=True)
                        if (key is 10):
                                text = text + "0"
                        elif (key is 12):
                                text = text[:-1]
                        elif (key is 9):
                                return None
                        elif (key is 11):
                                if (len(text) is 0):
                                        continue
                                return text
                        else:
                                text = text + str(key + 1)
                        #update display upon keypress
                        ui_numpad_disp(len(text), colorback, 0, colordone=Color(255,255,255), colorbg=color)
                        if (len(text) > 0):
                                ui_numpad_key(12, Color(255,255,255),color,colorback)
                                ui_numpad_key(11, Color(255,255,255),color,colorback)
                        else:
                                ui_numpad_key(9, Color(255,255,255),color,colorback)
                                ui_numpad_key(11, COLOR_GRAY600,color,colorback)
                        update()
                        if (len(text) >= 6):
                                return text


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
	bigstart = timer()	
	text = ui_numpad_loop(bigstart, COLOR_BLUE900, COLOR_BLUE800)
	while True:
		#empty?
		if (text is None):
			return False
		#correct?
		if (text == "12345"):
			return True
		#incorrect
		lcd.fill(COLOR_RED900)
		ui_numpad_disp(0, COLOR_RED800, 0, colorbg=COLOR_RED900)
		for i in range(0,11):
			ui_numpad_key(i, Color(255, 255, 255, alpha), COLOR_RED900)
		ui_numpad_key(11, COLOR_GRAY600, COLOR_RED900)
		update()

		#repeat
		text = ui_numpad_loop(bigstart, COLOR_RED900, COLOR_RED800)

def ui_title(color, bgcolor, title, icon):
	str_icon = FONT_ICONS.render(icon, fgcolor=color, size=32)
	str_icon[1].center = (30,32)

	str_title = FONT_LT.render(title, fgcolor=color, size=32)
	str_title[1].left = 64
	str_title[1].top = 20

	blit_clear = pygame.Rect(0,0,480,70)
	lcd.fill(bgcolor, blit_clear)
	
	lcd.blit(str_icon[0], str_icon[1])
	lcd.blit(str_title[0], str_title[1])

def ui_draw_textbox(color, toptext, helptext):
	
	rect = pygame.Rect(64, 116, 352, 40)
	lcd.fill(color, rect)

	str_top = FONT_LT.render(toptext, fgcolor=colorAlphaMult(color, 0.5), size=24)
	str_top[1].left = 64
	str_top[1].top = 80

	str_bottom = FONT_LT.render(helptext, fgcolor=colorAlphaMult(color, 0.3), size=16)
	str_bottom[1].left = 64
	str_bottom[1].top = 174

	lcd.blit(str_top[0], str_top[1])
	lcd.blit(str_bottom[0], str_bottom[1])

def getKeyboardString(allowcancel, regex):
	s = ""
	test = re.compile(regex)
	done = False
	pygame.event.clear()
	while not done:
		while True:
			while not pygame.event.peek(2):
				time.sleep(0.01)
			event = pygame.event.get(2)[0]
			pygame.event.clear()
			#print event.__dict__
			code = event.__dict__['key']
			char = event.__dict__['unicode']
			if (code is 13) and (len(s) > 0):
				#enter key
				done = True
				break
			elif (code is 27) and allowcancel:
				#escape
				done = True
				s = ""
				break
			elif (code is 8) and (len(s) > 0):
				#backspace
				s = s[:-1]
			#rest is actual characters
			elif (test.match(char) is None) or (test.match(s + char) is None):
				#don't allow this character because it would fail to pass the regex
				continue
			elif code >= 97 and code <= 122:
				s += char
			elif code is 32:
				s += char
			elif code is 45:
				s += char
			elif code >= 48 and code <= 57:
				s += char
			else:
				continue
			#print s + " (" + char + ")"

			#Draw the string!
			rect = pygame.Rect(64, 116, 352, 40)
			lcd.fill(COLOR_WHITE, rect)

			str = FONT_LT.render(s, fgcolor=COLOR_BLACK, size=24)
			str[1].center = (80, 136)
			str[1].left = 72

			lcd.blit(str[0], str[1])
			update()
	return s

def ui_register():
	ui_clear(COLOR_GREEN800)
	for alpha in (50, 100, 150, 200, 230, 255):
		white = COLOR_WHITE
		white.a = alpha
		ui_title(white, COLOR_GREEN800, "Register", u"\uf014") #f014
		ui_draw_textbox(white, "Enter your LEGAL FULL name", "Press the ENTER key when you're done or ESC to go back")	
		update()
		time.sleep(0.01)
	print getKeyboardString(True, "^[A-Za-z -]*$")
	print "Done!"
	return

def updateState(state):
	try:
		#check the server status and change state appropriately
		r = requests.get('http://localhost:8002/state')
		text = r.text
		#print text
		if (text == "Normal") and (state > 10):
			state = -1
		elif (text == "Register") and (state < 10 or state >= 20):
			state = 10
		#print text + " " + str(state)
		return state
	except Exception:
		return state

def ui_main():
	clearScreen(COLOR_BLUE900)
	state = -1

	while True:
		if state is -1:
			#Draw start icon
			drawBigIcon(u"\uf341")
			state = 0
		if state is 0:
			#Draw start screen
			updateTimeBottom()
			update()
			if (touch.hasUpdate() is True):
				press = touch.getState()[2]
				if (press is 1 or press is 3):
					state = 1
		if state is 1:
			#Draw login numpad
			ui_clear(COLOR_BLUE900, touch_coord())
			result = ui_numpad()
			ui_clear(COLOR_BLUE900, touch_coord())
			state = -1
		if state is 10:
			#Register
			#print "Running registration"
			ui_register()
		state = updateState(state)
		usleep(25000) #250ms

def exitThreads():
	#Exit threads
	print "Exiting..."
	for t in threads:
		t.stop()
	for t in threads:
		t.join()
	print "Exited."

def done():
	print "All done!"

if __name__ == '__main__':
	try:
		ui_main()
	except (Exception,KeyboardInterrupt,SystemExit) as e:
		traceback.print_exc()
		exitThreads()
exitThreads()
done()
