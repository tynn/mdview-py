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

AC_INIT([mdview.py], [1.0b])
AC_CONFIG_AUX_DIR([config])

AM_INIT_AUTOMAKE([foreign])

AC_ARG_VAR([python], [command used for the shebang])
AM_SUBST_NOTMAKE([python])
AS_IF([test -z "$python"], [python="/usr/bin/env python"])

AC_PATH_PROG([MSGFMT], [msgfmt])
AM_CONDITIONAL([INTL], [test -n "$MSGFMT"])

LOCALEDIR=$localedir
while true
do case $LOCALEDIR in *\$*) eval LOCALEDIR=$LOCALEDIR;; *) LOCALEDIR=${LOCALEDIR/#NONE/$ac_default_prefix}; break;; esac
done
AC_SUBST([LOCALEDIR])
AM_SUBST_NOTMAKE([LOCALEDIR])

AC_CONFIG_FILES([Makefile data/Makefile po/Makefile mdview.py])
AC_OUTPUT

