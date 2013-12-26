# 	This file is part of mdview.py
#
# 	Copyright (c) 2013 Christian Schmitz <tynn.dev@gmail.com>
#
# 	mdview.py is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	mdview.py is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with mdview.py. If not, see <http://www.gnu.org/licenses/>.

LOCALES = de


all: mo


SUFFIXES = .po .mo

.po.mo:
	$(MSGFMT) -c -o $@ $<


.Make: mo
.PHONY: mo
mo:
	for locale in $(LOCALES); do \
	  $(MAKE) $$locale.mo; \
	done


install-data-am: mo
	for locale in $(LOCALES); do \
	  dir=$(localedir)/$$locale/LC_MESSAGES; \
	  $(mkdir_p) $(DESTDIR)$$dir; \
	  $(INSTALL_DATA) $$locale.mo $(DESTDIR)$$dir/$(PACKAGE).mo; \
	done

uninstall-am:
	for locale in $(LOCALES); do \
	  rm -f $$locale.mo $(DESTDIR)$(localedir)/$$locale/LC_MESSAGES/$(PACKAGE).mo; \
	done

dist-hook:
	cp -p *.po $(distdir)

mostlyclean-local:
	rm -f *.mo

