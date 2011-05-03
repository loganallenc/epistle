APPDIR = $(DESTDIR)/usr/share/applications
LIBDIR = $(DESTDIR)/usr/share/epistle
BINDIR = $(DESTDIR)/usr/bin
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(APPDIR)
	mkdir -p $(LIBDIR)
	mkdir -p $(BINDIR)
	cp -r * $(LIBDIR)/
	cp epistle $(BINDIR)/
	cp epistle.desktop $(APPDIR)/
uninstall:
	rm -rf $(LIBDIR)
	rm -f $(BINDIR)/epistle
	rm -f $(APPDIR)/epistle.desktop
