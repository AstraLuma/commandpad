#-*- coding: utf-8 -*-
"""
Handles quite a bit of the back to uinput.
"""
import sys, uinput, os, stat
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

def input_id(bustype=None, vendor=None, product=None, version=None):
	rv = uinput.input_id()
	if bustype is not None: rv.bustype = bustype
	if vendor is not None: rv.vendor = vendor
	if product is not None: rv.product = product
	if version is not None: rv.version = version
	return rv

def timeval(sec=None, usec=None):
	rv = uinput.timeval()
	if sec is not None: rv.sec = sec
	if usec is not None: rv.usec = usec
	return rv

def input_event(time=None, type=None, code=None, value=None):
	rv = uinput.input_event()
	if time is not None: rv.time = time
	if type is not None: rv.type = type
	if code is not None: rv.code = code
	if value is not None: rv.value = value
	return rv

def uinput_user_dev(name=None, id=None, ff_effects_max=None, absmax=None, absmin=None, absfuzz=None, absflat=None):
	rv = uinput.uinput_user_dev()
	if name is not None: rv.name = name
	if id is not None: rv.id = id
	if ff_effects_max is not None: rv.ff_effects_max = ff_effects_max
	if absmax is not None: rv.absmax = absmax
	if absmin is not None: rv.absmin = absmin
	if absfuzz is not None: rv.absfuzz = absfuzz
	if absflat is not None: rv.absflat = absflat
	return rv

if __name__ == '__main__':
	uud = uinput_user_dev(name="Saitek Magic Bus", ff_effects_max=0, absmax=[1]*(uinput.ABS_MAX+1))
	print repr(uud)
	print uud.__dict__
	print hex(int(uud.this))
	print dir(uud.this)
	print uud.absmax
	print uud.absmin
	
