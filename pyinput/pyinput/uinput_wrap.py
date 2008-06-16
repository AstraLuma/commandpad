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
		raise ValueError, "Couldn't find uinput: ran out of devices"

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
			raise TypeError, "obj must have a pack() method."
	
	def read(self, type):
		if hasattr(type, '__len__'):
			s = type.__len__()
		elif hasattr(type, 'size'):
			s = type.size()
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
		"""e.dev_id() -> input_id
		Queries the device for its input_id struct.
		"""
		rv = array.array('H', [0]*4)
		self.ioctl(uinput.EVIOCGID, rv, True)
		bits = rv
		return uinput.input_id(
				bustype=bits[uinput.ID_BUS],
				vendor=bits[uinput.ID_VENDOR], 
				product=bits[uinput.ID_PRODUCT],
				version=bits[uinput.ID_VERSION])
	
	def dev_version(self):
		"""e.dev_version() -> int
		Queries the device for its version.
		"""
		rv = array.array("i", [0])
		self.ioctl(uinput.EVIOCGVERSION, rv, True)
		return rv[0]
	
	def dev_name(self):
		"""e.dev_name() -> str
		Queries the device for name.
		"""
		rv = array.array("c", ['\0']*256)
		self.ioctl(uinput.EVIOCGNAME(len(rv)), rv, True)
		return "".join(rv).rstrip('\0')
	
	def dev_bits(self):
		"""e.dev_bits() -> {int: [int], ...}
		Queries a device for its event bits. The keys are one of the EV_* 
		constants.
		"""
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
		"""e.dev_ranges() -> {int: (int,int,int,int,int), ...}
		Queries the range of each of the absolute axis.
		
		The keys are one of the ABS_* constants.
		The values are (value, min, max, fuzz, flat).
		"""
		bits = self.dev_bits()
		if uinput.EV_ABS not in bits: return {}
		rv = {}
		for j in bits[uinput.EV_ABS]:
			abs = array.array("i", [0]*5)
			self.ioctl(uinput.EVIOCGABS(j), abs, True)
			rv[j] = list(abs)
		return rv

class _uinput_device_manager(object):
	"""
	Private class to automagically call UinputStream.destroy()
	"""
	__stream = None
	def __init__(self, stream):
		self.__stream = stream
	def __enter__(self):
		if not self.__stream._devcreated:
			self.__stream.create()
		return self
			
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.__stream.destroy()

class UinputStream(EvdevStream):
	"""
	Just like EvdevStream, but with some convenience methods for uinput.
	
	Example:
		with UinputStream() as us:
			us.events = [...]
			with us.create():
				us.event(...)
	"""

	__slots__ = '_devcreated','_devcreatable'
	def __init__(self, fn=None, *pargs):
		if fn is None:
			fn = FindUinput()
		super(UinputStream, self).__init__(fn, *pargs)
		self._devcreated = False
		self._devcreatable = False
	def ioctl(self, op, *pargs):
		rv = super(UinputStream, self).ioctl(op, *pargs)
		if op == uinput.UI_DEV_CREATE:
			self._devcreated = True
		elif op == uinput.UI_DEV_DESTROY:
			self._devcreated = False
		return rv
	
	def close(self):
		super(UinputStream, self).close()
		self._devcreatable = False
		self._devcreated = False
	
	def write(self, obj):
		super(UinputStream, self).write(obj)
		if isinstance(obj, uinput.uinput_user_dev): self._devcreatable = True
	
	def create(self):
		"""u.create() -> contextmanager
		Actually creates the devices, locking events. Returns a context manager 
		which will call destroy() automagically.
		"""
		if not self._devcreatable:
			# Send the events
			pass
		if self._devcreatable and not self._devcreated:
			self.ioctl(uinput.UI_DEV_CREATE)
	
	def destroy(self):
		"""u.destroy() -> None
		Destroys the device created by create()
		"""
		if self._devcreated:
			self.ioctl(uinput.UI_DEV_DESTROY)
	
	def __enter__(self):
		return super(UinputStream, self).__enter__()
			
	def __exit__(self, exc_type, exc_val, exc_tb):
		return super(UinputStream, self).__exit__(exc_type, exc_val, exc_tb)

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
