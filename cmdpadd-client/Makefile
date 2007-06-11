# Where to put ____ on 'make install'?
BIN     = $(DESTDIR)/usr/bin
CONF    = $(DESTDIR)/etc
MAN     = $(DESTDIR)/usr/share/man
DOC     = $(DESTDIR)/usr/share/doc/cmdpadd-client

PROGRAM=cmdpadd-client

all: $(PROGRAM)-target

$(PROGRAM): 

$(PROGRAM)-target: $(PROGRAM)

install : $(PROGRAM)-target
	install -d $(BIN) $(MAN)/man1 $(DOC)
	install ./$(PROGRAM) $(BIN)
	install -m644 $(PROGRAM).1 $(MAN)/man1
	gzip debian/$(PROGRAM).sgml -c > $(DOC)/$(PROGRAM).sgml.gz

clean: 
	rm -f $(PROGRAM).tar.gz

cmdpadd.tar.gz : $(MODULES) $(PROGRAM) $(TEST) Makefile $(PROGRAM).1 debian/*
	-@rm -rf debian/$(PROGRAM)
	tar -czf $@ $^

deb:
	@rm -f *.pyc *.pyo
	@rm -f $(PROGRAM).tar.gz
	debuild

pbuilder:
	sudo pbuilder update
	pdebuild

dist : deb

.PHONY: all install clean dist $(PROGRAM)-target deb pbuilder
