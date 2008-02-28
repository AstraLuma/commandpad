#-*- coding: utf-8 -*-
"""
Allows for control of LEDs. May require root.
"""

from linuxkd import getled, setled, LED_SCR, LED_NUM, LED_CAP
from fcntl import ioctl
import os, array

__all__ = 'LEDs',

class LEDs(object):
	__slots__ = '_fd','__weakref__'
	def __init__(self):
		self._fd = os.open('/dev/console', os.O_NOCTTY)
	
	def __del__(self):
		os.close(self._fd)
		del self._fd
	
	def getCaps(self):
		return getled(self._fd, LED_CAP)
	
	def setCaps(self, value):
		setled(self._fd, LED_CAP, value)
	
	def getNum(self):
		return getled(self._fd, LED_NUM)
	
	def setNum(self, value):
		setled(self._fd, LED_NUM, value)
	
	def getScroll(self):
		return getled(self._fd, LED_SCR)
	
	def setScroll(self, value):
		setled(self._fd, LED_SCR, value)
	
	caps   = property(getCaps  , setCaps  , doc="""The state of the caps lock LED""")
	num    = property(getNum   , setNum   , doc="""The state of the num lock LED""")
	scroll = property(getScroll, setScroll, doc="""The state of the scroll lock LED""")

if __name__ == '__main__':
	from sys import stdin
	lights = LEDs()
	try:
		while True:
			c = stdin.read(1)
			if c == 's': lights.scroll = True
			elif c == 'c': lights.scroll = False
	except KeyboardInterrupt: pass

