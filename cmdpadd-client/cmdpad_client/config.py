"""
Handles the configuration dialog.
"""
from __future__ import absolute_import
import gtk.glade as glade
from .utils import resource, iterable
from commandpad.client import BUTTON_1, BUTTON_2, BUTTON_3, BUTTON_4, BUTTON_5, \
                       BUTTON_6, BUTTON_7, BUTTON_8, BUTTON_9, BUTTON_A, \
                       BUTTON_B, MODE_A, MODE_B, MODES

class ConfigDialog(object):
	__xml = None
	__dialog = None
	def __init__(self):
		self.__xml = glade.XML(resource('config.glade'))
		self.__xml.signal_autoconnect(self)
		self.__dialog = self.__xml.get_widget('gdConfig')
	
	def buttonChange(self, widget, data=None):
		print "buttonChange", widget, data
	
	def modeChange(self, widget, data=None):
		print "modeChange", widget, data
	
	def __del__(self):
		self.__dialog.destroy()
	
	def run(self):
		rv = self.__dialog.run()
		self.__dialog.hide()

class Config(object):
	"""
	Holds the configuration information and handles loading/saving.
	Configuration is gotten using a 2-array interface or a dict interface:
	2-array:
	   >>> config[MODE_A, 0]
	   The first item is a mode (see MODES) or a list-compatible index (eg,
	   slice).
	   The second item is a button, or a list-compatible index. Note that 
	   Button 1 is index 0.
	   None or Ellipses are accepted for either argument, and are 
	   equivelent to the slice "0:".
	String:
	   A combination of a mode (letters 'A' and 'B') and
	   a number (digits 1-9). So the string 'AB1' is equivelent to 
	   (MODE_A|MODE_B, 0). If no number is given, it's the same as just the
	   mode.
	
	The values returned are always iterables of the form:
	   [ (MODE, BUTTON), str(ACTION), dict(OPTIONS) ]
	Converting ACTION and OPTIONS to something useful is the responsibility
	of another module.
	"""
	def __init__(self):
		self.data = [ [(None, None) for i in range(9)] for i in MODES ]
	
	def __indexes(self,index):
		value = (Ellipsis,Ellipsis)
		if isinstance(index, basestring):
			index = index.lower()
			mode = (MODE_A if 'a' in index else 0) | (MODE_B if 'b' in index else 0)
			s = index.replace('a', '').replace('b', '')
			try:
				b = int(s, 10) - 1
			except ValueError:
				b = Ellipsis
			value = mode,b
		elif iterable(index):
			value = [Ellipsis if i is None else i for i in index]
		elif index in MODES:
			value = index,Ellipsis
		else:
			raise ValueError
		mode, button = value
		single = True
		if mode is Ellipsis:
			mode = slice(0)
		if button is Ellipsis:
			button = slice(0)
		if isinstance(mode, int):
			mode = slice(mode, mode+1)
		else: single = False
		if isinstance(button, int):
			button = slice(button, button+1)
		else: single = False
		
		return single, mode, button
	
	def __getitem__(self, index):
		single, mode, button = self.__indexes(index)
		
		modes = self.data[mode]
		buttons = [[(m,b)]+list(bu) for m,mo in enumerate(modes) for b,bu in list(enumerate(mo))[button]]
		
		if single:
			assert len(buttons) == 1
			return buttons[0]
		else:
			return buttons
	
	def __setitem__(self, index, value):
		single, mode, button = self.__indexes(index)
		
		if single:
			self.data[mode][button] = [value]
		else:
			values = iter(value)
			for m in mode.indexes(len(self.data)):
				for b in button.indexes(len(self.data[0])):
					self.data[m][b] = value.next()
	
	def __iter__(self):
		for mode, buttons in enumerate(self.data):
			for button, val in enumerate(buttons):
				yield [(mode, button)] + list(val)


