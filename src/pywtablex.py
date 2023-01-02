"""A test application for the novelyst_retablex plugin.

For further information see https://github.com/peter88213/novelyst_retablex
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import sys
import tkinter as tk
from pywriter.pywriter_globals import *
from pywriter.ui.main_tk import MainTk
from novelyst_retablex import Plugin

APPLICATION = 'Relationship table export'


class TableManager(MainTk):

    def __init__(self):
        kwargs = dict(
            yw_last_open='',
            root_geometry='800x600',
            )
        super().__init__(APPLICATION, **kwargs)

        # Export
        self.exportMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('Export'), menu=self.exportMenu)

        # Help
        self.helpMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('Help'), menu=self.helpMenu)

        self.plugin = Plugin()
        self.plugin.install(self)

    def refresh_tree(self):
        """Dummy"""


if __name__ == '__main__':
    ui = TableManager()
    ui.open_project(sys.argv[1])
    ui.start()

