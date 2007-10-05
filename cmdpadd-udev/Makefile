all : _uinput.so uinput-test docs

_uinput.so : uinput.i joystick.i setup.py
	python setup.py build
	cp build/lib.linux-i686-2.5/uinput.so _uinput.so

_joystick.so : _uinput.so
	cp build/lib.linux-i686-2.5/joystick.so _joystick.so

docs : uinput.html _uinput.html joystick.html _joystick.html

uinput.html : _uinput.so
	pydoc -w uinput

_uinput.html : _uinput.so
	pydoc -w _uinput

joystick.html : _joystick.so
	pydoc -w joystick

_joystick.html : _joystick.so
	pydoc -w _joystick

.PHONY : all clean test docs

clean :
	-rm -f _uinput.so
	-rm -f _joystick.so
	-rm -rf build
	-rm -f uinput_wrap.c
	-rm -f uinput.html
	-rm -f _uinput.html
	-rm -f joystick_wrap.c
	-rm -f joystick.html
	-rm -f _joystick.html
	-rm -f uinput-test
	-rm -f uinput.py
	-rm -f joystick.py
	-rm -f *.pyc *.pyo

test : docs
	sudo ./uinput-test
	sudo ./pytest
