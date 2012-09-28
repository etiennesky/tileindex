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
        self.action = QAction(QIcon(":/plugins/tileindex/icon.png"), \
            u"Tile Index", self.iface.mainWindow())
        self.action2 = QAction(u"Preferences", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        QObject.connect(self.action2, SIGNAL("triggered()"), self.run2)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Tile Index", self.action)
        self.iface.addPluginToMenu(u"&Tile Index", self.action2)

        self.filterActive = False
        self.checkSettings()


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Tile Index",self.action)
        self.iface.removePluginMenu(u"&Tile Index",self.action2)
        self.iface.removeToolBarIcon(self.action)


    # run method that performs all the real work
    # this method opens the prefs. dialog
    def run2(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            self.checkSettings()
            pass


    # run method that performs all the real work
    def run(self):
        # add selected tile rasters
        count = self.addSelectedTiles( self.iface.activeLayer() )


    # checks settings
    def checkSettings(self):
        s = QSettings()

        # activate/deactivate map canvas event filter
        if s.value('TileIndexPlugin/contextMenu', True).toBool():
            if not self.filterActive:
                self.iface.mapCanvas().installEventFilter(self) 
                self.filterActive = True
        else:
            if self.filterActive:
                self.iface.mapCanvas().removeEventFilter(self) 
                self.filterActive = False

        # which attribute(s) should we look for to get raster file names?
        self.locationAttr=['location']
        if s.value('TileIndexPlugin/attribute', False).toBool():
            attr=s.value('TileIndexPlugin/attributeStr', '').toString().split(' ',QString.SkipEmptyParts)
            for a in attr:
                #print(a)
                self.locationAttr.append(a)


    # this method will add the selected tile raster files
    def addSelectedTiles(self, layer, index=-1):
        # test layer is valid and get "location" attribute index
        if index == -1:
            index = self.checkLayerAttribute(layer)
        if index == -1:
            return 0
        #print("layer has location field")
     
        # make sure file exists and get dir name (to know raster file location)
        layerPath = QFileInfo(layer.publicSource()).dir().path()
        if not QFileInfo(layerPath).exists():
            layerPath = None
        
        feat = QgsFeature()
        provider = layer.dataProvider()
        count = 0
        for feat in layer.selectedFeatures():
            fileName = feat.attributeMap()[index].toString()
            fileInfo = QFileInfo(fileName)
            #print(str(fileName)+" - "+str(fileInfo.isRelative()))
            if fileInfo.isRelative():
                if layerPath is None:
                    print("tile has relative path %s but tileindex path is unknown..." % fileName)
                    continue
                fileName = layerPath + QDir.separator() + fileName
                fileInfo.setFile(fileName)
            print("adding raster "+str(fileName))
            if not fileInfo.exists():
                print("raster file %s does not exist..." % fileName)
                continue
            rlayer = QgsRasterLayer(fileName, fileInfo.baseName())
            if rlayer is None:
                print("raster file %s could not be loaded..." % fileName)
                continue
            QgsMapLayerRegistry.instance().addMapLayer(rlayer)
            count = count + 1
                    
        print("%d tile rasters added" % count)

        # restore active layer - unfortunately this does not show in the legend...
        #if count > 0:
        #    self.iface.setActiveLayer(layer)

        return count


    # checks that given vector layer has valid tile information, and at least one feature selected
    def checkLayerAttribute(self, layer):
        index = -1
        if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
            # get attribute id which contains "location" (or user-defined attribute)
            provider = layer.dataProvider()
            for i in provider.fields():
                #if provider.fields()[i].name() == "location":
                if provider.fields()[i].name() in self.locationAttr:
                    index = i
                    break
            if index == -1:
                print("did not find a location attribute in layer")                    
                return -1
            # make sure there is at least 1 selected tile
            featList = layer.selectedFeatures()
            if len(featList) == 0: 
                print("layer has no selected features")
                return -1
            return index 

        #print("layer has "+str(len(featList))+" selected features")
        else:
            print("layer not a vector layer")

        return -1

    # intercept map canvas right mouse clicks
    def eventFilter(self, obj, event):
        if event is None or self is None:
            return False
        if event.type() == QEvent.ContextMenu:
            layer = self.iface.activeLayer()
            #if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
            index = self.checkLayerAttribute( layer )
            if index != -1:
                globalPos = self.iface.mapCanvas().mapToGlobal(event.pos())
                myMenu = QMenu()
                myMenu.addAction("Add selected tile raster(s)")
                selectedItem = myMenu.exec_(globalPos)
                if selectedItem:
                    count = self.addSelectedTiles( self.iface.activeLayer() )
                    return True
                return False

        return False
