#-*- coding: utf-8 -*-
"""
Handles quite a bit of the back to uinput.
"""
import sys, uinput, os, stat, pystruct
from fcntl import ioctl

UINPUT_DEVICES = ['/dev/uinput', '/dev/misc/uinput', '/dev/input/uinput']

def FindUinput(*others):
	"""FindUinput([string ...]) -> string
	Attempts to locate the uinput devices from the names in UINPUT_DEVICES and 
	what's passed in. Returns None if not found.
	"""
	for dev in UINPUT_DEVICES+list(others):
		if os.path.exists(dev) and stat.S_ISCHR(os.stat(dev).st_mode):
			return dev
	else:
		return None

class InputEvent(pystruct.Struct):
	"""
	This is sent to and from uinput and evdev devices (the input subsystem).
	"""
	__fields__ = [
		('sec', 'l', """Number of seconds this occured"""),
		('usec', 'l', """The microseconds of the timestamp"""),
		('type', 'H', """The type of event"""),
		('code', 'H', """The input button/axis/whatever"""),
		('value', 'l', """The current value"""),
		]

if __name__ == '__main__':
	ie = InputEvent(sec=1, usec=2, type=3, code=4)
	print repr(ie)
	print ie.__dict__
	
