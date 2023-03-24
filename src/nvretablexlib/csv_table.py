"""Provide a class for csv relationship table representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-table
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import csv
from pywriter.pywriter_globals import *


class CsvTable:
    """csv relationship table representation.

    Public methods:
        write() -- Write instance variables to the file.

    Public instance variables:
        filePath: str -- path to the file (property with getter and setter). 

    Uses the conventions for Excel-generated CSV files.
    """
    DESCRIPTION = _('csv Table')
    EXTENSION = '.csv'
    SUFFIX = '_relationships'

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath: str -- path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.  
            
        Extends the superclass constructor.          
        """
        self.novel = None
        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a supported type as specified by EXTENSION.

        self.filePath = filePath
        self._csvArcTrue = kwargs.get('csv_arc_true', 'A')
        self._csvArcFalse = kwargs.get('csv_arc_false', '')
        self._csvChrTrue = kwargs.get('csv_chr_true', 'C')
        self._csvChrFalse = kwargs.get('csv_chr_false', '')
        self._csvLocTrue = kwargs.get('csv_loc_true', 'L')
        self._csvLocFalse = kwargs.get('csv_loc_false', '')
        self._csvItmTrue = kwargs.get('csv_itm_true', 'I')
        self._csvItmFalse = kwargs.get('csv_itm_false', '')
        self._csvRowNumbers = kwargs.get('csv_row_numbers', True)
        self._csvDialect = kwargs.get('csv_dialect', 'ecxel')
        self._csvEncoding = kwargs.get('csv_encoding', 'utf-8')
        self._csv_arcPoints = kwargs.get('csv_arc_points', False)

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Setter for the filePath instance variable.
                
        - Format the path string according to Python's requirements. 
        - Accept only filenames with the right suffix and extension.
        """
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath

    def write(self):
        """Write the relations to the file.
        
        Raise the "Error" exception in case of error. 
        This is a stub to be overridden by subclass methods.
        """
        try:
            with open(self.filePath, 'w', newline='', encoding=self._csvEncoding) as f:
                writer = csv.writer(f, dialect=self._csvDialect)

                # Get arcs.
                hasSubplot = False
                arcs = []
                scnArcs = {}
                for chId in self.novel.srtChapters:
                    for scId in self.novel.chapters[chId].srtScenes:
                        if self.novel.scenes[scId].scType == 0:
                            scnArcs[scId] = string_to_list(self.novel.scenes[scId].scnArcs)
                            for arc in scnArcs[scId]:
                                if not arc in arcs:
                                    arcs.append(arc)
                            if self.novel.scenes[scId].isSubPlot:
                                hasSubplot = True

                if hasSubplot and not arcs:
                    arcs.append('Subplot')
                    for scId in scnArcs:
                        if self.novel.scenes[scId].isSubPlot:
                            scnArcs[scId] = ['Subplot']

                # Title row.
                row = []
                if self._csvRowNumbers:
                    row.append('')
                row.append('')
                for arc in arcs:
                    row.append(arc)
                for crId in self.novel.characters:
                    row.append(self.novel.characters[crId].title)
                for lcId in self.novel.locations:
                    row.append(self.novel.locations[lcId].title)
                for itId in self.novel.items:
                    row.append(self.novel.items[itId].title)
                writer.writerow(row)

                # Scene rows.
                for i, scId in enumerate(scnArcs):
                    row = []
                    if self._csvRowNumbers:
                        row.append(i + 1)
                    row.append(self.novel.scenes[scId].title)
                    for arc in arcs:
                        if arc in scnArcs[scId]:
                            entry = self._csvArcTrue
                            if self._csv_arcPoints:
                                # Use arc point titles instead of binary marker.
                                pointIds = string_to_list(self.novel.scenes[scId].kwVar.get('Field_SceneAssoc', None))
                                points = []
                                for ptId in pointIds:
                                    if arc in self.novel.scenes[ptId].scnArcs:
                                        points.append(self.novel.scenes[ptId].title)
                                if points:
                                    entry = list_to_string(points)
                            row.append(entry)
                        else:
                            row.append(self._csvArcFalse)
                    for crId in self.novel.srtCharacters:
                        try:
                            if crId in self.novel.scenes[scId].characters:
                                row.append(self._csvChrTrue)
                            else:
                                row.append(self._csvChrFalse)
                        except:
                            row.append(self._csvChrFalse)
                    for lcId in self.novel.srtLocations:
                        try:
                            if lcId in self.novel.scenes[scId].locations:
                                row.append(self._csvLocTrue)
                            else:
                                row.append(self._csvLocFalse)
                        except:
                            row.append(self._csvLocFalse)
                    for itId in self.novel.srtItems:
                        try:
                            if itId in self.novel.scenes[scId].items:
                                row.append(self._csvItmTrue)
                            else:
                                row.append(self._csvItmFalse)
                        except:
                            row.append(self._csvItmFalse)
                    writer.writerow(row)
        except:
            raise Error(f'{_("Cannot write File")}: "{norm_path(self.filePath)}".')

        return (f'{_("File written")}: "{norm_path(self.filePath)}".')
