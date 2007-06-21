#!/usr/bin/python
# -*- encoding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License with
# the Debian GNU/Linux distribution in file /usr/share/common-licenses/GPL;
# if not, write to the Free Software Foundation, Inc.,  51 Franklin St, 
# Fifth Floor, Boston, MA  02111-1307  USA
"""
Handles the reading and parsing of the device file.
"""
#from __future__ import with_statement
#from __future__ import division
import struct, time
__all__ = 'DevEvent', 'Device', 'CPEvent', 'CommandPad', 'BUTTON_1', \
          'BUTTON_2', 'BUTTON_3', 'BUTTON_4', 'BUTTON_5', 'BUTTON_6', \
          'BUTTON_7', 'BUTTON_8', 'BUTTON_9', 'BUTTON_A', 'BUTTON_B', \
          'buttonName', 'modeName', 'MODE_A', 'MODE_B', 'MODES'

# typedef long time_t, suseconds_t; // 4B
# struct input_event {
# 	struct timeval {
# 		time_t      tv_sec;         /* seconds */
# 		suseconds_t tv_usec;        /* microseconds */
# 	} time; // 8B
# 	__u16 type; // 2B
# 	__u16 code; // 2B
# 	__s32 value; // 4B
# }; // 16B

class DevEvent(object):
	"""
	A single event read from an event device.
	"""
	__sec = 0
	__usec = 0
	__type = 0
	__code = 0
	__value = 0
	
	sec   = property((lambda s: s.__sec  ), doc="""Number of seconds this occured""")
	usec  = property((lambda s: s.__usec ), doc="""The microseconds of the timestamp""")
	type  = property((lambda s: s.__type ), doc="""The type of event""")
	code  = property((lambda s: s.__code ), doc="""The input button/axis/whatever""")
	value = property((lambda s: s.__value), doc="""The current value""")
	
	time = property((lambda s: s.sec + s.usec / 1e6), doc="""The timestamp, as floating-point seconds""")
	
	def __new__(cls, sec, type, code, value, usec=None):
		self = super(DevEvent, cls).__new__(cls)
		if usec is None:
			self.__sec = int(sec)
			self.__usec = int(sec * 10e6 - self.sec*10e6)
		else:
			self.__sec = int(sec)
			self.__usec = int(usec)
		self.__type = type
		self.__code = code
		self.__value = value
		return self
	
	def __hash__(self):
		return hash((self.time, self.type, self.code, self.value))
	
	def __cmp__(self, other):
		try:
			c = cmp(self.time, other.time)
			if c != 0: return c
			c = cmp(self.type, other.type)
			if c != 0: return c
			c = cmp(self.code, other.code)
			if c != 0: return c
			c = cmp(self.value, other.value)
			if c != 0: return c
		except AttributeError:
			return NotImplemented
	
	def __repr__(self):
		return "%s(%r, %r, %r, %r)" % (self.__class__.__name__, self.time, self.type, self.code, self.value)
	
class Device(object):
	"""
	Class to process /dev/input/event* files.
	"""
	__file = None
	__FORMAT = "llHHl"
	__LENGTH = struct.calcsize(__FORMAT)
	
	def __init__(self, fn):
		self.__file = file(fn, 'rb')
	
	def __del__(self):
		self.__file.close()
		
	def __parsePacket(self, packet):
		"""
		http://lxr.linux.no/source/include/linux/input.h#L26
		"""
		bits = struct.unpack(self.__FORMAT, packet)
		return DevEvent(sec=bits[0], usec=bits[1], type=bits[2], code=bits[3], value=bits[4])
	
	def readEvent(self):
		"""
		Read 1 event.
		"""
		return self.__parsePacket(self.__file.read(self.__LENGTH))
	
	def __enter__(self):
		return self
	
	def __exit__(self, *p):
		pass
	
	def __iter__(self):
		"""
		Reads events forever
		"""
		while True:
			yield self.readEvent()

BUTTON_1, BUTTON_2, BUTTON_3, BUTTON_4, BUTTON_5, BUTTON_6, BUTTON_7, BUTTON_8, \
          BUTTON_9, BUTTON_A, BUTTON_B = range(11)
MODE_A = 0x1
MODE_B = 0x2
MODES = frozenset([0, MODE_A, MODE_B, MODE_A|MODE_B])

def modeName(mode):
	return ("A" if mode & 0x1 else "") + ("B" if mode & 0x2 else "")

def buttonName(btn,mode=None):
	"""
	Returns the name of the button, given the BUTTON_* code
	"""
	m = ""
	if mode:
		m = modeName(mode)
	if len(m) > 0: m = m+":"
		
	if btn == BUTTON_A:
		return m+"Mode A"
	elif btn == BUTTON_B:
		return m+"Mode B"
	else:
		return m+str(btn + 1)

class CPEvent(DevEvent):
	"""
	An extension of DevEvent to handle the specifics of the command pad.
	"""
	__MIN = 304
	__mode = 0
	
	mode = property((lambda s: s.__mode), doc="""The mode of this button""")
	
	button = property((lambda s: s.code - s.__MIN), doc="""The button this event relates to. See the BUTTON_* constants""")
	pushed = property((lambda s: bool(s.value)), doc="""Is the button pushed?""")
	garbage = property((lambda s: s.type == 0), doc="""Is this event garbage?""")
	
	def __new__(cls, *p, **kw):
		if len(p) == 1:
			v = p[0]
			self = super(CPEvent, cls).__new__(cls, sec=v.sec, usec=v.usec, type=v.type, code=v.code, value=v.value)
		else:
			self = super(CPEvent, cls).__new__(cls, *p)
		if 'mode' in kw:
			self.__mode = int(kw['mode']) & 0x3
		return self
	
	def __unicode__(self):
		t = u"[%s.%i]" % (time.strftime(u"%Y-%m-%d %H:%M:%S", time.gmtime(self.sec)), self.usec)
		if self.garbage:
			return u"%s garbage" % t
		else:
			push = u"down" if self.pushed else u"up"
			mode = ("A" if self.mode & 0x1 else "") + ("B" if self.mode & 0x2 else "")
			if len(mode) > 0: mode += ":"
			return u"%s %s%s (%s)" % (t, mode, buttonName(self.button), push)
	
	def __str__(self):
		return str(unicode(self))

class CommandPad(Device):
	"""
	An extension of Device to handle the specifics of the command pad.
	"""
	__mode = 0
	mode = property((lambda s: s.__mode), doc="""A bitfield of the current mode, in the form of 0bBA""")
	def readEvent(self):
		"""
		Read 1 event.
		"""
		rv = CPEvent(super(CommandPad, self).readEvent(), mode=self.mode)
		while rv.garbage:
			rv = CPEvent(super(CommandPad, self).readEvent(), mode=self.mode)
		
		if rv.pushed and rv.button == BUTTON_A:
			self.__mode ^= 0x1
		elif rv.pushed and rv.button == BUTTON_B:
			self.__mode ^= 0x2
		
		return rv
	

if __name__ == '__main__':
	import os
	DEV_FILE = '/dev/input/event3'
	if 'CPDEV' in os.environ: DEV_FILE = os.environ['CPDEV']
	for data in CommandPad(DEV_FILE):
		print data
