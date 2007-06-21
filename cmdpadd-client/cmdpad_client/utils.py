"""
Some misc. functions for the client.
"""
import os.path, sys
__all__ = 'resource', 'iterable'

def resource(fname):
	sfname = os.path.join('/usr/share/', sys.argv[0], fname)
	if os.path.exists(sfname):
		return sfname
	#stick other places here
	else:
		return fname

def iterable(o):
	return hasattr(o, '__iter__') and callable(o.__iter__)

