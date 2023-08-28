"""A csv relationship table export plugin for novelyst

Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_retablex
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import sys
import os
import gettext
import locale
from pathlib import Path
import webbrowser
import tkinter as tk
from pywriter.converter.export_target_factory import ExportTargetFactory
from pywriter.pywriter_globals import *
from pywriter.config.configuration import Configuration
from nvretablexlib.csv_table import CsvTable
from pywriter.file.doc_open import open_document

SETTINGS = dict(
    csv_arc_true='Ⓐ',
    csv_arc_false='',
    csv_chr_true='Ⓒ',
    csv_chr_false='',
    csv_loc_true='Ⓛ',
    csv_loc_false='',
    csv_itm_true='Ⓘ',
    csv_itm_false='',
    )
OPTIONS = dict(
    csv_row_numbers=True,
    csv_arc_points=True,
    show_exported=True,
    )

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
    # Fallback for old Windows versions.
    CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('novelyst_retablex', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message

APPLICATION = _('Relationship table export')
PLUGIN = f'{APPLICATION} plugin v@release'


class Plugin:
    """novelyst relationship table export plugin class.
    
    Public methods:
        on_quit() -- Apply changes and close the window.
    """
    VERSION = '@release'
    NOVELYST_API = '4.0'
    DESCRIPTION = 'A relationship table exporter'
    URL = 'https://peter88213.github.io/novelyst_retablex'
    _HELP_URL = 'https://peter88213.github.io/novelyst_retablex/usage'

    def install(self, ui):
        """Add a "Relationship table export" submenu to the 'Export' menu.
        
        Positional arguments:
            ui -- reference to the NovelystTk instance of the application.
        """
        self._ui = ui
        self._csvExporter = None

        #--- Load configuration.
        try:
            homeDir = str(Path.home()).replace('\\', '/')
            configDir = f'{homeDir}/.pywriter/novelyst/config'
        except:
            configDir = '.'
        self.iniFile = f'{configDir}/retable.ini'
        self.configuration = Configuration(SETTINGS, OPTIONS)
        self.configuration.read(self.iniFile)
        self.kwargs = {}
        self.kwargs.update(self.configuration.settings)
        self.kwargs.update(self.configuration.options)

        # Add a submenu to the Export menu.
        retablexMenu = tk.Menu(tearoff=0)
        self._ui.exportMenu.add_separator()
        self._ui.exportMenu.add_cascade(label=APPLICATION, menu=retablexMenu)
        self._ui.exportMenu.entryconfig(APPLICATION, state='normal')
        retablexMenu.add_command(label='csv', command=lambda: self._export_table('excel', 'utf-8'))
        retablexMenu.add_command(label='csv (Excel)', command=lambda:self._export_table('excel-tab', 'utf-16'))

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('Relationship table export plugin Online Help'), command=lambda: webbrowser.open(self._HELP_URL))

    def _export_table(self, csvDialect, csvEncoding):
        """Export the table as a csv file."""
        exportTargetFactory = ExportTargetFactory([CsvTable])
        try:
            self.kwargs['suffix'] = CsvTable.SUFFIX
            self.kwargs['csv_dialect'] = csvDialect
            self.kwargs['csv_encoding'] = csvEncoding
            __, target = exportTargetFactory.make_file_objects(self._ui.prjFile.filePath, **self.kwargs)
        except Exception as ex:
            self._ui.set_info_how(f'!{str(ex)}')
            return

        self._ui.refresh_tree()
        target.novel = self._ui.novel
        try:
            message = target.write()
        except Exception as ex:
            self._ui.set_info_how(f'!{str(ex)}')
        else:
            self._ui.set_info_how(message)
            if self.kwargs['show_exported']:
                if self._ui.ask_yes_no(_('Document "{}" created. Open now?').format(norm_path(target.filePath))):
                    open_document(target.filePath)

    def on_quit(self):
        """Actions to be performed when novelyst is closed.
        
        Save the project specific configuration
        """
        for keyword in self.kwargs:
            if keyword in self.configuration.options:
                self.configuration.options[keyword] = self.kwargs[keyword]
            elif keyword in self.configuration.settings:
                self.configuration.settings[keyword] = self.kwargs[keyword]
        self.configuration.write(self.iniFile)

