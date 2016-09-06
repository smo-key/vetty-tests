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
import subprocess
import socket
import evdev

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

touch_state_reset = False

#Wait for touch thread
while(not touch.isInitialized()):
	if (touch.hasError()):
		exit(1)
	time.sleep(0.1)

print "READY!"

def touch_coord():
	global touch_state_reset
	if (not touch.isInitialized() or touch.hasError()):
		return (240, 160)
	if (touch_state_reset):
		touch_state_reset = False
		return (240, 160)
	else:
		state = touch.getState()
		return (state[0], state[1])

def touch_reset():
	global touch_state_reset
	state = (240, 160)
	touch_state_reset = True

#Enable VSync
enable_vsync()

def keyboardAttached():
	devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
	for device in devices:
		if ("Keyboard" in device.name):
			return True
	return False

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

def ui_fastclear(color=COLOR_BLUE900):
	lcd.fill(color)

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

	lcd.fill(bgcolor)
	#blit_clear = pygame.Rect(0,0,480,70)
	#lcd.fill(bgcolor, blit_clear)
	
	lcd.blit(str_icon[0], str_icon[1])
	lcd.blit(str_title[0], str_title[1])

def ui_draw_textbox(color, toptext, helptext):
	
	rect = pygame.Rect(64, 116, 352, 40)
	lcd.fill(color, rect)

	str_top = FONT_LT.render(toptext, fgcolor=colorAlphaMult(color, 0.9), size=24)
	str_top[1].left = 64
	str_top[1].top = 80

	str_bottom = FONT_LT.render(helptext, fgcolor=colorAlphaMult(color, 0.7), size=16)
	str_bottom[1].left = 64
	str_bottom[1].top = 174

	lcd.blit(str_top[0], str_top[1])
	lcd.blit(str_bottom[0], str_bottom[1])

def getKeyboardString(allowcancel, regex, skipchar=-1, skipresult=""):
	s = ""
	test = re.compile(regex)
	pygame.event.clear()
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
			return s
		elif (code is 27) and allowcancel:
			#escape
			return None
		elif (code is 8) and (len(s) > 0):
			#backspace
			s = s[:-1]
		#rest is actual characters
		elif (code == skipchar):
			#skip
			print "Skipping!"
			return skipresult
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

#def stateChanged(state):
#	try:
#		#check the server status and change state appropriately
#		r = requests.get('http://localhost:8002/state')
#		return not (state == r.text)
#	except Exception:
#		return False

def ui_register_fp(count, text, subtext="", bgcolor=COLOR_GREEN800, fgcolor=pygame.Color(76,175,80)):
	ui_fastclear(bgcolor)
	#Draw outside circle
	pygame.draw.circle(SURFACE, fgcolor, (240,120), 95)
	#Draw inside circle
	pygame.draw.circle(SURFACE, bgcolor, (240,120), 85)
	#Draw arc of completion
	if count > 0:
		angle = 2 * math.pi / 3 * count
		rect = pygame.Rect(145, 25, 190, 190)
		pygame.draw.arc(SURFACE, COLOR_WHITE, rect,math.pi/2-angle,(math.pi/2) + (math.pi/180),10)

	#Draw icon
	str_icon = FONT_ICONS.render(u"\uf237",fgcolor=COLOR_WHITE, size=140)
	str_icon[1].center = (240, 120)
	lcd.blit(str_icon[0], str_icon[1])

	#Draw text
	if len(text) > 0:
		str_text = FONT_LT.render(text, fgcolor=COLOR_WHITE, size=28)
		str_text[1].center = (240, 260)
		lcd.blit(str_text[0], str_text[1])

	#Draw subtext
	if len(subtext) > 0:
		str_sub = FONT_LT.render(subtext, fgcolor=pygame.Color(255,255,255,190), size=20)
		str_sub[1].center = (240, 296)
		lcd.blit(str_sub[0], str_sub[1])

def ui_register():
	phase = 0
	firstName = None
	lastName = None
	stuId = None
	invalidId = False
	while True:
		if phase is 0:
			#Draw animation
			ui_clear(COLOR_GREEN800, touch_coord())
			for alpha in (50, 100, 150, 200, 230):
				white = COLOR_WHITE
				white.a = alpha
				ui_fastclear(COLOR_GREEN800)
				ui_title(white, COLOR_GREEN800, "Register", u"\uf014") #f014
				ui_draw_textbox(white, "Enter your first name", "Press the ENTER key when you're done or ESC to cancel")
				update()
				time.sleep(0.01)
			phase = 1
		if phase is 1:
			#Get first name
			ui_fastclear(COLOR_GREEN800)
			ui_title(white, COLOR_GREEN800, "Register", u"\uf014") #f014
			ui_draw_textbox(COLOR_WHITE, "Enter your first name", "Press the ENTER key when you're done or ESC to cancel")	
			update()
			firstName = getKeyboardString(True, "^[A-Za-z\\-]{0,24}$")
			if firstName is None:
				touch_reset()
				return
			else:
				firstName = firstName.title()
				phase = 2
		if phase is 2:
			#Get last name
			ui_fastclear(COLOR_GREEN800)
			ui_title(COLOR_WHITE, COLOR_GREEN800, "Hi, " + firstName, u"\uf014")
			ui_draw_textbox(COLOR_WHITE, "Enter your last name", "Press the ENTER key when you're done or ESC to go back")
			update()
			lastName = getKeyboardString(True, "^[A-Za-z\\-]{0,24}$")
			if lastName is None:
				phase = 1
			else:
				lastName = lastName.title()
				invalidId = False
				phase = 3
		if phase is 3:
			#Get student ID
			ui_fastclear(COLOR_GREEN800)
			ui_title(COLOR_WHITE, COLOR_GREEN800, "Almost ready, " + firstName, u"\uf014")
			helptext = "If you don't have one, press the SPACEBAR to skip."
			if invalidId:
				helptext = "Invalid student or teacher ID."
			ui_draw_textbox(COLOR_WHITE, "Enter your student or teacher ID", helptext)
			update()
			stuId = getKeyboardString(True, "^[0-9]{0,9}$", 32, "")
			if stuId is None:
				phase = 2
			elif len(stuId) < 7 and len(stuId) > 0:
				#Not valid student ID
				invalidId = True
			else:
				phase = 10
		if phase is 10:
			#Draw fingerprint
			ui_clear(COLOR_GREEN800)
			ui_register_fp(0, "Press and hold finger firmly", "You may only record one finger")
			update()

			#Start enrollment
			r = None
			count = 0
			while count < 3:
				if ((r is not None) and r.text != "OK"):
					count = 0
					ui_register_fp(count, "Lift finger and try again", "Hold your finger firmly on the pad")
					update()
					time.sleep(2)
				elif ((r is not None) and r.text == "OK"):
					if count is 1:
						ui_register_fp(count, "Rotate finger slightly left and place", "Hold finger firmly on the pad")
					elif count is 2:
						ui_register_fp(count, "Rotate finger slightly right and place", "Hold finger firmly on the pad")
					update()
				r = requests.post('http://localhost:8002/register/' + str(int(count + 1)), data={ })
				#print r.text
				if (r.text == "OK"):
					count += 1
					ui_register_fp(count - 0.5, "Lift your finger now", "")
					update()
					d = requests.post('http://localhost:8002/wait/release', data={ })
					print "Release: " + d.text
				else:
					print "Enroll " + str(int(count + 1)) + ": " + r.text
					#if ("finger_timeout!" in r.text):				
					#	f = requests.post('http://localhost:8002/led/off', data={ })
					#	print "Led OFF: " + f.text
					#	return
					if ("timeout!" in r.text):
						f = requests.post('http://localhost:8002/led/off', data = { })
						print "Led OFF: " + f.text
						touch_reset()
						return

			#Success!
			ui_register_fp(3, "All done!", "")
			update()
			time.sleep(3)
	
			print "Done!"
			touch_reset()
			return

def get_ip_address():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	return s.getsockname()[0]

def ui_login_updatetime(bgcolor):
	#Draw time
	str_time = FONT_LT.render(strftime("%I:%M"), fgcolor=pygame.Color(255,255,255,255), size=26)
	str_time[1].bottom = 312
	str_time[1].left = 8

	str_timeap = FONT_LT.render(strftime("%p"), fgcolor=pygame.Color(255,255,255,255), size=18)
	str_timeap[1].bottom = str_time[1].bottom
	str_timeap[1].left = str_time[1].right + 6

	blit_clear = pygame.Rect(0, str_time[1].top - 8,
     str_time[1].width + str_timeap[1].width + 30, str_time[1].height + 16)
	
	#Blit
	lcd.fill(bgcolor, blit_clear)
	lcd.blit(str_time[0], str_time[1])
	lcd.blit(str_timeap[0], str_timeap[1])

def ui_login_updatetext(bgcolor, text, color=pygame.Color(255,255,255,200), textsize=20):
	#Draw text
	str_sub = FONT_LT.render(text, fgcolor=color, size=textsize)
	str_sub[1].center = (240, 260)
	lcd.blit(str_sub[0], str_sub[1])
	
	blit_clear = pygame.Rect(0, str_sub[1].top - 8, 480, str_sub[1].height + 16)

	#Blit
	lcd.fill(bgcolor, blit_clear)
	lcd.blit(str_sub[0], str_sub[1])

def ui_login():
	phase = 0
	while True:
		if phase is 0:
			#Draw animation
			ui_clear(COLOR_BLUE900, touch_coord())
			#for alpha in (50, 100, 150, 200, 230):
			#	white = COLOR_WHITE
			#	white.a = alpha
			#	ui_fastclear(COLOR_BLUE900)
			#	
			#	update()
			#	time.sleep(0.01)
			phase = 1
		if phase is 1:
			#Main screen - wait for touch or fingerprint
			ui_fastclear(COLOR_BLUE900)
			ui_register_fp(0, '', "", COLOR_BLUE900, pygame.Color(24,90,188).correct_gamma(GAMMA))
			
			#Draw text
			txt = "Place finger on pad"
			if (keyboardAttached()):
				txt += " or touch screen to register"
			ui_login_updatetext(COLOR_BLUE900, txt)			
			
			#Draw time
			ui_login_updatetime(COLOR_BLUE900)

			#Draw IP
			str_ip = FONT_LT.render(get_ip_address(), fgcolor=pygame.Color(255,255,255,120), size=14)
			str_ip[1].right = 474
			str_ip[1].bottom = 312
			lcd.blit(str_ip[0], str_ip[1])

			update()

			#Activate fingerprint and touchscreen
			bgcolor = COLOR_BLUE900
			start = timer()
			bigstart = timer()
			while True:
				p = False #fp pressed
				t = False #touchscreen touched
				while (not p) and (not t):
					if (touch.hasUpdate() is True):
						press = touch.getState()[2]
						if (press is 1 or press is 3):	
							t = keyboardAttached()
				
					try:
						r = requests.get('http://localhost:8002/pressed')
						if (r.text == "True"):
							p = True
					except:
						ui_login_updatetext(bgcolor, "Fingerprint sensor not ready, try again", textsize=24)

					#Draw things to screen	
					ui_login_updatetime(bgcolor)
					update()
					
					#Check timers
					if (timer() - start > 10) or (timer() - bigstart > 30):
						try:
							r = requests.post('http://localhost:8002/led/off', data={ })
							print "LED OFF: " + r.text
						except:
							pass
						#touch_reset()
						return -2

					usleep(10000) #100ms
				
				if t:
					#Turn FPS LED off
					try:
						r = requests.post('http://localhost:8002/led/off', data={ })
						print "LED OFF: " + r.text
					except:
						pass
					
					#Go to register screen
					return 20

				if p:
					#Identify
					r = requests.post('http://localhost:8002/login', data={ })
					print r.text
					start = timer()
					if (r.text[:2] == "OK"):
						id = int(r.text[3:])
						print "Logged in as " + str(id)

						#Go to success screen
						phase = 10
						break
					else:
						ui_login_updatetext(bgcolor, "Try again", COLOR_WHITE, 32)						

		if phase is 10:
			#Success!
			ui_clear(COLOR_GREEN800)

			user = {}
			user["firstName"] = "Arthur"
			user["lastName"] = "Pachachura"
			user["hoursToday"] = "2:40"
			user["hoursTotal"] = "263"
			user["lastEntry"] = "3:40 PM today"
			user["isLeaving"] = False

			white_lt = pygame.Color(255, 255, 255, 200)

			#Draw welcome + name
			str_name2 = FONT_LT.render(user["firstName"], fgcolor=COLOR_WHITE, size=32)
			str_name2[1].top = 24
			
			str_name1 = FONT_LT.render(("Goodbye, " if user["isLeaving"] else "Welcome, "), fgcolor=white_lt, size=24)
			str_name1[1].bottom = str_name2[1].bottom + 4
			str_name1[1].left = 16
			
			str_name2[1].left = str_name1[1].right + 6

			str_name3 = FONT_LT.render(user["lastName"], fgcolor=COLOR_WHITE, size=32)
			str_name3[1].left = str_name2[1].right + 10
			str_name3[1].bottom = str_name2[1].bottom

			#Draw hours
			str_h1 = FONT_LT.render(user["hoursToday"], fgcolor=COLOR_WHITE, size=36)
			str_h1[1].top = str_name2[1].bottom + 36
			str_h1[1].left = str_name1[1].left

			str_h2 = FONT_LT.render("logged today", fgcolor=white_lt, size=24)
			str_h2[1].bottom = str_h1[1].top + str_h1[1].height + 5
			str_h2[1].left = str_h1[1].right + 12

			str_h3 = FONT_LT.render("Last entered at " + user["lastEntry"], fgcolor=white_lt, size=16)
			str_h3[1].top = str_h1[1].top + str_h1[1].height + 16
			str_h3[1].left = str_name1[1].left
		
			str_h4 = FONT_LT.render(user["hoursTotal"], fgcolor=COLOR_WHITE, size=36)
			str_h4[1].top = str_h3[1].top + str_h3[1].height + 28
			str_h4[1].left = str_name1[1].left

			str_h5 = FONT_LT.render("hours total", fgcolor=white_lt, size=24)
			str_h5[1].left = str_h4[1].right + 12
			str_h5[1].bottom = str_h4[1].bottom

			#Blit and render
			lcd.blit(str_h1[0], str_h1[1])
			lcd.blit(str_h2[0], str_h2[1])
			lcd.blit(str_h3[0], str_h3[1])
			lcd.blit(str_h4[0], str_h4[1])
			lcd.blit(str_h5[0], str_h5[1])
			lcd.blit(str_name1[0], str_name1[1])
			lcd.blit(str_name2[0], str_name2[1])
			lcd.blit(str_name3[0], str_name3[1])
			#ui_login_updatetime(COLOR_GREEN800)
			update()

			#Wait until touch of screen or certain timeout
			start = timer()
			while touch.hasUpdate() is False:
				usleep(100000) #100ms
				if (timer() - start > 10): 
					touch_reset()
					return 1
				#ui_login_updatetime(COLOR_GREEN800)
				update()

			#Return to login screen
			return 1
	
def updateState(state):
	try:
		#check the server status and change state appropriately
		r = requests.get('http://localhost:8002/state')
		text = r.text
		#print text
		if (text == "Normal") and (state >= 10):
			state = -2
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
		if state is -2:
			#Clear screen
			ui_clear(COLOR_BLUE900)
			state = -1
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
			#Draw login/register screen
			state = ui_login()
		if state is 10:
			#Draw login numpad
			ui_clear(COLOR_BLUE900, touch_coord())
			result = ui_numpad()
			ui_clear(COLOR_BLUE900, touch_coord())
			state = -1
		if state is 20:
			#Register
			ui_register()
			state = 1 #Go to login
		#state = updateState(state)
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
	#Turn off fingerprint sensor
	try:
		f = requests.post('http://localhost:8002/led/off', data = { })
		print "Led OFF: " + f.text
	except:
		pass

	print "All done!"

if __name__ == '__main__':
	try:
		ui_main()
	except (Exception,KeyboardInterrupt,SystemExit) as e:
		traceback.print_exc()
		exitThreads()
exitThreads()
done()
