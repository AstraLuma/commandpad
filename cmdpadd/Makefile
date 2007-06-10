# Where to put ____ on 'make install'?
BIN     = $(DESTDIR)/usr/bin
CONF    = $(DESTDIR)/etc
MAN     = $(DESTDIR)/usr/share/man
DOC     = $(DESTDIR)/usr/share/doc/cmdpadd
MOD     = $(DESTDIR)/usr/share/python-support/cmdpadd

MODULE=commandpad
DAEMON=cmdpadd
TEST=cpd-test
DAEMON_CONF=dbus-cmdpadd.conf
UPSTART_SCRIPT=debian/event.d

all: cmdpadd-target

cmdpadd: 

cmdpadd-target: cmdpadd 

install : cmdpadd-target
	install -d $(BIN) $(CONF) $(CONF)/dbus-1/system.d $(CONF)/event.d $(MAN)/man1 $(DOC) $(MOD)/$(MODULE)
	install ./cmdpadd $(BIN)
	install -m644 dbus-cmdpadd.conf $(CONF)/dbus-1/system.d/cmdpadd.conf
	install -m644 $(DAEMON).1 $(MAN)/man1
	gzip debian/cmdpadd.sgml -c > $(DOC)/cmdpadd.sgml.gz
	install $(wildcard $(MODULE)/*) $(MOD)/$(MODULE)

clean: 
	rm -f cmdpadd.tar.gz

cmdpadd.tar.gz : $(MODULES) $(DAEMON) $(TEST) $(DAEMON_CONF) Makefile $(DAEMON).1 debian/*
	-@rm -rf debian/$(DAEMON)
	tar -czf $@ $^

deb:
	@rm -f *.pyc *.pyo
	@rm -f cmdpadd.tar.gz
	debuild

pbuilder:
	sudo pbuilder update
	pdebuild

dist : deb

.PHONY: all install clean dist cmdpadd-target deb pbuilder
