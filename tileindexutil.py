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
from qgis.utils import iface

# Import the code for symbology
from tileindexfillsymbollayer import *


class TileIndexUtil(QObject):

    def __init__(self):
        QObject.__init__(self)
        
        self.filterActive = False
        self.transparentFix = True
        self.locationAttr = []
        self.previewWidth = 1000

    def instance():
        return 

    # checks settings
    def checkSettings(self):
        s = QSettings()

        # pixmap preview width
        self.previewWidth = s.value('TileIndexPlugin/previewWidth', 1000).toInt()[0]

        # activate/deactivate map canvas event filter
        self.transparentFix = ( s.value('TileIndexPlugin/transparentFix', True).toBool() == True )

        # activate/deactivate map canvas event filter
        if s.value('TileIndexPlugin/contextMenu', True).toBool():
            if not self.filterActive:
                iface.mapCanvas().installEventFilter(self) 
                self.filterActive = True
        else:
            if self.filterActive:
                iface.mapCanvas().removeEventFilter(self) 
                self.filterActive = False

        # which attribute(s) should we look for to get raster file names?
        self.locationAttr=['location']
        if s.value('TileIndexPlugin/attribute', False).toBool():
            attr=s.value('TileIndexPlugin/attributeStr', '').toString().split(' ',QString.SkipEmptyParts)
            for a in attr:
                self.locationAttr.append(a)


    # checks that given vector layer has valid tile information, and at least one feature selected
    def checkLayerAttribute(self, layer, checkFeatures=True):
        fieldId = -1
        fieldStr = None

        if layer is not None and layer.type() == QgsMapLayer.VectorLayer:

            # get attribute id which contains "location" (or user-defined attribute)
            provider = layer.dataProvider()
            for i in provider.fields():
                #if provider.fields()[i].name() == "location":
                if provider.fields()[i].name() in self.locationAttr:
                    fieldId = i
                    fieldStr = provider.fields()[i].name()
                    break
            if fieldId == -1:
                print("did not find a location attribute in layer")                    
                return (-1,None)

            # make sure there is at least 1 selected tile (if requested)
            if checkFeatures:
                featList = layer.selectedFeatures()
                if len(featList) == 0: 
                    print("layer has no selected features")
                    return (-1,None)

            return (fieldId,fieldStr)

        else:
            print("layer not a vector layer")

        return (-1,None)


    def getRasterFilenames(self, layer, selected=False, index=-1):
        # test layer is valid and get "location" attribute index
        if index == -1:
            (index,indexStr) = self.checkLayerAttribute(layer, selected)
        if index == -1:
            return None
     
        # make sure file exists and get dir name (to know raster file location)
        layerPath = QFileInfo(layer.publicSource()).dir().path()
        if not QFileInfo(layerPath).exists():
            layerPath = None
        
        # get feature list, depending on selected flag - is there not an automatic way to loop with same logic?
        feat = QgsFeature()
        if selected:
            selection = layer.selectedFeatures()
        else:
            selection = []
            provider = layer.dataProvider()
            provider.select(provider.attributeIndexes())
            while provider.nextFeature(feat):
                selection.append(feat)

        # now loop over selection and build file list
        files = []
        for feat in selection:
            fileName = feat.attributeMap()[index].toString()
            fileInfo = QFileInfo(fileName)
            if fileInfo.isRelative():
                if layerPath is None:
                    print("tile has relative path %s but tileindex path is unknown..." % fileName)
                    continue
                fileName = layerPath + QDir.separator() + fileName
                fileInfo.setFile(fileName)
            if not fileInfo.exists():
                print("raster file %s does not exist..." % fileName)
                continue
            files.append(fileName)
        
        if len(files)==0:
            return None
        else:
            return files

    # this method will add the selected tile raster files to map registry
    def addSelectedTiles(self, layer):
        files = self.getRasterFilenames(layer, True)
        if files is None or len(files)==0:
            return 0
        count = 0
        for fileName in files:
            fileInfo = QFileInfo(fileName)
            rlayer = QgsRasterLayer(fileName, fileInfo.baseName())
            if rlayer is None:
                print("raster file %s could not be loaded..." % fileName)
                continue
            QgsMapLayerRegistry.instance().addMapLayer(rlayer)
            count = count + 1
                    
        #print("%d tile rasters added" % count)

        # restore active layer - unfortunately this does not show in the legend...
        #if count > 0:
        #    iface.setActiveLayer(layer)

        return count


    def showPreview(self,layer):

        # make sure file exists
        layerPath = QFileInfo(layer.publicSource()).dir().path()
        if QFileInfo(layerPath).exists():
            #renderer = TileIndexRenderer(fieldId, fieldStr, layer, 500)
            renderer = TileIndexRenderer(layer)
            layer.setRendererV2(renderer)
            layer.setCacheImage( None )
            layer.triggerRepaint()


    # intercept map canvas right mouse clicks
    def eventFilter(self, obj, event):
        if event is None or self is None:
            return False
        if event.type() == QEvent.ContextMenu:
            layer = iface.activeLayer()
            #if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
            (index,indexStr) = self.checkLayerAttribute( layer, False )
            if index != -1:
                globalPos = iface.mapCanvas().mapToGlobal(event.pos())
                myMenu = QMenu()
                str1 = self.tr("Add selected tile raster layer(s)")
                str2 = self.tr("Show tile previews in map")
                if len(layer.selectedFeatures()) != 0: 
                    myMenu.addAction(str1)
                myMenu.addAction(str2)
                selectedAction = myMenu.exec_(globalPos)
                if selectedAction:
                    if selectedAction.text() == str1:
                        count = self.addSelectedTiles( iface.activeLayer() )
                    elif selectedAction.text() == str2:
                        self.showPreview(layer)
                    else:
                        return False
                    return True
                return False

        return False

    def rasterThumbnail(self, fileName, width):
        pixmap = None
        rlayer = None

        if QFileInfo(fileName).isFile:
            print("reading raster %s" % fileName)
            rlayer = QgsRasterLayer(fileName, QFileInfo(fileName).baseName())
        if rlayer is None or not rlayer.isValid():
                print("raster %s is invalid" % fileName)
        else:

            size = QSize(width,width * float(rlayer.height())/float(rlayer.width()))
            
            if int(QGis.QGIS_VERSION[2]) and "previewAsPixmap2" in dir(rlayer) > 8: # for QGIS > 1.8
                # with qgis > 1.8 (master) set background as transparent
                pixmap = rlayer.previewAsPixmap(size,Qt.transparent)
            else:
                pixmap = QPixmap(size)
                rlayer.thumbnailAsPixmap(pixmap)
                # with qgis <= 1.8 add transparency where there are white pixels
                if self.transparentFix:
                    mask = pixmap.createMaskFromColor(QColor(255, 255, 255), Qt.MaskInColor)
                    pixmap.setMask(mask)

        return pixmap


# add static member for external access
tileindexutil = TileIndexUtil()
