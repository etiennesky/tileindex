# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TileIndex
                                 A QGIS plugin
 allows to open raster layers in tile index with right-click action in map canvas and icon/menu entry
                              -------------------
        begin                : 2012-09-27
        copyright            : (C) 2012 by Etienne Tourigny
        email                : etienne.dev at gmail dot com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from tileindexdialog import TileIndexDialog
# Import the code for utils
#from tileindexutil import tileindexutil, TileIndexUtil
import tileindexutil
# Import the code for symbology
from tileindexfillsymbollayer import *

class TileIndex(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        # Save reference to the QGIS interface
        self.iface = iface
        # Create the dialog and keep reference
        self.dlg = TileIndexDialog()
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/tileindex"
        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale").toString()[0:2]
       
        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/tileindex_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
  

    def initGui(self):
        # Create action that will start plugin configuration
        self.action_dlg = QAction(u"Preferences", self.iface.mainWindow())
        self.action_add_tiles = QAction(QIcon(":/plugins/tileindex/icon.png"), \
            u"Add selected tile raster layer(s)", self.iface.mainWindow())
        self.action_show_preview = QAction(u"Show tile previews in map", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action_dlg, SIGNAL("triggered()"), self.run_dlg)
        QObject.connect(self.action_add_tiles, SIGNAL("triggered()"), self.run_add_tiles)
        QObject.connect(self.action_show_preview, SIGNAL("triggered()"), self.run_show_preview)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action_add_tiles)
        self.iface.addPluginToMenu(u"&Tile Index", self.action_dlg)
        self.iface.addPluginToMenu(u"&Tile Index", self.action_add_tiles)
        self.iface.addPluginToMenu(u"&Tile Index", self.action_show_preview)

        tileindexutil.tileindexutil.checkSettings()

        QgsSymbolLayerV2Registry.instance().addSymbolLayerType(PixmapFillSymbolLayerMetadata())
        QgsRendererV2Registry.instance().addRenderer(TileIndexRendererMetadata())


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Tile Index",self.action_dlg)
        self.iface.removePluginMenu(u"&Tile Index",self.action_add_tiles)
        self.iface.removePluginMenu(u"&Tile Index",self.action_show_preview)
        self.iface.removeToolBarIcon(self.action_show_preview)


    # opens the prefs. dialog
    def run_dlg(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            tileindexutil.tileindexutil.checkSettings()
            pass


    # adds selected tiles
    def run_add_tiles(self):
        # add selected tile rasters
        count = tileindexutil.tileindexutil.addSelectedTiles( self.iface.activeLayer() )


    # adds slected tiles
    def run_show_preview(self):
        # add selected tile rasters
        count = tileindexutil.tileindexutil.showPreview(self.iface.activeLayer() )

