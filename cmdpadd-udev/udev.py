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
		raise ValueError, "Ran out of options"

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

class EvdevStream(object):
	__slots__ = '_fileobj','__weakref__'
	def __init__(self, fn, *pargs):
		if isinstance(fn, int):
			self._fileobj = os.fdopen(fn, *pargs)
		elif isinstance(fn, basestring):
			self._fileobj = open(fn, *pargs)
		else:
			self._fileobj = fn
	
	def write(self, obj):
		if hasattr(obj, 'pack'):
			self._fileobj.write(obj.pack())
			self._fileobj.flush()
		else:
			raise ValueError, "Must have a pack() attribute."
	
	def read(self, type):
		if hasattr(type, '__len__'):
			s = type.__len__()
		elif hasattr(type, 'length'):
			s = type.length()
		data = self._fileobj.read(s)
		return type.unpack(data)
	
	def ioctl(self, op, *pargs):
		ioctl(self._fileobj, op, *pargs)
	
	def close(self):
		self._fileobj.close()
	
	def flush(self):
		# Should be redundent
		self._fileobj.flush()
	
	def iter(self,type):
		"""
		Like iter(), but needs an initial type. To change the type, use .send() 
		(PEP 342).
		"""
		while True: # Ends when something raises an error
			ntype = yield self.read(type)
			if ntype is not None: type = ntype
	
	def __enter__(self):
		self._fileobj.__enter__()
		return self
	
	def __getattr__(self, attr):
		return getattr(self._fileobj, attr)

class UidevStream(EvdevStream):
	"""
	Just like EvdevStream, but with some convenience methods for uinput.
	"""
	__slots__ = '_devcreated',
	_devcreated = False
	def ioctl(self, op, *pargs):
		rv = super(UidevStream, self).ioctl(op, *pargs)
		if op == uinput.UI_DEV_CREATE:
			self._devcreated = True
		elif op == uinput.UI_DEV_DESTROY:
			self._devcreated = False
		return rv
	
	def __enter__(self):
		if self._fileobj.closed:
			super(UidevStream, self).__enter__()
		elif not self._devcreated:
			self.ioctl(uinput.UI_DEV_CREATE)
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		if self._devcreated:
			self.ioctl(uinput.UI_DEV_DESTROY)
		else:
			super(UidevStream, self).__exit__(exc_type, exc_val, exc_tb)

if __name__ == '__main__':
	uud = uinput_user_dev(name="Saitek Magic Bus", ff_effects_max=0, absmax=[1]*(uinput.ABS_MAX+1))
	print repr(uud)
	print uud.__dict__
	print hex(int(uud.this))
	print dir(uud.this)
	print dir(uinput.timeval)
	print uud.absmax
	print uud.absmin
	print repr(input_event().pack())
