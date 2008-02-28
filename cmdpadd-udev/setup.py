from distutils.core import setup, Extension

swigops = ['-I/usr/include','-I/usr/include/python','-modern','-modernargs','-keyword']

uinput = Extension('uinput',
                    sources = ['uinput.i'],
                    swig_opts=swigops,
                    )

joystick = Extension('joystick',
                    sources = ['joystick.i'],
                    swig_opts=swigops,
                    )

linuxkd = Extension('linuxkd',
                    sources = ['linuxkd.c'],
                    )

setup (name = 'uinput',
       version = '1.0',
       description = 'some constants',
       ext_modules = [uinput, joystick, linuxkd])
