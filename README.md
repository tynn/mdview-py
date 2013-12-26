mdview.py
=========

*mdview.py* is a simple viewer for Markdown files.
It tracks changes in files currently opened to keep the view up to date.

It is based on *Gtk* and *WebKit* and uses *Gio* to monitor changes of opened files.


Installation
------------

Create the *mdview.py* file with

	 ./configure

and install with

	 sudo make install

or just use it directly.

If the configure script does not exist run

	 autoreconf -fi

first.

