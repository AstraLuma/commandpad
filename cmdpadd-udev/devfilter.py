#-*- coding: utf-8 -*-
"""
Provides the basic framework for a device filter.
"""
from __future__ import with_statement
import uinput, udev, sys

class Filter(object):
	"""
	Fill out these attributes:
	* __dev_name__
	* __dev_bus__
	* __dev_vendor__
	* __dev_product__
	* __dev_version__
	"""
	
	def __events__(self,cur=None):
		"""f.__events__(cur=None) -> dict
		Returns a dict of {int: [int, ...], ...}, where the keys are the event
		types (uinput.EV_KEY et al) and the sequence is of events (uinput.KEY_* et 
		al).
		
		The optional argument is for a dict of the same form from the device(s) 
		we read from.
		"""
		return cur
	
	def test(self, event):
		"""f.test(uinput.input_event) -> boolean
		Acts as the filter. Default always returns True.
		"""
		return True
	
	def filter(self, event):
		"""f.filter(uinput.input_event) -> uinput.input_event
		Modifies the event for passing on. Return the event to pass.
		Default just returns what's passed in
		"""
		return event
	
	def __iter__(self):
		"""f.__iter__() -> iter(uinput.input_event->uinput.input_event|None)
		Filters events. Should be a generator which receives events from yield.
		(PEP 342)
		
		The default calls test() and filter() for each event. Overload if you 
		wish.
		"""
		event = yield
		while True:
			if self.test(event):
				event = yield self.filter(event)

def DevFilter(name, vendor, product, version, **kwargs):
	"""
	A decorator for generator functions that creates the necessary class.
	"""
	name = name[:80]
	vendor &= 0xFFFF
	product &= 0xFFFF
	version &= 0xFFFF
	
	events = {}
	
	upper = lambda s: s.upper() if isinstance(s, basestring) else s
	
	for k, l in kwargs.iteritems():
		k = k.upper()
		if k[:3] != 'EV_': k = 'EV_'+k
		t = getattr(uinput, k)
		p = k[3:]+'_'
		l = [getattr(uinput, a) if isinstance(a, basestring) else a for a in 
			( i if not isinstance(i, basestring) or i.startswith(p) else p+i 
				for i in map(upper, l) )]
		events[t] = l
	
	def _(func):
		class _DevFilter(Filter):
			__dev_name__ = name
			__dev_bus__ = 0
			__dev_vendor__ = vendor
			__dev_product__ = product
			__dev_version__ = version
			__events = events
			__events__ = lambda self,cur=None: self.__events
			__func = staticmethod(func)
			def __iter__(self):
				return self.__func()
			def __call__(self):
				return self.__func()
		_DevFilter.__name__ = func.__name__
		#_DevFilter.__doc__ = func.__doc__
		_DevFilter.__module__ = func.__module__
		return _DevFilter()
	return _

def main(evfilter, idevice, odevice, eclass=uinput.input_event):
	"""main(generator, string|file|something) -> None
	Actually does the work.
	"""
	with udev.UidevStream(odevice, 'w') as uidev:
		with udev.EvdevStream(idevice, 'r') as rdev:
			uidev.write(udev.uinput_user_dev(name=evfilter.__dev_name__,
				id=udev.input_id(
					bustype=evfilter.__dev_bus__,
					vendor=evfilter.__dev_vendor__, 
					product=evfilter.__dev_product__,
					version=evfilter.__dev_version__)))
			SETBITS = {
				uinput.EV_ABS  : uinput.UI_SET_ABSBIT,
				uinput.EV_FF   : uinput.UI_SET_FFBIT,
				uinput.EV_KEY  : uinput.UI_SET_KEYBIT,
				uinput.EV_LED  : uinput.UI_SET_LEDBIT,
				uinput.EV_MSC  : uinput.UI_SET_MSCBIT,
				uinput.EV_REL  : uinput.UI_SET_RELBIT,
				uinput.EV_SND  : uinput.UI_SET_SNDBIT,
				uinput.EV_SW   : uinput.UI_SET_SWBIT,
				}
			for etype, events in evfilter.__events__(rdev.dev_bits()).iteritems():
				uidev.ioctl(uinput.UI_SET_EVBIT, etype)
				set = SETBITS[etype]
				for ev in events:
					uidev.ioctl(set, ev)
			uidev.ioctl(uinput.UI_DEV_CREATE)
			
			fiter = iter(evfilter)
			moreinit = fiter.next() # Get to the first yield, its result is more init
			if moreinit is not None:
				for i in moreinit:
					uidev.ioctl(*i)
			with uidev:
				def _run_event(ev):
					if ev is not None:
						uidev.write(ev)
				try:
					for event in rdev.iter(eclass):
						try:
							nev = fiter.send(event)
						except StopIteration:
							break
						else:
							_run_event(nev)
					else:
						map(_run_event, fiter) # Flush the filter
				except: # Pass exceptions along to the iterator
					try:
						nev = fiter.throw(*sys.exc_info())
					except StopIteration:
						pass
					else:
						_run_event(nev)
						map(_run_event, fiter) # Flushing
				finally:
					fiter.close()

