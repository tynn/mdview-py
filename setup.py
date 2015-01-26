#	This file is part of mdview.py
#
#	Copyright (c) 2014 Christian Schmitz <tynn.dev@gmail.com>
#
#	mdview.py is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	mdview.py is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with mdview.py. If not, see <http://www.gnu.org/licenses/>.

from DistUtilsExtra.auto import setup, install_auto, sdist_auto
import mdview

_noegg = lambda (key, _) :  key != 'install_egg_info'
class install_noegg (install_auto) :
	sub_commands = list(filter(_noegg, install_auto.sub_commands))

class sdist_nopot (sdist_auto) :
	filter_suffix = sdist_auto.filter_suffix + ['.pot']


setup(
	name = mdview.__appname__,
	version = mdview.__version__,
	author = mdview.__author__,
	author_email = mdview.__author_email__,
	license = 'GPLv3+',
	description = mdview.__doc__,
	long_description = mdview.__doc__,
	url = mdview.__url__,
	platforms = ['Linux'],
	scripts = ['mdview.py'],
	cmdclass = {'install': install_noegg, 'sdist': sdist_nopot},
)

