all : uinput.so uinput-test uinput.html

uinput.so : uinput.i
	python setup.py build
	cp build/lib.linux-i686-2.5/uinput.so .

uinput.html : uinput.so
	pydoc -w uinput

.PHONY : all clean test

clean :
	-rm -f uinput.so
	-rm -rf build
	-rm -f uinput_wrap.c
	-rm -f uinput.html
	-rm -f uinput-test
	-rm -f uinput.py
	-rm -f *.pyc *.pyo

test : uinput.html uinput-test
	sudo ./uinput-test
	sudo ./pytest
