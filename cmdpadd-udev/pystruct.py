#-*- coding: utf-8 -*-
"""
Defines a structure mixin class.
"""
import struct
__all__ = 'Struct',


_WORDSIZE = 2**(8*struct.calcsize('P'))

def _applyargs(names, pargs, kwargs, funcname):
	"""
	Emulates Python's rules of argument resolution.
	See <http://docs.python.org/ref/calls.html>
	"""
	empty = object() # We don't use python objects because they could be the object
	slots = dict(zip(names, [empty]*len(names)))
	if len(pargs)+len(kwargs) > len(names):
		raise TypeError, "%s() takes exactly %i arguments (%i given)" % (funcname, len(names), len(pargs)+len(kwargs)
	for name,arg in zip(names, pargs):
		slots[name] = args
	for name, value in kwargs.iteritems():
		if name not in slots:
			raise TypeError, "%s() got an unexpected keyword argument %r" % (funcname, name)
		elif slots[name] is not empty:
			raise TypeError,  "%s() got multiple values for the keyword argument %r" % (funcname, name)
		slots[name] = value
	for k,v in slots.items(): # Not iteritems() because we're going to modify it
		if v is empty:
			del slots[k]
	return slots

# Alternate version by KirkMcDonald <http://deadbeefbabe.org/paste/6065>:
#def _applyargs(f_args, args, kwargs, defaults={}):
#	a = dict(zip(f_args, args))
#	f_args = set(f_args[len(args):])
#	for k, v in kwargs.iteritems():
#		assert k in f_args, "Invalid keyword argument!"
#		a[k] = v
#		f_args.remove(k)
#	for i in f_args:
#		a[i] = self.defaults[i]
#	return a


def _checkvalue(typ, value):
	global _WORDSIZE
	try:
		if typ == 'c': return len(str(value)) == 1
		#int 8
		elif typ == 'b': return -0x80 <= int(value) <= 0x7F
		elif typ == 'B': return 0 <= int(value) <= 255
		#int 16
		elif typ == 'h': return -0x8000 <= int(value) <= 0x7FFF
		elif typ == 'H': return 0 <= int(value) <= 0xFFFF
		#int 24
		elif typ == 'i': return -0x800000 <= int(value) <= 0x7FFFFF
		elif typ == 'I': return 0 <= long(value) <= 0xFFFFFF
		#int 32
		elif typ == 'l': return -0x80000000 <= int(value) <= 0x7FFFFFFF
		elif typ == 'L': return 0 <= long(value) <= 0xFFFFFFFF
		#int 64
		elif typ == 'q': return -2**63 <= long(value) <= 2**63-1
		elif typ == 'Q': return 0 <= long(value) <= 2**64-1
		#floats
		elif typ == 'f': return -3.4e38 <= float(value) <= 3.4e38
		elif typ == 'd': return -1.7976931348623157e308 <= float(value) <= 1.7976931348623157e308
		# Other types
		elif typ[-1] == 's': return len(str(value)) == int(typ[:-1])
		elif typ[-1] == 'p':
			c = int(typ[:-1])
			return len(str(value)) == c and 0 <= c <= 255
		elif typ == 'P': return 0 <= long(value) < _WORDSIZE
	except (ValueError, TypeError), err:
		return False

class _FieldDescriptor(object):
	"""
	(Based on utils.rwprop from pycms.)
	"""
	__slots__ = '_prop', '_type', '__weakref__'
	def __new__(cls, prop, typ, doc=None):
		cls2 = type('_'+cls.__name__, (cls,), {'__doc__':doc})
		self = super(_FieldDescriptor, cls2).__new__(cls2)
		self._prop = prop
		self._type = typ
		return self
	def __get__(self, instance, owner):
		if instance is not None:
			return instance.__dict__[self._prop]
		else:
			raise AttributeError, "Can't get at the class attribute."
	def __set__(self, instance, value):
		if not _checkvalue(self._type, value):
			raise ValueError, "Wrong type or out of range. Type is "+self._type
		instance.__dict__[self._prop] = value
		

class _StructMetaclass(type):
	_struct = None
	def __new__(cls, name, bases, dct):
		format = ''
		fields = dct['__fields__']
		for nam,typ,doc in fields:
			dct[name] = _FieldDescriptor(nam,typ,doc)
			format += typ
		self = super(_StructMetaclass, cls).__new__(cls, name, bases, dct)
		self._struct = struct.Struct(format)
		return self
	def __len__(cls):
		return cls._struct.size

class Struct(object):
	"""
	A mixin that allows python classes to behave somewhat like C structures.
	
	Defines some methods that allows one to pass this to C functions.
	"""
	# Incidentally, __dict__ is usually the fields only.
	__metaclass__ = _StructMetaclass
	__fields__ = [] # So that the metaclass doesn't freak
	
	def __init__(self, *pargs, **kwargs):
		args = _applyargs(zip(*self.__fields__)[0], pargs, kwargs, type(self).__name__)
		for name,typ,_ in self.__fields__:
			if name in args:
				value = args[name]
			else: # Defaults
				if typ in 'bBhHiIlLqQP':
					value = 0
				elif typ in 'fd':
					value = 0.0
				elif typ == 'c':
					value = '\0'
				elif typ[-1] in 'sp':
					value = ""
			print name
			setattr(self, name, value)
	
	def __repr__(self):
		return "%s(%s)" % (type(self).__name__, ', '.join(("%s=%r" % i for i in self)))
	
	def __iter__(self):
		"""
		Yields (name, value) pairs in order.
		"""
		for name,_,_ in self.__fields__:
			yield name, getattr(self, name)
	
	def pack(self, order=''):
		"""s.pack([string]) -> string
		Returns a binary string of this structure's raw data, a la 
		struct.pack().
		
		order can be '@', '=', '<', '>', or '!'; see the struct module 
		documentation for what these mean.
		"""
		return struct.pack(order+self._struct.format, *(getattr(self, n) for n,_,_ in self.__fields__))
	
	@classmethod
	def unpack(cls, data, order=''):
		"""Struct.unpack(string) -> Struct
		Creates a new instance initialized to the given data, via 
		struct.unpack().
		
		order can be '@', '=', '<', '>', or '!'; see the struct module 
		documentation for what these mean.
		
		To get the needed length of the string, use len(Struct)
		
		Do not call on Struct directly; call on a subclass.
		"""
		return cls(struct.unpack(order+cls._struct.format, data))

