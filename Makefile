LIBDIR = $(DESTDIR)/usr/share/epistle
BINDIR = $(DESTDIR)/usr/bin
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(LIBDIR)
	mkdir -p $(BINDIR)
	cp -r * $(LIBDIR)/
	cp epistle $(BINDIR)/
uninstall:
	rm -rf $(LIBDIR)
	rm -f $(BINDIR)/epistle
