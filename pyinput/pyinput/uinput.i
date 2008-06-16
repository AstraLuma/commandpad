// vim:syn=c
%module(package="pyinput") uinput
%feature("autodoc", "1");

#ifndef SWIGPYTHON
#error "Doesn't work except with Python"
#endif

%{
/* Put headers and other declarations here */
#include <linux/input.h>
#include <linux/uinput.h>
%}

%typemap(in) __time_t {
    $1 = PyLong_AsLong($input);
}
%typemap(out) __time_t {
    $result = PyLong_FromLong($1);
}

%typemap(in) __suseconds_t {
    $1 = PyLong_AsLong($input);
}
%typemap(out) __suseconds_t {
    $result = PyLong_FromLong($1);
}

%typemap(in) __u16 {
    $1 = PyLong_AsUnsignedLong($input);
}
%typemap(out) __u16 {
	PyObject * spam = 0;
	spam = PyLong_FromUnsignedLong($1);
    $result = PyLong_FromUnsignedLong($1);
}

typedef signed long int __s32;

// This does not create the cleanest wrapper (I'd rather a dynamic-updater with 
// a custom class), but it works.

%typemap(in) int[ANY](int temp[$1_dim0]) {
  int i;
  if (!PySequence_Check($input)) {
      PyErr_SetString(PyExc_TypeError,"Expecting a sequence");
      return NULL;
  }
  if (PyObject_Length($input) != $1_dim0) {
      PyErr_SetString(PyExc_ValueError,"Expecting a sequence with $1_dim0 elements");
      return NULL;
  }
  for (i = 0; i < $1_dim0; i++) {
      PyObject *o = PySequence_GetItem($input,i);
      if (!PyInt_Check(o)) {
         Py_XDECREF(o);
         PyErr_SetString(PyExc_ValueError,"Expecting a sequence of ints");
         return NULL;
      }
      temp[i] = PyInt_AsLong(o);
      Py_DECREF(o);
  }
  $1 = &temp[0];
}

%typemap(out) int[ANY](int temp[$1_dim0]) {
  int i;
  $result = PyTuple_New($1_dim0);
  for (i = 0; i < $1_dim0; i++) {
    PyTuple_SetItem($result, i, PyInt_FromLong($1[i]));
  }
}

%include <linux/input.h>
%include <linux/uinput.h>

struct timeval
{
    __time_t tv_sec;		/* Seconds.  */
    __suseconds_t tv_usec;	/* Microseconds.  */
};

%pythoncode %{
def _struct_new(theclass):
	def __new__(cls, *args, **kwargs):
		"""
		A generic struct initializer that allows for setting of props during initializartion.
		"""
		self = super(theclass, cls).__new__(cls, *args, **kwargs)
		props = {}
		for k,v in kwargs.copy().iteritems():
			if hasattr(cls, k) and not k.startswith('__') and k not in ('this', 'thisown'):
				props[k] = v
				del kwargs[k]
		self.__init__(*args, **kwargs)
		for k,v in props.iteritems():
			setattr(self, k, v)
		return self
	theclass.__new__ = staticmethod(__new__) # This doesn't work.
%}
%define STRUCT_UTILS(type)
%extend type {
	PyObject* pack() {
		char* rv = 0;
		rv = malloc(sizeof(struct type));
		memcpy(rv, $self, sizeof(struct type));
		return PyString_FromStringAndSize(rv, sizeof(struct type));
	}
	
	static struct type *unpack(PyObject *data) {
		struct type *rv = 0;
		if (!PyString_Check(data) || PyString_Size(data) != sizeof(struct type)) {
			return NULL;
		}
		rv = malloc(sizeof(struct type));
		//printf("type::unpack:rv:%x\n", rv);
		memcpy(rv, PyString_AsString(data), sizeof(struct type));
		return rv;
	}
	
	static size_t size() {
		return sizeof(struct type);
	}
}
%newobject type::pack;
%newobject type::unpack;
%exception type::unpack {
  $action
  if (!result) {
     PyErr_SetString(PyExc_ValueError,"Expecting a string of the correct length");
     return NULL;
  }
}
%pythoncode %{
_struct_new(type)
%}
%enddef

STRUCT_UTILS(ff_condition_effect);
STRUCT_UTILS(ff_constant_effect);
STRUCT_UTILS(ff_effect);
// ff_effect_u is a union in ff_effect
STRUCT_UTILS(ff_envelope);
STRUCT_UTILS(ff_periodic_effect);
STRUCT_UTILS(ff_ramp_effect);
STRUCT_UTILS(ff_replay);
STRUCT_UTILS(ff_rumble_effect);
STRUCT_UTILS(ff_trigger);
STRUCT_UTILS(input_absinfo);
STRUCT_UTILS(uinput_ff_erase);
STRUCT_UTILS(uinput_ff_upload);
STRUCT_UTILS(input_id);
STRUCT_UTILS(timeval);
STRUCT_UTILS(input_event);
STRUCT_UTILS(uinput_user_dev);

%extend timeval {
	PyObject* __float__() {
		double rv = 0.0;
		rv += $self->tv_sec;
		rv += ((double)$self->tv_usec) / 1e6;
		return PyFloat_FromDouble(rv);
	}
}

%define RAW_CONST(type, name)
%init %{
SWIG_Python_SetConstant(d, #name,SWIG_From_##type((type)(name)));
%}
%pythoncode %{
globals()[`name`] = getattr(_uinput, `name`)
%}
%enddef

RAW_CONST(long, UI_SET_EVBIT);
RAW_CONST(long, UI_SET_KEYBIT);
RAW_CONST(long, UI_SET_RELBIT);
RAW_CONST(long, UI_SET_ABSBIT);
RAW_CONST(long, UI_SET_MSCBIT);
RAW_CONST(long, UI_SET_LEDBIT);
RAW_CONST(long, UI_SET_SNDBIT);
RAW_CONST(long, UI_SET_FFBIT);
RAW_CONST(long, UI_SET_PHYS);
RAW_CONST(long, UI_SET_SWBIT);
RAW_CONST(long, UI_DEV_CREATE);
RAW_CONST(long, UI_DEV_DESTROY);
RAW_CONST(long, EVIOCGID);
RAW_CONST(long, EVIOCGVERSION);


%define MACRO(type, name, cargs, argnames)
type _##name cargs;
%pythoncode %{
def _##name argnames :
	"A C Macro. Really lame, I know."
	return _uinput._##name argnames
globals()[`name`] = _##name
%}
%{
type _##name cargs {
	return name argnames;
}
%}
%enddef

MACRO(long, EVIOCGNAME, (long len), (len));
MACRO(long, EVIOCGPHYS, (long len), (len));
MACRO(long, EVIOCGUNIQ, (long len), (len));

MACRO(long, EVIOCGKEY, (long len), (len));
MACRO(long, EVIOCGLED, (long len), (len));
MACRO(long, EVIOCGSND, (long len), (len));
MACRO(long, EVIOCGSW, (long len), (len));

//MACRO(long, EVIOCGBIT, (long ev, long len), (ev, len));
MACRO(long, EVIOCGABS, (long abs), (abs));
MACRO(long, EVIOCSABS, (long abs), (abs));

long _EVIOCGBIT(long ev, long len);
%pythoncode %{
def _EVIOCGBIT(ev,len):
	"A C Macro. Really lame, I know."
	return _uinput._EVIOCGBIT(ev,len)
globals()["EVIOCGBIT"] = _EVIOCGBIT
%}
%{
long _EVIOCGBIT(long ev, long len) {
	return EVIOCGBIT(ev, len);
}
%}

%{
// Some forward declarations
#ifdef __cplusplus
extern "C"
#endif
SWIGEXPORT void SWIG_init(void);

static PyMethodDef SwigMethods[];

PyMODINIT_FUNC
inituinput(void)
{
    PyObject *m;
    m = Py_InitModule("uinput",SwigMethods);
    if (m == NULL)
       return;
    SWIG_init();
}
%}


// The nice wrapper code
%pythoncode %{
__doc__ = """
Handles quite a bit of the back to uinput.

The struct interface is used frequently in this module, and is as follows:
class struct(object):
	@classmethod
	def size(cls):
		Return the size (in bytes) used by this struct when packed.
	
	@classmethod
	def unpack(cls, data):
		Creates a new instance based on the data. Reverse of pack().
	
	def pack(self):
		Packs the struct into a str and returns it. Reverse of unpack().
"""

import sys, os, stat, struct, array
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
	"""
	Acts as an "object stream", meaning that instead of reading bytes, you read 
	objects.
	
	Note that objects must follow the struct interface.
	"""
	__slots__ = '_fileobj','__weakref__'
	def __init__(self, fn, *pargs):
		if isinstance(fn, int):
			self._fileobj = os.fdopen(fn, *pargs)
		elif isinstance(fn, basestring):
			self._fileobj = open(fn, *pargs)
		else:
			self._fileobj = fn
	
	def write(self, obj):
		"""e.write(obj) -> None
		Packs and writes an object.
		"""
		if hasattr(obj, 'pack'):
			self._fileobj.write(obj.pack())
			self._fileobj.flush()
		else:
			raise TypeError, "obj must have a pack() method."
	
	def read(self, type):
		"""e.read(type) -> type
		Reads data and unpacks it into a struct.
		"""
		if hasattr(type, '__len__'):
			s = type.__len__()
		elif hasattr(type, 'size'):
			s = type.size()
		data = self._fileobj.read(s)
		return type.unpack(data)
	
	def ioctl(self, op, *pargs):
		"""e.ioctl(int, ...) -> something
		Calls fcntl.ioctl() using the backing stream.
		"""
		return ioctl(self._fileobj, op, *pargs)
	
	def close(self):
		"""e.close() -> None
		Closes the backing stream.
		"""
		self._fileobj.close()
	
	def flush(self):
		"""e.flush() -> None
		Flushes the stream.
		"""
		# Should be redundent
		self._fileobj.flush()
	
	def iter(self,type):
		"""
		Like iter(), but needs an initial type to load. To change the type, use 
		.send() (PEP 342).
		"""
		while True: # Ends when something raises an error
			ntype = yield self.read(type)
			if ntype is not None: type = ntype
	
	def __enter__(self):
		"""
		Opens the stream.
		"""
		self._fileobj.__enter__()
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		"""
		Closes the stream.
		"""
		self._fileobj.__exit__(exc_type, exc_val, exc_tb)
	
#	def __getattr__(self, attr):
#		return getattr(self._fileobj, attr)
	
	# Convenience functions to get info on the device
	def dev_id(self):
		"""e.dev_id() -> input_id
		Queries the device for its input_id struct.
		"""
		rv = array.array('H', [0]*4)
		self.ioctl(EVIOCGID, rv, True)
		bits = rv
		return input_id(
				bustype=bits[ID_BUS],
				vendor=bits[ID_VENDOR], 
				product=bits[ID_PRODUCT],
				version=bits[ID_VERSION])
	
	def dev_version(self):
		"""e.dev_version() -> int
		Queries the device for its version.
		"""
		rv = array.array("i", [0])
		self.ioctl(EVIOCGVERSION, rv, True)
		return rv[0]
	
	def dev_name(self):
		"""e.dev_name() -> str
		Queries the device for name.
		"""
		rv = array.array("c", ['\0']*256)
		self.ioctl(EVIOCGNAME(len(rv)), rv, True)
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
		sfmt = 'L', [0] * NBITS(KEY_MAX)
		bit = [None] * uinput.EV_MAX
		buf = array.array(*sfmt)
		self.ioctl(EVIOCGBIT(0, EV_MAX), buf, True)
		bit[0] = list(buf)
		for i in xrange(1,EV_MAX):
			if test_bit(i, bit[0]):
				buf = array.array(*sfmt)
				try:
					self.ioctl(EVIOCGBIT(i, KEY_MAX), buf, True);
				except: pass
				bit[i] = list(buf)
				rvbits[i] = [j for j in xrange(KEY_MAX) if test_bit(j, bit[i])]
		return rvbits
	
	def dev_ranges(self):
		"""e.dev_ranges() -> {int: (int,int,int,int,int), ...}
		Queries the range of each of the absolute axis.
		
		The keys are one of the ABS_* constants.
		The values are (value, min, max, fuzz, flat).
		"""
		bits = self.dev_bits()
		if EV_ABS not in bits: return {}
		rv = {}
		for j in bits[EV_ABS]:
			abs = array.array("i", [0]*5)
			self.ioctl(EVIOCGABS(j), abs, True)
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
	Just like EvdevStream, but with some convenience methods for uinput. Also 
	tries to make errors nicer.
	
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
		"""e.ioctl(int, ...) -> something
		Calls fcntl.ioctl() using the backing stream.
		"""
		rv = super(UinputStream, self).ioctl(op, *pargs)
		if op == UI_DEV_CREATE:
			self._devcreated = True
		elif op == UI_DEV_DESTROY:
			self._devcreated = False
		return rv
	
	def close(self):
		"""e.close() -> None
		Closes the backing stream.
		"""
		super(UinputStream, self).close()
		self._devcreatable = False
		self._devcreated = False
	
	def write(self, obj):
		"""e.write(obj) -> None
		Packs and writes an object.
		"""
		super(UinputStream, self).write(obj)
		if isinstance(obj, uinput_user_dev): self._devcreatable = True
	
	def create(self):
		"""u.create() -> contextmanager
		Actually creates the devices, locking events. Returns a context manager 
		which will call destroy() automagically.
		"""
		if not self._devcreatable:
			raise ValueError, "Need to define events before creating the device."
		if self._devcreatable 
			if not self._devcreated:
				self.ioctl(UI_DEV_CREATE)
			else:
				raise ValueError, "Already created the device."
	
	def destroy(self):
		"""u.destroy() -> None
		Destroys the device created by create()
		"""
		if not self._devcreatable:
			# WTF???
			raise ValueError, "Device not yet created. Nothing to destroy. (WTF?)"
		if self._devcreated:
			self.ioctl(UI_DEV_DESTROY)
		else:
			raise ValueError, "Device not yet created. Nothing to destroy."
	
	def __enter__(self):
		return super(UinputStream, self).__enter__()
			
	def __exit__(self, exc_type, exc_val, exc_tb):
		return super(UinputStream, self).__exit__(exc_type, exc_val, exc_tb)

if __name__ == '__main__':
	uud = uinput_user_dev(name="Saitek Magic Bus", ff_effects_max=0, absmax=[1]*(ABS_MAX+1))
	print repr(uud)
	print uud.__dict__
	print hex(int(uud.this))
	print dir(uud.this)
	print dir(timeval)
	print uud.absmax
	print uud.absmin
	print repr(input_event().pack())
%}
