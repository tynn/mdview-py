#!/usr/bin/env python
# -*- coding: utf-8 -*-
#	This file is part of mdview.py
#
#	Copyright (c) 2013 Christian Schmitz <tynn.dev@gmail.com>
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

__appname__ = "mdview.py"
__version__ = "1.0b"
__author__ = "Christian Schmitz"
__author_email__ = "tynn.dev@gmail.com"
__url__ = "https://github.com/tynn/mdview-py"


import os, sys
from codecs import open
from gettext import gettext as _
from gi.repository import Gdk, Gio, Gtk, WebKit
from markdown import Markdown
from subprocess import Popen
try : from urllib.parse import unquote, urlparse
except :
	from urllib import unquote
	from urlparse import urlparse


def _stock (stock_id, mnemonic = True) :
	label = Gtk.stock_lookup(stock_id).label
	if not mnemonic : return label.replace('_', '')
	return label


def _true (*args) : return True



class MarkdownOptions (object) :

	KEYS = ('output_format', 'safe_mode', 'html_replacement_text', 'tab_length', 'enable_attributes', 'smart_emphasis', 'lazy_ol')

	output_format = ('xhtml1', 'xhtml5', 'html4', 'html5')
	safe_mode = (False, 'replace', 'remove', 'escape')
	html_replacement_text = str
	tab_length = int
	enable_attributes = bool
	smart_emphasis = bool
	lazy_ol = bool

	def set (self, key, value) :
		if key in MarkdownOptions.KEYS : setattr(self, key, value)

	def dict (self, dict = None) :
		if not dict : dict = {}
		for key in MarkdownOptions.KEYS :
			attr = getattr(MarkdownOptions, key)
			value = getattr(self, key)
			if bool == attr == type(value) or tuple == type(attr) and value in attr or value and attr == type(value) : dict[key] = value
		return dict



class Menu (object) :

	UI = """
		<ui>
			<menubar name='MainMenu'>
				<menu action='FileMenu'>
					<menuitem action='FileOpen'/>
					<separator/>
					<menuitem action='FileRevertToSaved'/>
					<menuitem action='FileExportHTML'/>
					<separator/>
					<menuitem action='FileQuit'/>
				</menu>
				<menu action='EditMenu'>
					<menuitem action='EditCopy'/>
					<separator/>
					<menuitem action='EditSelectAll'/>
					<separator/>
					<menuitem action='EditPreferences'/>
				</menu>
				<menu action='ViewMenu'>
					<menuitem action='ViewZoomIn'/>
					<menuitem action='ViewZoomOut'/>
					<menuitem action='ViewZoom100'/>
					<separator/>
					<menuitem action='ViewViewSource'/>
				</menu>
				<menu action='MarkdownMenu'>
					<menuitem action='MarkdownEnableAttributes'/>
					<menuitem action='MarkdownSmartEmphasis'/>
					<menuitem action='MarkdownLazyOl'/>
					<separator/>
					<menu action='MarkdownOutputFormatMenu'>
						<menuitem action='MarkdownOutputFormatHTML5'/>
						<menuitem action='MarkdownOutputFormatHTML4'/>
						<menuitem action='MarkdownOutputFormatXHTML1'/>
						<menuitem action='MarkdownOutputFormatXHTML5'/>
					</menu>
					<menu action='MarkdownSafeModeMenu'>
						<menuitem action='MarkdownSafeModeFalse'/>
						<menuitem action='MarkdownSafeModeReplace'/>
						<menuitem action='MarkdownSafeModeRemove'/>
						<menuitem action='MarkdownSafeModeEscape'/>
					</menu>
				</menu>
				<menu action='HelpMenu'>
					<menuitem action='HelpAbout'/>
				</menu>
			</menubar>
		</ui>"""

	def __init__ (self) :
		uimanager = Gtk.UIManager()
		uimanager.add_ui_from_string(self.UI)

		default_action_group = Gtk.ActionGroup('default_actions')
		self.document_action_group = Gtk.ActionGroup('document_actions')
		self.selection_action_group = Gtk.ActionGroup('selection_actions')

		self.document_action_group.set_sensitive(False)
		self.selection_action_group.set_sensitive(False)

		uimanager.insert_action_group(default_action_group)
		uimanager.insert_action_group(self.document_action_group)
		uimanager.insert_action_group(self.selection_action_group)

		self.action = {}

		self._add_action('FileMenu', _stock(Gtk.STOCK_FILE), None, None, default_action_group)
		self._add_action('FileOpen', None, None, Gtk.STOCK_OPEN, default_action_group, None)
		self._add_action('FileExportHTML', _("_Export HTML"), None, None, self.document_action_group, "<Shift><Control>E")
		self._add_action('FileRevertToSaved', None, None, Gtk.STOCK_REVERT_TO_SAVED, self.document_action_group, None)
		self._add_action('FileQuit', None, None, Gtk.STOCK_QUIT, default_action_group, None)

		self._add_action('EditMenu', _stock(Gtk.STOCK_EDIT), None, None, default_action_group)
		self._add_action('EditCopy', None, None, Gtk.STOCK_COPY, self.selection_action_group, None)
		self._add_action('EditSelectAll', None, None, Gtk.STOCK_SELECT_ALL, self.document_action_group, "<Control>A")
		self._add_action('EditPreferences', None, None, Gtk.STOCK_PREFERENCES, default_action_group)

		self._add_action('ViewMenu', _("_View"), None, None, default_action_group)
		self._add_action('ViewZoomIn', None, None, Gtk.STOCK_ZOOM_IN, self.document_action_group, "<Control>plus")
		self._add_action('ViewZoomOut', None, None, Gtk.STOCK_ZOOM_OUT, self.document_action_group, "<Control>minus")
		self._add_action('ViewZoom100', None, None, Gtk.STOCK_ZOOM_100, self.document_action_group, "<Control>0")
		self._add_action('ViewViewSource', _("_View source"), None, None, self.document_action_group, "<Control>U", Gtk.ToggleAction)

		self._add_action('MarkdownMenu', _("_Markdown"), None, None, default_action_group)
		self._add_action('MarkdownEnableAttributes', _("E_nable attributes"), None, None, default_action_group, Action = Gtk.ToggleAction)
		self._add_action('MarkdownSmartEmphasis', _("S_mart emphasis"), None, None, default_action_group, Action = Gtk.ToggleAction)
		self._add_action('MarkdownLazyOl', _("_Lazy ol"), None, None, default_action_group, Action = Gtk.ToggleAction)

		self._add_action('MarkdownOutputFormatMenu', _("_Output format"), None, None, default_action_group)
		group = self._add_action('MarkdownOutputFormatHTML5', "HTML _5", None, None, default_action_group, Action = Gtk.RadioAction, args = [3])
		self._add_action('MarkdownOutputFormatHTML4', "HTML _4", None, None, default_action_group, Action = Gtk.RadioAction, args = [2], group_source = group)
		self._add_action('MarkdownOutputFormatXHTML1', "_XHTML 1.1", None, None, default_action_group, Action = Gtk.RadioAction, args = [0], group_source = group)
		self._add_action('MarkdownOutputFormatXHTML5', "XHTML '5'", None, None, default_action_group, Action = Gtk.RadioAction, args = [1], group_source = group)

		self._add_action('MarkdownSafeModeMenu', _("_Safe mode"), None, None, default_action_group)
		group = self._add_action('MarkdownSafeModeFalse', _("_None"), None, None, default_action_group, Action = Gtk.RadioAction, args = [0])
		self._add_action('MarkdownSafeModeReplace', _("Re_place"), None, None, default_action_group, Action = Gtk.RadioAction, args = [1], group_source = group)
		self._add_action('MarkdownSafeModeRemove', _("_Remove"), None, None, default_action_group, Action = Gtk.RadioAction, args = [2], group_source = group)
		self._add_action('MarkdownSafeModeEscape', _("_Escape"), None, None, default_action_group, Action = Gtk.RadioAction, args = [3], group_source = group)

		self._add_action('HelpMenu', _stock(Gtk.STOCK_HELP), None, None, default_action_group)
		self._add_action('HelpAbout', None, None, Gtk.STOCK_ABOUT, default_action_group)

		self.menubar = uimanager.get_widget("/MainMenu")
		self.accel_group = uimanager.get_accel_group()

	def _add_action (self, menu_id, menu_label, menu_icon, stock_id, action_group, accel = False, Action = Gtk.Action, args = [], group_source = None) :
		action = Action(menu_id, menu_label, menu_icon, stock_id, *args)
		if accel == False : action_group.add_action(action)
		else : action_group.add_action_with_accel(action, accel)
		self.action[menu_id] = action
		if group_source : action.join_group(group_source)
		return action

	def connect (self, menu_id, callback, *args) : self.action[menu_id].connect("activate", callback, *args)

	def set_document_available (self, available) : self.document_action_group.set_sensitive(available)

	def set_selection_available (self, available) : self.selection_action_group.set_sensitive(available)

	def set_view_source (self, view_source) : self.action['ViewViewSource'].set_active(bool(view_source))

	def set_enable_attributes (self, enable_attributes) : self.action['MarkdownEnableAttributes'].set_active(bool(enable_attributes))

	def set_smart_emphasis (self, smart_emphasis) : self.action['MarkdownSmartEmphasis'].set_active(bool(smart_emphasis))

	def set_lazy_ol (self, lazy_ol) : self.action['MarkdownLazyOl'].set_active(bool(lazy_ol))

	def set_output_format (self, value) : self.action['MarkdownOutputFormatHTML4'].set_current_value(MarkdownOptions.output_format.index(value))

	def set_safe_mode (self, value) : self.action['MarkdownSafeModeReplace'].set_current_value(MarkdownOptions.safe_mode.index(value))



class WebView (WebKit.WebView) :

	def __init__ (self) :
		WebKit.WebView.__init__(self)
		self.connect('drag-motion', _true)
		self.connect('drag-drop', _true)
		self.drag_dest_unset()
		self.drag_dest_set(Gtk.DestDefaults.DROP, [], Gdk.DragAction.COPY)
		self.drag_dest_add_uri_targets()
		self.props.settings.props.enable_default_context_menu = False
		self.props.settings.props.enable_scripts = False
		self.props.settings.props.enable_java_applet = False
		self.props.settings.props.enable_plugins = False

	def copy_clipboard (self, *args) : WebKit.WebView.copy_clipboard(self)

	def select_all (self, *args) : WebKit.WebView.select_all(self)

	def zoom_in (self, *args) : WebKit.WebView.zoom_in(self)

	def zoom_out (self, *args) : WebKit.WebView.zoom_out(self)



class UriLabel (Gtk.Label) :

	def __init__ (self) :
		Gtk.Label.__init__(self)
		self.set_no_show_all(True)
		self.set_halign(Gtk.Align.START)
		self.set_valign(Gtk.Align.END)
		self.set_padding(3, 1)

	def hide (self, *args) : Gtk.Label.hide(self)



class AboutDialog (Gtk.AboutDialog) :

	def __init__ (self, parent) :
		Gtk.AboutDialog.__init__(self, parent = parent, program_name = __appname__, version = __version__)
		self.connect('delete-event', _true)
		self.connect('response', self.hide)

		self.set_comments(_("{0} is a simple viewer for Markdown files.").format(__appname__))
		self.set_website(__url__)
		self.set_copyright("Copyright © 2013 " + __author__)
		self.set_license_type(Gtk.License.GPL_3_0)
		self.set_logo_icon_name(None)

	def present (self, *args) : Gtk.AboutDialog.present(self)

	def hide (self, *args) : Gtk.AboutDialog.hide(self)



class PreferencesDialog (Gtk.Dialog) :

	SCHEMA = "apps.mdview-py"

	def __init__ (self, parent) :
		Gtk.Dialog.__init__(self, parent = parent, title = _stock(Gtk.STOCK_PREFERENCES, False))
		self.connect('delete-event', _true)
		self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

		output_format = self._combo(MarkdownOptions.output_format, {'xhtml1': "XHTML 1.1", 'xhtml5': "XHTML '5'", 'html4': "HTML 4", 'html5': "HTML 5"})
		safe_mode = self._combo(MarkdownOptions.safe_mode, {False: _("None"), 'replace': _("Replace"), 'remove': _("Remove"), 'escape': _("Escape")})
		html_replacement_text = Gtk.Entry()
		tab_length = Gtk.SpinButton()
		enable_attributes = Gtk.CheckButton(_("Enable attributes"))
		smart_emphasis = Gtk.CheckButton(_("Smart emphasis"))
		lazy_ol = Gtk.CheckButton(_("Lazy ol"))

		output_format.connect('changed', self.on_state_changed, 'output_format')
		safe_mode.connect('changed', self.on_state_changed, 'safe_mode')
		html_replacement_text.connect('changed', self.on_html_replacement_text_changed)
		tab_length.connect('value-changed', self.on_tab_length_changed)
		enable_attributes.connect('toggled', self.on_state_changed, 'enable_attributes')
		smart_emphasis.connect('toggled', self.on_state_changed, 'smart_emphasis')
		lazy_ol.connect('toggled', self.on_state_changed, 'lazy_ol')

		# TODO layout
		box = self.get_content_area()
		box.pack_start(output_format, False, False, False)
		box.pack_start(safe_mode, False, False, False)
		box.pack_start(html_replacement_text, False, False, False)
		box.pack_start(tab_length, False, False, False)
		box.pack_start(enable_attributes, False, False, False)
		box.pack_start(smart_emphasis, False, False, False)
		box.pack_start(lazy_ol, False, False, False)
		box.show_all()

		self.md_options = MarkdownOptions()
		self.md_options.html_replacement_text = html_replacement_text.get_text()
		self.md_options.enable_attributes = enable_attributes.get_active()
		self.md_options.smart_emphasis = smart_emphasis.get_active()
		self.md_options.lazy_ol = lazy_ol.get_active()

		tab_length.set_adjustment(Gtk.Adjustment(4, 1, 24, 1, 4, 0))

		if self.SCHEMA in Gio.Settings.list_schemas() :
			settings = Gio.Settings.new(self.SCHEMA)
			settings.bind("output-format", output_format, 'active-id', Gio.SettingsBindFlags.DEFAULT)
			settings.bind("safe-mode", safe_mode, 'active-id', Gio.SettingsBindFlags.DEFAULT)
			settings.bind("html-replacement-text", html_replacement_text, 'text', Gio.SettingsBindFlags.DEFAULT)
			settings.bind("tab-length", tab_length, "value", Gio.SettingsBindFlags.DEFAULT)
			settings.bind("enable-attributes", enable_attributes, 'active', Gio.SettingsBindFlags.DEFAULT)
			settings.bind("smart-emphasis", smart_emphasis, 'active', Gio.SettingsBindFlags.DEFAULT)
			settings.bind("lazy-ol", lazy_ol, 'active', Gio.SettingsBindFlags.DEFAULT)
		else :
			output_format.set_active(3)
			tab_length.set_value(4)
			safe_mode.set_active(3)
			enable_attributes.set_active(True)
			smart_emphasis.set_active(True)
			lazy_ol.set_active(True)

	def _combo (self, keys, values) :
		combo = Gtk.ComboBoxText()
		for id in keys : combo.append(str(id), values[id])
		return combo

	def on_html_replacement_text_changed (self, entry) : self.on_preference_changed('html_replacement_text', entry.get_text())

	def on_tab_length_changed (self, spin_button) : self.on_preference_changed('tab_length', spin_button.get_value_as_int())

	def on_state_changed (self, widget, key) : self.on_preference_changed(key, widget.get_active())

	def on_preference_changed (self, key, value) :
		try : self.md_options.set(key, getattr(MarkdownOptions, key)[value])
		except : self.md_options.set(key, value)

	def present (self, *args) : Gtk.Dialog.present(self)



class ErrorDialog (Gtk.MessageDialog) :

	def __init__ (self, error_msg, parent = None) :
		Gtk.MessageDialog.__init__(self, parent, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, error_msg, title = __appname__)
		self.connect('response', self.destroy)

	def destroy (self, *args) : Gtk.MessageDialog.destroy(self)



class FileChooserDialog (Gtk.FileChooserDialog) :

	def __init__ (self, title, parent, action, stock_ok, file) :
		Gtk.FileChooserDialog.__init__(self, title, parent, action, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, stock_ok, Gtk.ResponseType.OK))
		if file : self.set_filename(file)
		else : self.set_current_folder(os.getcwd())

	def add_text_filter (self) :
		filter = Gtk.FileFilter()
		filter.set_name(_("Text files"))
		filter.add_mime_type("text/plain")
		self.add_filter(filter)

	def add_pattern_filter (self, name, pattern) :
		filter = Gtk.FileFilter()
		filter.set_name(name)
		for pat in pattern : filter.add_pattern(pat)
		self.add_filter(filter)



class MdView (Gtk.Window) :

	USER_HOME = os.path.expanduser('~')

	_menu_batch = False

	file = None
	html = None
	monitor = None

	def __init__ (self, *files) :
		Gtk.Window.__init__(self, title = __appname__)
		self.connect('delete-event', Gtk.main_quit)
		self.set_default_size(600, 500)
		self.set_default_icon_name(__appname__)

		self._setup_gui()

		self.webview.connect('document-load-finished', self.uri_label.hide)
		self.webview.connect('drag-data-received', self.on_drag_data_received)
		self.webview.connect('hovering-over-link', self.on_hovering_over_link)
		self.webview.connect("scroll-event", self.on_scroll_event)
		self.webview.connect('selection-changed', self.on_selection_changed)

		self.menu.connect('FileOpen', self.on_action_open)
		self.menu.connect('FileExportHTML', self.on_action_export)
		self.menu.connect('FileRevertToSaved', self.on_action_revert_to_saved)
		self.menu.connect('FileQuit', Gtk.main_quit)
		self.menu.connect('EditCopy', self.webview.copy_clipboard)
		self.menu.connect('EditSelectAll', self.webview.select_all)
		self.menu.connect('EditPreferences', self.preferences.present)
		self.menu.connect('ViewZoomIn', self.webview.zoom_in)
		self.menu.connect('ViewZoomOut', self.webview.zoom_out)
		self.menu.connect('ViewZoom100', self.zoom_100)
		self.menu.connect('ViewViewSource', self.on_action_view_source)
		self.menu.connect('MarkdownEnableAttributes', self.on_activate_markdown_option, 'enable_attributes')
		self.menu.connect('MarkdownSmartEmphasis', self.on_activate_markdown_option, 'smart_emphasis')
		self.menu.connect('MarkdownLazyOl', self.on_activate_markdown_option, 'lazy_ol')
		self.menu.connect('MarkdownOutputFormatHTML5', self.on_activate_markdown_option, 'output_format')
		self.menu.connect('MarkdownOutputFormatHTML4', self.on_activate_markdown_option, 'output_format')
		self.menu.connect('MarkdownOutputFormatXHTML1', self.on_activate_markdown_option, 'output_format')
		self.menu.connect('MarkdownOutputFormatXHTML5', self.on_activate_markdown_option, 'output_format')
		self.menu.connect('MarkdownSafeModeFalse', self.on_activate_markdown_option, 'safe_mode')
		self.menu.connect('MarkdownSafeModeReplace', self.on_activate_markdown_option, 'safe_mode')
		self.menu.connect('MarkdownSafeModeRemove', self.on_activate_markdown_option, 'safe_mode')
		self.menu.connect('MarkdownSafeModeEscape', self.on_activate_markdown_option, 'safe_mode')
		self.menu.connect('HelpAbout', self.about.present)

		self.preferences.connect('response', self.on_preferences_changed)

		self.md_options = MarkdownOptions()
		self._setup_markdown_menu(self.preferences.md_options.dict())

		self.load_files(*files)


	def _setup_gui (self) :
		self.menu = Menu()
		self.webview = WebView()
		self.uri_label = UriLabel()

		self.add_accel_group(self.menu.accel_group)

		self.preferences = PreferencesDialog(self)
		self.about = AboutDialog(self)

		scroller = Gtk.ScrolledWindow()
		scroller.add(self.webview)
		overlay = Gtk.Overlay()
		overlay.add(scroller)
		overlay.add_overlay(self.uri_label)
		box = Gtk.VBox()
		box.pack_start(self.menu.menubar, False, False, False)
		box.pack_start(overlay, True, True, False)
		self.add(box)

		self.adj = scroller.get_vadjustment()
		self.adj.connect('value-changed', self.on_adjustment_value_changed)

	def _setup_markdown_menu (self, md_options) :
		self._menu_batch = True
		self.menu.set_enable_attributes(md_options['enable_attributes'])
		self.menu.set_smart_emphasis(md_options['smart_emphasis'])
		self.menu.set_lazy_ol(md_options['lazy_ol'])
		self.menu.set_output_format(md_options['output_format'])
		self.menu.set_safe_mode(md_options['safe_mode'])
		del self._menu_batch
		self._setup_markdown()

	def _setup_markdown (self) : self.md = Markdown(**self.md_options.dict(self.preferences.md_options.dict()))

	def _setup_monitor (self) :
		if self.monitor : self.monitor.cancel()
		self.monitor = Gio.File.new_for_path(self.file).monitor_file(Gio.FileMonitorFlags.SEND_MOVED | Gio.FileMonitorFlags.WATCH_HARD_LINKS, None)
		self.monitor.connect('changed', self.on_file_changed)

	def _load_html (self, lock_scrolling = False) :
		if lock_scrolling == True : self._lock_scrolling()
		self.webview.load_string(self.html, "text/html", "utf-8", "file://" + self.file)

	def _lock_scrolling (self) :
		try :
			adj_value = self.adj.get_value()
			if adj_value > self.adj.get_lower() :
				if adj_value == self.adj.get_upper() - self.adj.get_page_size() : self.adj_value = False
				else : self.adj_value = adj_value
		except : pass

	def _show_error_dialog (self, msg) :
		ErrorDialog(msg, self).run()

	def load_files (self, *files) :
		if files :
			files = list(map(os.path.abspath, files))
			if self.file in files :
				self.menu.set_view_source(False)
				self.zoom_100()
				self.reload()
				files.remove(self.file)
			else :
				while files :
					if self.load(files.pop(0)) : break
			if files :
				files.insert(0, __file__)
				if sys.executable : files.insert(0, sys.executable)
				Popen(files)

	def load (self, file, lock_scrolling = False) :
		old_file, self.file = self.file, os.path.abspath(file)
		old_html, self.html = self.html, None
		if self.reload(lock_scrolling) :
			self._setup_monitor()
			self.zoom_100()
			self.menu.set_document_available(True)
			self.menu.set_view_source(False)
			self.set_title("{2} ({1}) - {0}".format(__appname__, *os.path.split(self.file.replace(self.USER_HOME, '~', 1))))
			return old_file or True
		self.file = old_file
		self.html = old_html

	def reload (self, lock_scrolling = False) :
		try :
			if self.file :
				with open(self.file, 'r', 'utf-8') as f : self.html = self.md.reset().convert(f.read())
				self._load_html(lock_scrolling)
				return True
		except : self._show_error_dialog(_("Failed loading file {0}").format(self.file))

	def export_html (self, file) :
		try :
			if file :
				with open(file, 'w', 'utf-8') as f : f.write(self.html)
				return True
		except : self._show_error_dialog(_("Failed writing file {0}").format(self.file))

	def toggle_view_source (self) : self.menu.set_view_source(not self.webview.get_view_source_mode())

	def zoom_100 (self, *args) : self.webview.set_zoom_level(1)

	def on_file_changed (self, monitor, file, new_file, event) :
		if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT :
			self.reload(True)
		elif event == Gio.FileMonitorEvent.CREATED :
			self._setup_monitor()
			self.reload(True)
		elif event == Gio.FileMonitorEvent.MOVED :
			self.load(new_file.get_path(), True)

	def on_drag_data_received (self, widget, drag_context, x, y, data, info, time) :
		self.load_files(*map(lambda uri : unquote(urlparse(uri).path), data.get_uris()))

	def on_hovering_over_link (self, webview, title, uri) :
		if uri :
			self.uri_label.set_text(uri)
			self.uri_label.show()
		else :
			self.uri_label.hide()

	def on_scroll_event (self, webview, event) :
		if event.type == Gdk.EventType.SCROLL and event.state == Gdk.ModifierType.CONTROL_MASK :
			if event.direction == Gdk.ScrollDirection.UP :
				webview.zoom_in()
				return True
			elif event.direction == Gdk.ScrollDirection.DOWN :
				webview.zoom_out()
				return True

	def on_selection_changed (self, widget) : self.menu.set_selection_available(widget.has_selection())

	def on_adjustment_value_changed (self, adj) :
		try :
			if not adj.get_value() :
				if adj.get_upper() :
					if self.adj_value : adj.set_value(self.adj_value)
					else : adj.set_value(adj.get_upper() - adj.get_page_size())
				del self.adj_value
		except : pass

	def on_preferences_changed (self, preferences, response_id) :
		preferences.hide()
		self._setup_markdown_menu(preferences.md_options.dict())
		self.reload(True)

	def on_action_open (self, action) :
		dialog = FileChooserDialog(_stock(Gtk.STOCK_OPEN, False), self, Gtk.FileChooserAction.OPEN, Gtk.STOCK_OPEN, self.file)
		dialog.set_select_multiple(True)
		dialog.add_pattern_filter(_("Markdown files"), ["*.md"])
		dialog.add_text_filter()
		ok = dialog.run() == Gtk.ResponseType.OK
		files = dialog.get_filenames()
		dialog.destroy()
		if ok : self.load_files(*files)

	def on_action_export (self, action) :
		dialog = FileChooserDialog(_stock(Gtk.STOCK_SAVE_AS, False), self, Gtk.FileChooserAction.SAVE, Gtk.STOCK_SAVE, self.file)
		dialog.set_local_only(True)
		dialog.set_do_overwrite_confirmation(True)
		if self.file : dialog.set_current_name(os.path.splitext(os.path.basename(self.file))[0] + ".html")
		dialog.add_pattern_filter(_("HTML files"), ["*.html", "*.htm"])
		dialog.add_text_filter()
		ok = dialog.run() == Gtk.ResponseType.OK
		file = dialog.get_filename()
		dialog.destroy()
		if ok : self.export_html(file)

	def on_action_revert_to_saved (self, action) :
		self.zoom_100()
		self._load_html()

	def on_action_view_source (self, action) :
		self.webview.set_view_source_mode(action.get_active())
		self._load_html()

	def on_activate_markdown_option (self, action, key) :
		try :
			value = getattr(MarkdownOptions, key)[action.get_current_value()]
			if action.get_active() : self.md_options.set(key, value)
		except : self.md_options.set(key, action.get_active())
		if not self._menu_batch :
			self._setup_markdown()
			self.reload(True)



def main () :
	import signal, gettext
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	gettext.textdomain(__appname__)
	MdView(*sys.argv[1:]).show_all()
	Gtk.main()

if __name__ == '__main__' : main()

