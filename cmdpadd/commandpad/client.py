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

Note that for signals to be received, a mainloop must be ran. 
CommandPadListener has methods to deal with this. In addition, threading is
used. gobject and dbus.main.glib are init'd in threads by this package. Make
sure that you do not violate this.

The dbus.mainloop.glib.DBusGMainLoop is set as default. If you wish to change 
this, do so before instantiating any CommandPadListener, or pass it as the 
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
          'modeName', 'MODE_A', 'MODE_B'

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
	## Class attribute
	MainLoop = gobject.MainLoop()
	
	__up = None
	__down = None
	__mode = None
	__filter = True
	## You know, this assignment thing is a pain
	ButtonUp = property((lambda s: s.__up), (lambda s,v: setattr(s, '_CommandPadListener__up',v)), doc="""The callback for ButtonUp events.""")
	ButtonDown = property((lambda s: s.__down), (lambda s,v: setattr(s, '_CommandPadListener__down',v)), doc="""The callback for ButtonUp events.""")
	ModeChange = property((lambda s: s.__mode), (lambda s,v: setattr(s, '_CommandPadListener__mode',v)), doc="""The callback for ButtonUp events.""")
	Filter = property((lambda s: s.__filter), (lambda s,v: setattr(s, '_CommandPadListener__filter',v)), doc="""Do we filter out the mode buttons?""")
	__bus = None
	__thread = None
	__receiver = None
	def __init__(self, up=None, down=None, mode=None, mainloop=None):
		"""CommandPadListener(up=None, down=None, mode=None, mainloop=None) -> CommandPadListener
		Creates a CommandPadListener.
		* up - the ButtonUp handler or None
		* down - the ButtonDown handler or None
		* mode - the ModeChange handler or None
		* mainloop - the mainloop object to pass to dbus.SystemBus()
		"""
		if up is not None:
			self.ButtonUp = up
		if down is not None:
			self.ButtonDown = down
		if mode is not None:
			self.ModeChange = mode
		print "Creating Bus"
		if mainloop is None:
			self.__bus = dbus.SystemBus()
		else:
			self.__bus = dbus.SystemBus(mainloop=mainloop)
		print "\tbus:", repr(self.__bus)
		print "Adding signal handler"
		self.__receiver = self.__bus.add_signal_receiver(self.__signal, 
		       None, None, 'com.astro73.saitek.CommandPad', None,
		       member_keyword='member', path_keyword='path')
		print "\tval:", repr(self.__receiver)
	
	def __del__(self):
		self.__receiver.remove()
	
	def __filter(self, button, mode=None):
		return (self.Filter and button not in (BUTTON_A, BUTTON_B)) or \
		       (not self.Filter)
	
	def __signal(self, *pargs, **kw):
		if 'member' not in kw: return
		member = kw['member']
		path = kw['path']
		if member == 'ButtonUp' and callable(self.ButtonUp):
			if self.__filter(*pargs): self.ButtonUp(path, *pargs)
		elif member == 'ButtonDown' and callable(self.ButtonDown):
			if self.__filter(*pargs): self.ButtonDown(path, *pargs)
		elif member == 'ModeChange' and callable(self.ModeChange):
			self.ModeChange(path, *pargs)
	
	@classmethod
	def startMainLoop(cls):
		"""
		Runs the DBus main loop in a new thread.
		"""
		cls.__thread = threading.Thread(target=cls.MainLoop.run, name="dbus-mainloop")
		cls.__thread.start()
	
	@classmethod
	def joinMainLoop(cls, *p, **kw):
		"""
		Calls the join() method on the main loop thread created by startMainLoop()
		"""
		cls.__thread.join(*p, **kw)
	
	@classmethod
	def quitMainLoop(cls):
		"""
		Tells the main loop thread started by startMainLoop() to stop.
		"""
		cls.MainLoop.quit()
	
	@classmethod
	def runMainLoop(cls):
		"""
		Just runs the main loop instead of threading it.
		"""
		try:
			cls.MainLoop.run()
		except KeyboardInterrupt:
			pass

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
	CommandPadListener.runMainLoop()

