"""
The actual actions.
"""

import pkgutil

__all__ = 'actionMods', 'Action'

def actionMods():
	"""actionMods() -> iterator
	An iterator of a list of strings for the modules defining actions.
	"""
	for pkg in pkgutil.iter_modules(__path__, __name__+'.'):
		yield pkg[1]

def actionObjs():
	for pkg in actionMods():
		yield Action(pkg)

class Action(object):
	__mod = None
	name = property((lambda self: self.__mod.__name__.split('.')[-1]), doc="""The module name of the action.""")
	label = property((lambda self: self.__mod.__label__), doc="""The display name of the action.""")
	config = property((lambda self: self.__mod.__config__), doc="""The configuration options.""")
	def __init__(self, name=None):
		if name is None:
			name = __name__ + '.null'
		m = __import__(name)
		for bit in name.split('.')[1:]: # skip the first module
			print "m,n,b", m, name, bit
			print "props", dir(m)
			m = getattr(m, bit)
		self.__mod = m
		print "mod", name, dir(self.__mod)
	
	def run(self, conf):
		self.__mod.run(conf)
	
	def __eq__(self, other):
		try:
			return self.__mod == other.__mod
		except AttributeError:
			return NotImplemented
	
	def __repr__(self):
		return "%s(%r)" % (type(self).__name__, self.__mod.__name__)

