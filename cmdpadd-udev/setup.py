from distutils.core import setup, Extension

uinput = Extension('uinput',
                    sources = ['uinput.i'],
                    swig_opts=['-I/usr/include','-I/usr/include/python','-modern','-modernargs','-keyword'])

setup (name = 'uinput',
       version = '1.0',
       description = 'some constants',
       ext_modules = [uinput])
