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

EXTRA_DIST = scalable 16x16 22x22 24x24 32x32 48x48 512x512

iconsdir = $(datarootdir)/icons/hicolor
nobase_icons_DATA = scalable/apps/mdview.py.svg 16x16/apps/mdview.py.png 22x22/apps/mdview.py.png 24x24/apps/mdview.py.png 32x32/apps/mdview.py.png 48x48/apps/mdview.py.png 512x512/apps/mdview.py.png
gtk-update-icon-cache:
	gtk-update-icon-cache -ft $(DESTDIR)$(iconsdir) || :

desktopentrydir = $(datarootdir)/applications
desktopentry_DATA = mdview.py.desktop

schemasdir = $(datarootdir)/glib-2.0/schemas
dist_schemas_DATA = apps.mdview-py.gschema.xml
glib-compile-schemas:
	glib-compile-schemas $(DESTDIR)$(schemasdir) || :

install-data-hook: update-data-config
uninstall-hook: update-data-config
update-data-config: gtk-update-icon-cache glib-compile-schemas

