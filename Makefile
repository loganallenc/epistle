APPDIR = $(DESTDIR)/usr/share/applications
LIBDIR = $(DESTDIR)/usr/lib/epistle
BINDIR = $(DESTDIR)/usr/bin
install:
	mkdir -p $(APPDIR)
	mkdir -p $(LIBDIR)
	mkdir -p $(BINDIR)
	cp -r * $(LIBDIR)/
	chmod +x $(LIBDIR)/epistle.py
	cp epistle $(BINDIR)/
	chmod +x $(BINDIR)/epistle
	cp epistle.desktop $(APPDIR)/
uninstall:
	rm -rf $(LIBDIR)
	rm -f $(BINDIR)/epistle
	rm -f $(APPDIR)/epistle.desktop
