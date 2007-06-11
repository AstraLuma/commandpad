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
Provides some utilities for clients of the command pad service.

Note that for signals to be received, a mainloop must be ran. There are 
functions to deal with this. In addition, threading is used. gobject and 
dbus.main.glib are init'd in threads by this package. Make sure that you do not
violate this.

The dbus.mainloop.glib.DBusGMainLoop is set as default. If you wish to change 
this, do so before instantiating any CommandPadListener or , or pass it as the 
"mainloop" keyword argument to it.
"""
from __future__ import absolute_import
import dbus, dbus.mainloop.glib, gobject, threading

gobject.threads_init()
dbus.mainloop.glib.threads_init()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

from commandpad.device import BUTTON_1, BUTTON_2, BUTTON_3, BUTTON_4, BUTTON_5, \
                       BUTTON_6, BUTTON_7, BUTTON_8, BUTTON_9, BUTTON_A, \
                       BUTTON_B, buttonName, modeName, MODE_A, MODE_B

__all__ = 'CommandPadListener', 'BUTTON_1', 'BUTTON_2', \
          'BUTTON_3', 'BUTTON_4', 'BUTTON_5', 'BUTTON_6', 'BUTTON_7', \
          'BUTTON_8', 'BUTTON_9', 'BUTTON_A', 'BUTTON_B', 'buttonName', \
          'modeName', 'MODE_A', 'MODE_B', 'startMainLoop', 'joinMainLoop', \
          'quitMainLoop', 'runMainLoop', 'CPManagerListener'

## Class attribute
MainLoop = gobject.MainLoop()

def startMainLoop(cls):
	"""
	Runs the DBus main loop in a new thread.
	"""
	global _thread, MainLoop
	_thread = threading.Thread(target=MainLoop.run, name="dbus-mainloop")
	_thread.start()
	
def joinMainLoop(cls, *p, **kw):
	"""
	Calls the join() method on the main loop thread created by startMainLoop()
	"""
	global _thread
	_thread.join(*p, **kw)

def quitMainLoop(cls):
	"""
	Tells the main loop thread started by startMainLoop() to stop.
	"""
	global MainLoop
	MainLoop.quit()

def runMainLoop(cls):
	"""
	Just runs the main loop instead of threading it.
	"""
	global MainLoop
	try:
		MainLoop.run()
	except KeyboardInterrupt:
		pass

class CPManagerListener(object):
	"""
	Interfaces with DBus and CommandPadD.
	
	The Add and Remove callbacks have the same signature:
	   def event(manager, object)
	* manager - The manager that's doing the calling
	* object - The device that was added/removed (a CommandPadListener)
	"""
	__add = None
	__remove = None
	Add = property((lambda s: s.__add), (lambda s,v: setattr(s, '_CPManagerListener__add',v)), doc="""The callback for addDevice events.""")
	Remove = property((lambda s: s.__remove), (lambda s,v: setattr(s, '_CPManagerListener__remove',v)), doc="""The callback for removeDevice events.""")
	__bus = None
	__receiver = None
	__listeners = None
	__mainloop = None
	__object = None
	def __init__(self, add=None, remove=None, mainloop=None):
		"""CPManagerListener(mainloop=None) -> CommandPadListener
		Creates a CommandPadListener.
		* mainloop - the mainloop object to pass to dbus.SystemBus()
		Note that as soon as Remove() returns, the CommandPadListener is 
		destroyed.
		"""
		self.__listeners = {}
		self.__mainloop = mainloop
		if mainloop is None:
			self.__bus = dbus.SystemBus()
		else:
			self.__bus = dbus.SystemBus(mainloop=mainloop)
		self.__receiver = self.__bus.add_signal_receiver(self.__signal, 
		       None, None, 'com.astro73.saitek.CPManager', None,
		       member_keyword='member', path_keyword='path')
		self.__object = self.__bus.get_object('com.astro73.saitek.CommandPad', "/com/astro73/saitek/CPManager")
	
	def close(self):
		if self.__listeners is not None:
			self.__receiver.remove()
		self.__receiver = None
		self.__add = None
		self.__remove = None
		self.__bus = None
		self.__device = None
		self.__filter = None
		self.__mainloop = None
		self.__object = None
		if self.__listeners is not None:
			for v in self.__listeners.values():
				v.close()
		self.__listeners = None
		
	def __del__(self):
		self.close()
	
	def __signal(self, dev, member, path):
		if member == 'addDevice' and callable(self.Add):
			if dev not in self.__listeners:
				self.__listeners[dev] = CommandPadListener(device=dev, mainloop=self.__mainloop)
			self.Add(self, self.__listeners[dev])
		elif member == 'removeDevice' and callable(self.Remove):
			l = self.__listeners.pop(dev)
			self.Remove(self, l)
			l.close()
	
	def Devices(self):
		"""
		Returns a list of listeners for all the devices the daemon recognizes. 
		Also synchronizes our list of devices with the daemon's.
		"""
		devs = self.__object.Devices()
		rv = []
		for d in self.__listeners.keys():
			if d not in devs:
				l = self.__listeners.pop(dev)
				self.Remove(self, l)
				l.close()
		for dev in devs:
			if dev not in self.__listeners:
				self.__listeners[dev] = CommandPadListener(device=dev, mainloop=self.__mainloop)
				self.Add(self, self.__listeners[dev])
			rv.append(self.__listeners[dev])
		return rv

class CommandPadListener(object):
	"""
	Interfaces with DBus and CommandPadD.
	
	The ButtonUp and ButtonDown callbacks have the same signature:
	   def event(path, button, mode)
	* path - The path of the device file (technically, the DBus object)
	* button - The button pushed (one of the BUTTON_* constants)
	* mode - the mode the pad is currently in (a mix of the MODE_* constants)
	The ModeChange callback is slightly different:
	   def event(oldmode, newmode)
	* path - The path of the device file (technically, the DBus object)
	* oldmode - The mode set before the button was pushed
	* newmode - The mode now set
	"""
	__up = None
	__down = None
	__mode = None
	__filter = True
	## You know, this assignment thing is a pain
	ButtonUp = property((lambda s: s.__up), (lambda s,v: setattr(s, '_CommandPadListener__up',v)), doc="""The callback for ButtonUp events.""")
	ButtonDown = property((lambda s: s.__down), (lambda s,v: setattr(s, '_CommandPadListener__down',v)), doc="""The callback for ButtonUp events.""")
	ModeChange = property((lambda s: s.__mode), (lambda s,v: setattr(s, '_CommandPadListener__mode',v)), doc="""The callback for ButtonUp events.""")
	Device = property((lambda s: s.__device), doc="""The specific device to listen to.""")
	Filter = property((lambda s: s.__filter), (lambda s,v: setattr(s, '_CommandPadListener__filter',v)), doc="""Do we filter out the mode buttons?""")
	__bus = None
	__receiver = None
	__device = None
	self.__object = None
	def __init__(self, up=None, down=None, mode=None, device=None, mainloop=None):
		"""CommandPadListener(up=None, down=None, mode=None, device=None, mainloop=None) -> CommandPadListener
		Creates a CommandPadListener.
		* up - the ButtonUp handler or None
		* down - the ButtonDown handler or None
		* mode - the ModeChange handler or None
		* device - the specific device to listen to or None
		* mainloop - the mainloop object to pass to dbus.SystemBus()
		"""
		if up is not None:
			self.ButtonUp = up
		if down is not None:
			self.ButtonDown = down
		if mode is not None:
			self.ModeChange = mode
		self.__device = device
		if mainloop is None:
			self.__bus = dbus.SystemBus()
		else:
			self.__bus = dbus.SystemBus(mainloop=mainloop)
		self.__receiver = self.__bus.add_signal_receiver(self.__signal, 
		       None, None, 'com.astro73.saitek.CommandPad', self.__device,
		       member_keyword='member', path_keyword='path')
		if self.__device:
			self.__object = self.__bus.get_object('com.astro73.saitek.CommandPad', self.__device)
			self.getMode = self._getMode
			self.getDevice = self._getDevice
	
	def close(self):
		if hasattr(self.__receiver, 'remove'):
			self.__receiver.remove()
		self.__receiver = None
		self.__up = None
		self.__down = None
		self.__mode = None
		self.__bus = None
		self.__device = None
		self.__filter = None
		self.__object = None
		
	def __del__(self):
		self.close()
	
	def _filter(self, button, mode=None):
		return (self.Filter and button not in (BUTTON_A, BUTTON_B)) or \
		       (not self.Filter)
	
	def __signal(self, *pargs, **kw):
		if 'member' not in kw: return
		member = kw['member']
		path = kw['path']
		if member == 'ButtonUp' and callable(self.ButtonUp):
			if self._filter(*pargs): self.ButtonUp(path, *pargs)
		elif member == 'ButtonDown' and callable(self.ButtonDown):
			if self._filter(*pargs): self.ButtonDown(path, *pargs)
		elif member == 'ModeChange' and callable(self.ModeChange):
			self.ModeChange(path, *pargs)
	
	def _getDevice(self):
		return self.__object.getDevice()
	
	def _getMode(self):
		return self.__object.getMode()
	
if __name__ == '__main__':
	import sys
	def up(path, button, mode):
		print "Up: %s from %s" % (buttonName(button,mode), path)
		sys.stdout.flush()
	
	def down(path, button, mode):
		print "Down: %s from %s" % (buttonName(button,mode), path)
		sys.stdout.flush()
	
	def mode(path, old, new):
		print "Mode: %s->%s from %s" % (modeName(old) or "(default)", modeName(new) or "(default)", path)
		sys.stdout.flush()
	
	print "Instantiate"
	cpl = CommandPadListener(up, down, mode)
	print "Run"
	runMainLoop()

