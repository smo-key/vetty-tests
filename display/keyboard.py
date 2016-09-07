import string
import evdev

from evdev import InputDevice
from select import select


keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
dev = InputDevice('/dev/input/event1') #Change this to fit your device

#keys = {
#	1: "ESC",
#	
#}
#
while True:
   r,w,x = select([dev], [], [])
   for event in dev.read():
        if event.type==1 and event.value==1:
			try:
				print str(event.code) + " (" + keys[event.code] + ")"
			except:
				print event.code
			#print( keys[ event.code ] )

#devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
#for device in devices:
#	print(device.fn, device.name, device.phys)
#	if ("Keyboard" in device.name):
#		print "Keyboard found!"
