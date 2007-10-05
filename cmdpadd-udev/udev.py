#-*- coding: utf-8 -*-
"""
Handles quite a bit of the back to uinput.
"""
import sys, uinput, os, stat, struct, array
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
		raise ValueError, "Ran out of devices"

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
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self._fileobj.__exit__(exc_type, exc_val, exc_tb)
	
	def __getattr__(self, attr):
		return getattr(self._fileobj, attr)
	
	# Convenience functions to get info on the device
	def dev_id(self):
		rv = array.array('H', [0]*4)
		self.ioctl(uinput.EVIOCGID,rv, True)
		bits = rv
		return input_id(
				bustype=bits[uinput.ID_BUS],
				vendor=bits[uinput.ID_VENDOR], 
				product=bits[uinput.ID_PRODUCT],
				version=bits[uinput.ID_VERSION])
	
	def dev_version(self):
		rv = array.array("i", [0])
		self.ioctl(uinput.EVIOCGVERSION,rv, True)
		return rv[0]
	
	def dev_name(self):
		rv = array.array("c", ['\0']*256)
		self.ioctl(uinput.EVIOCGNAME(len(rv)), rv, True)
		return "".join(rv).rstrip('\0')
	
	def dev_bits(self):
		import math
		BITS_PER_LONG = int(math.ceil(math.log(sys.maxint) / math.log(2))) + 1
		NBITS = lambda x:  (x-1) // BITS_PER_LONG + 1
		OFF = lambda x: x % BITS_PER_LONG
		BIT = lambda x: 1L << OFF(X)
		LONG = lambda x: x // BITS_PER_LONG
		test_bit = lambda b, array: (array[LONG(b)] >> OFF(b)) & 1
		rvbits = {}
		sfmt = 'L', [0] * NBITS(uinput.KEY_MAX)
		bit = [None] * uinput.EV_MAX
		buf = array.array(*sfmt)
		self.ioctl(uinput.EVIOCGBIT(0, uinput.EV_MAX), buf, True)
		bit[0] = list(buf)
		for i in xrange(1,uinput.EV_MAX):
			if test_bit(i, bit[0]):
				buf = array.array(*sfmt)
				try:
					self.ioctl(uinput.EVIOCGBIT(i, uinput.KEY_MAX), buf, True);
				except: pass
				bit[i] = list(buf)
				rvbits[i] = [j for j in xrange(uinput.KEY_MAX) if test_bit(j, bit[i])]
		return rvbits
	
	def dev_ranges(self):
		"""
		The values of the dict are in this order:
			value, min, max, fuzz, flat
		"""
		bits = self.dev_bits()
		if uinput.EV_ABS not in bits: return {}
		rv = {}
		for j in bits[uinput.EV_ABS]:
			abs = array.array("i", [0]*5)
			self.ioctl(uinput.EVIOCGABS(j), abs, True)
			rv[j] = list(abs)
		return rv

class UidevStream(EvdevStream):
	"""
	Just like EvdevStream, but with some convenience methods for uinput.
	"""
	__slots__ = '_devcreated','_devcreatable'
	def __init__(self, fn, *pargs):
		super(UidevStream, self).__init__(fn, *pargs)
		self._devcreated = False
		self._devcreatable = False
	def ioctl(self, op, *pargs):
		rv = super(UidevStream, self).ioctl(op, *pargs)
		if op == uinput.UI_DEV_CREATE:
			self._devcreated = True
		elif op == uinput.UI_DEV_DESTROY:
			self._devcreated = False
		return rv
	
	def close(self):
		super(UidevStream, self).close()
		self._devcreatable = False
		self._devcreated = False
	
	def write(self, obj):
		super(UidevStream, self).write(obj)
		if isinstance(obj, uinput.uinput_user_dev): self._devcreatable = True
	
	def __enter__(self):
		if self._devcreatable and not self._devcreated:
			self.ioctl(uinput.UI_DEV_CREATE)
		else:
			super(UidevStream, self).__enter__()
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
