BUILD_BIN=build/lib.linux-i686-2.5
CMODULES=_uinput.so _joystick.so linuxkd.so
GENPYMODULES=$(filter %.py,$(patsubst _%.so,%py,$(CMODULES)))
LOCALPYMODULES=$(filter-out setup.py $(GENPYMODULES),$(wildcard *.py))
PYMODULES=$(LOCALPYMODULES) commandpad/*.py
DOCS=$(filter %.html,$(patsubst %.so,%.html,$(CMODULES)) $(patsubst _%.so,%.html,$(CMODULES)) $(patsubst %.py,%.html,$(LOCALPYMODULES)))

all : $(CMODULES) uinput-test docs pyc pyo

_uinput.so : uinput.i joystick.i linuxkd.c setup.py
	python setup.py build
	cp $(BUILD_BIN)/uinput.so _uinput.so

_joystick.so : _uinput.so
	cp $(BUILD_BIN)/joystick.so $@

linuxkd.so : _uinput.so
	cp $(BUILD_BIN)/linuxkd.so $@

pyc : $(patsubst %.py,%.pyc,$(PYMODULES))
pyo : $(patsubst %.py,%.pyo,$(PYMODULES))

%.pyc : %.py
	python -m py_compile $<

%.pyo : %.py
	python -Om py_compile $<

docs : $(DOCS)

%.html : %.py _%.so
	pydoc -w $*

%.html : %.py
	pydoc -w $*

%.html : %.so
	pydoc -w $*

.PHONY : all clean test docs pyc pyo

clean :
	-rm -rf build
	-rm -f $(CMODULES)
	-rm -f $(DOCS)
	-rm -f $(patsubst %,%_wrap.c %.py,joystick uinput)
	-rm -f uinput-test
	-rm -f *.pyc *.pyo

test : docs uinput-test
	sudo ./uinput-test
	sudo ./pytest

