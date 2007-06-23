"""
Handles the configuration dialog.
"""
from __future__ import absolute_import
import gtk.glade as glade
from .utils import resource, iterable
from .actions import actionObjs, Action
from commandpad.client import BUTTON_1, BUTTON_2, BUTTON_3, BUTTON_4, BUTTON_5, \
                       BUTTON_6, BUTTON_7, BUTTON_8, BUTTON_9, BUTTON_A, \
                       BUTTON_B, MODE_A, MODE_B, MODES
import gobject, gtk
from threading import Lock

__all__ = 'ConfigDialog','Config'

## http://faq.pygtk.org/index.py?req=show&file=faq16.008.htp
def set_model_from_list(cb, items):
	"""Setup a ComboBox or ComboBoxEntry based on a list of strings."""           
	model = gtk.ListStore(str)
	for i in items:
		model.append([i])
	cb.set_model(model)
	if type(cb) == gtk.ComboBoxEntry:
		cb.set_text_column(0)
	elif type(cb) == gtk.ComboBox:
		cell = gtk.CellRendererText()
		cb.pack_start(cell, True)
		cb.add_attribute(cell, 'text', 0)

class ConfigDialog(object):
	__xml = None
	__dialog = None
	__mode = 0
	__button = BUTTON_1
	MODES = [u'0', u'A', u'B', u'AB']
	__modes = []
	__buttons = []
	__actions = []
	__act = None
	__cbAct = None
	__vbActConfig = None
	__ulock = None
	def __init__(self, config):
		self.__conf = config
		self.__xml = glade.XML(resource('config.glade'))
		self.__xml.signal_autoconnect(self)
		self.__dialog = self.__xml.get_widget('gdConfig')
		self.__buttons = [self.__xml.get_widget('b%i'%(btn+1)) for btn in range(BUTTON_1, BUTTON_9+1)]
		self.__modes = [None, self.__xml.get_widget('tbModeA'), self.__xml.get_widget('tbModeB')]
		self.__actions = sorted(list(actionObjs()), (lambda a,b: cmp(a.label, b.label)))
		self.__cbAct = self.__xml.get_widget('cbAction')
		set_model_from_list(self.__cbAct, map((lambda a: a.label), self.__actions))
		self.__vbActConfig = self.__xml.get_widget('vbActConfig')
		self.__ulock = Lock()
		self.__update(True)
	
	def __name(self):
		FORMAT = u"%(num)i (%(mode)s)"
		mode = self.MODES[self.__mode]
		return FORMAT % {'mode': mode, 'num': self.__button + 1}
	
	def __set_action(self, action):
		if self.__act is not None:
			for name, label, conf in self.__act.config:
				conf.destroy()
		if isinstance(action, int):
			i = action
			action = self.__actions[i]
		else:
			print "change", self.__actions, action
			i = self.__actions.index(action)
			self.__cbAct.set_active(i)
		self.__act = action
		self.__vbActConfig.forall(self.__vbActConfig.remove) # Get rid of previous children
		ops = self.__conf[self.__mode, self.__button][1]
		if ops is None: ops = {}
		print "load ops", ops
		for name, label, conf in action.config:
			print "nlc:", name, label, conf
			ui = conf.createInput(self.__save)
			if name in ops: 
				conf.setValue(ops[name])
			self.__vbActConfig.add(ui)
		self.__vbActConfig.show_all()
	
	def __save(self):
		if self.__ulock.locked(): return # Don't save when updating
		ops = {}
		for name, label, conf in self.__act.config:
			ops[name] = conf.getValue()
		print "Save:", self.__act, ops
		self.__conf[self.__mode, self.__button] = (self.__act, ops)
		print "saved:", self.__conf[self.__mode, self.__button]
	
	def __update(self, first=False):
		if not self.__ulock.acquire(False): return
		try:
			self.__xml.get_widget('lbldButton').set_label(self.__name())
			if bool(self.__mode & MODE_A) != bool(self.__modes[MODE_A].get_active()):
				self.__modes[MODE_A].set_active(bool(num & MODE_A))
			if bool(self.__mode & MODE_B) != bool(self.__modes[MODE_B].get_active()):
				self.__modes[MODE_B].set_active(bool(self.__mode & MODE_B))
			conf = self.__conf[self.__mode, self.__button]
			self.__set_action(conf[0] or Action())
		finally:
			self.__ulock.release()
	
	def buttonChange(self, widget, data=None):
		num = self.__buttons.index(widget)
		print "buttonChange", widget, num
		self.__save()
		if num != self.__button:
			self.__button = num
			self.__update()
	
	def modeChange(self, widget, data=None):
		num = self.__modes.index(widget)
		print "modeChange", widget, num
		self.__save()
		self.__mode = (self.__mode & ~num) | (num if widget.get_active() else 0)
		self.__update()
	
	def actionChange(self, widget, data=None):
		print "actionChange", widget, data
		i = widget.get_active()
		self.__set_action(i)
		self.__save()
	
	def __del__(self):
		self.__dialog.destroy()
		self.__dialog = None
	
	def run(self):
		rv = self.__dialog.run()
		self.__dialog.hide()
		return rv
	
	def grab(self):
		return self.__dialog.present()

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
	String:
	   A combination of a mode (letters 'A' and 'B') and
	   a number (digits 1-9). So the string 'AB1' is equivelent to 
	   (MODE_A|MODE_B, 0). If no number is given, it's the same as just the
	   mode.
	
	Note that slicing is handled but strictly unsupported.
	
	The values returned are always iterables of the form:
	   [ actions.Action(ACTION), dict(OPTIONS) ]
	"""
	def __init__(self):
		self.data = dict([ ((m,b), (None, None)) for m in MODES for b in range(9) ])
	
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
		else: 
			single = False
		if isinstance(button, int):
			button = slice(button, button+1)
		else: 
			single = False
		
		return single, mode, button
	
	def __getitem__(self, index):
		single, mode, button = self.__indexes(index)
		
		buttons = [self.data[m,b] for m in xrange(*mode.indices(len(MODES))) for b in xrange(*button.indices(9))]
		
		if single:
			assert len(buttons) == 1
			return buttons[0]
		else:
			return buttons
	
	def __setitem__(self, index, value):
		single, mode, button = self.__indexes(index)
		
		if single:
			value = [value]
		iv = iter(value)
		try:
			for m in xrange(*mode.indices(len(MODES))):
				for b in xrange(*button.indices(9)):
					v = iv.next()
					if not (iterable(v) and len(tuple(v)) == 2):
						raise ValueError
					self.data[m,b] = tuple(v)
		except StopIteration: 
			raise IndexError("Too many values: %i values for %r" % (len(value), index))
	
	def __iter__(self):
		for mode, buttons in enumerate(self.data):
			for button, val in enumerate(buttons):
				yield [(mode, button)] + list(val)


