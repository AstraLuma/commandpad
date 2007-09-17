all : _uinput.so uinput-test docs

_uinput.so : uinput.i setup.py
	python setup.py build
	cp build/lib.linux-i686-2.5/uinput.so _uinput.so

docs : uinput.html _uinput.html

uinput.html : _uinput.so
	pydoc -w uinput

_uinput.html : _uinput.so
	pydoc -w _uinput

.PHONY : all clean test docs

clean :
	-rm -f _uinput.so
	-rm -rf build
	-rm -f uinput_wrap.c
	-rm -f uinput.html
	-rm -f uinput-test
	-rm -f uinput.py
	-rm -f *.pyc *.pyo

test : docs
	sudo ./uinput-test
	sudo ./pytest
