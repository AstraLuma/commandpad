#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import with_statement
from distutils.core import setup, Extension
import os, pickle, re

NAME_EMAIL = re.compile(r'^\s*(?P<name>.*)\s*<(?P<email>.*)\s$')
VERSIONLINE = re.compile(r'\(([0-9.]+)\)')

def parse_control_file(f):
	name=value=None
	for line in f:
		line = line.rstrip()
		if len(line.strip()) == 0:
			# Blank line
			continue
		elif line[0] in ' \t':
			assert value is not None, "Continuations can't exist before a field"
			value += '\n' + line
		elif ':' in line:
			if name is not None: yield name,value
			name,value = line.split(':', 1)
	if name is not None: yield name,value

DEBIAN_CONTROL_MAPPING = {
	'source': 'name',
	'package': 'name',
	'description': 'description',
	'maintainer': '__maintainer_info',
	'homepage': 'url',
	'version': 'version', # Also comes from the changelog
	}

debian_fields = {}
with open('debian/changelog') as changelog:
	for line in changelog:
		line = line.rstrip()
		m = VERSIONLINE.search(line)
		if m:
			debian_fields['version'] = m.group(1)
			break

with open('debian/control') as control:
	for name,value in parse_control_file(control):
		if name in DEBIAN_CONTROL_MAPPING:
			key = DEBIAN_CONTROL_MAPPING[name]
			debian_fields[key] = value

# Fix-up some fields
if 'description' in debian_fields:
	debian_fields['description'], debian_fields['long_description'] = debian_fields['description'].split('\n', 1)

if 'name' in debian_fields:
	if debian_fields['name'].startswith('python-'):
		debian_fields['name'] = debian_fields['name'][len('python-'):]

if '__maintainer_info' in debian_fields:
	nameemail = debian_fields['__maintainer_info']
	del debian_fields['__maintainer_info']
	m = NAME_EMAIL.search(nameemail)
	if m:
		md = m.groupdict()
		debian_fields['maintainer'], debian_fields['maintainer_email'] = md['name'], md['email']

swigops = {
	'swig_opts': ['-I/usr/include', '-I/usr/include/python', '-modern', '-modernargs', '-keyword', '-Wall', '-copyctor'],
	}
setup(
	author='James Bliss',
	author_email='james.bliss@astro73.com',
	packages=['pyinput'],
	ext_modules=[
		Extension('pyinput._uinput', sources=['pyinput/uinput.i'], **swigops),
		],
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: C',
		'Programming Language :: Python',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: System :: Hardware',
		'Topic :: System :: Operating System Kernels :: Linux',
		],
	**debian_fields
	)

