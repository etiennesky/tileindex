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
        self.previewWidth = s.value('TileIndexPlugin/previewWidth', 1000, type=int)

        # activate/deactivate map canvas event filter
        self.transparentFix = ( s.value('TileIndexPlugin/transparentFix', True, type=bool ) == True )

        # activate/deactivate map canvas event filter
        if s.value('TileIndexPlugin/contextMenu', True, type=bool):
            if not self.filterActive:
                iface.mapCanvas().installEventFilter(self) 
                self.filterActive = True
        else:
            if self.filterActive:
                iface.mapCanvas().removeEventFilter(self) 
                self.filterActive = False

        # which attribute(s) should we look for to get raster file names?
        self.locationAttr=['location']
        if s.value('TileIndexPlugin/attribute', False, type=bool):
            # TODO change this
            attr=s.value('TileIndexPlugin/attributeStr', '', type=str).split(' ') #,QString.SkipEmptyParts)
            for a in attr:
                self.locationAttr.append(a)


    # checks that given vector layer has valid tile information, and at least one feature selected
    def checkLayerAttribute(self, layer, checkFeatures=True):
        fieldId = -1
        fieldStr = None

        if layer is not None and layer.type() == QgsMapLayer.VectorLayer:

            # get attribute id which contains "location" (or user-defined attribute)
            provider = layer.dataProvider()
            if QGis.QGIS_VERSION_INT >= 10900:
                fields = range(provider.fields().count())
            else:
                fields = provider.fields()
            for i in fields:
                if str(provider.fields()[i].name()).lower() in self.locationAttr:
                    fieldId = i
                    fieldStr = provider.fields()[i].name()
                    break
            if fieldId == -1:
                #print("TileIndex plugin : did not find a location attribute in layer")                    
                return (-1,None)

            # make sure there is at least 1 selected tile (if requested)
            if checkFeatures:
                featList = layer.selectedFeatures()
                if len(featList) == 0: 
                    print("TileIndex plugin : layer has no selected features")
                    return (-1,None)

            return (fieldId,fieldStr)

#        else:
#            print("layer not a vector layer")

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
        
        # get filenames in file
        files1 = []
        feat = QgsFeature()
        if selected:
            for feat in layer.selectedFeatures():
                if QGis.QGIS_VERSION_INT >= 10900:
                    fileName = feat.attribute(indexStr)
                else:
                    fileName = feat.attributeMap()[index]
                files1.append(fileName)
        else:
            selection = []
            if QGis.QGIS_VERSION_INT >= 10900:
                for feat in layer.getFeatures():
                    files1.append(feat.attribute(indexStr))
            else:
                provider = layer.dataProvider()
                provider.select(provider.attributeIndexes())
                while provider.nextFeature(feat):
                    files1.append(feat.attributeMap()[index])

        # now loop over files and build actual file list, including prefix
        files = []
        for fileName in files1:
            fileInfo = QFileInfo(fileName)
            if fileInfo.isRelative():
                if layerPath is None:
                    print("TileIndex plugin : tile has relative path %s but tileindex path is unknown..." % fileName)
                    continue
                fileName = layerPath + QDir.separator() + fileName
                fileInfo.setFile(fileName)
            if not fileInfo.exists():
                print("TileIndex plugin : raster file %s does not exist..." % fileName)
                continue
            files.append(fileName)
        
        if len(files)==0:
            return None
        else:
            return files

    # this method will add the given raster files to map registry
    def addTiles(self, layer, files):
        count = 0
        layers = []

        QApplication.setOverrideCursor( Qt.WaitCursor )       
        iface.mapCanvas().freeze(True)

        for fileName in files:
            print("TileIndex plugin : loading raster file %s" % fileName)           
            fileInfo = QFileInfo(fileName)
            rlayer = QgsRasterLayer(fileName, fileInfo.baseName())
            if rlayer is None:
                print("TileIndex plugin : raster file %s could not be loaded..." % fileName)
                continue
            layers.append(rlayer)
            count = count + 1

        print("TileIndex plugin : adding %d layers to map registry" % count) 
        QgsMapLayerRegistry.instance().addMapLayers(layers)
        iface.mapCanvas().freeze(False)
        iface.mapCanvas().refresh()
        print("TileIndex plugin : done adding layers")
        QApplication.restoreOverrideCursor()
                    
        # restore active layer if qgis >= 1.9
        if count > 0:
            if QGis.QGIS_VERSION_INT >= 10900:
                iface.legendInterface().setCurrentLayer(layer)
            else:
                iface.setActiveLayer(layer)
                

        return count


    # this method will add the selected tile raster files to map registry
    def addSelectedTiles(self, layer):
        files = self.getRasterFilenames(layer, True)
        if files is None or len(files)==0:
            return 0
        return self.addTiles(layer, files)


    # this method will add all tile raster files to map registry
    def addAllTiles(self, layer):
        files = self.getRasterFilenames(layer, False)
        if files is None or len(files)==0:
            return 0
        return self.addTiles(layer, files)


    def showPreview(self,layer):

        # don't do anything if this is not a tileindex file
        (index,indexStr) = self.checkLayerAttribute(layer, False)
        if index == -1:
            return

        layerPath = QFileInfo(layer.publicSource()).dir().path()
        if QFileInfo(layerPath).exists():
            #renderer = TileIndexRenderer(fieldId, fieldStr, layer, 500)
            renderer = TileIndexRenderer(layer)
            layer.setRendererV2(renderer)
            layer.setCacheImage( None )
            layer.triggerRepaint()


    # intercept map canvas right mouse clicks
    def eventFilter(self, obj, event):
        if event is None or self is None or QEvent is None:
            return False
        if event.type() == QEvent.ContextMenu:
            layer = iface.activeLayer()
            #if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
            (index,indexStr) = self.checkLayerAttribute( layer, False )
            if index != -1:
                globalPos = iface.mapCanvas().mapToGlobal(event.pos())
                myMenu = QMenu()
                str1 = self.tr("Add selected tile raster layer(s)")
                str3 = self.tr("Add all tile raster layer(s)")
                str2 = self.tr("Show tile previews in map")
                if len(layer.selectedFeatures()) != 0: 
                    myMenu.addAction(QIcon(":/plugins/tileindex/icon/mActionAddImage.png"),str1)
                myMenu.addAction(QIcon(":/plugins/tileindex/icon/mActionAddRasterLayer.png"),str3)
                myMenu.addAction(QIcon(":/plugins/tileindex/icon/mActionMapTips.png"),str2)
                selectedAction = myMenu.exec_(globalPos)
                if selectedAction:
                    if selectedAction.text() == str1:
                        count = self.addSelectedTiles( iface.activeLayer() )
                    elif selectedAction.text() == str3:
                        self.addAllTiles( iface.activeLayer() )
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

        if not QFileInfo(fileName).isFile():
            print("TileIndex plugin : raster %s is invalid" % fileName)
            return None

        # try to find layer in map registry or legend
        for layer in iface.legendInterface().layers() + QgsMapLayerRegistry.instance().mapLayers().values():
            #print(layer.name()+' - '+layer.publicSource())
            if layer and layer.isValid() and \
                    layer.type()==QgsMapLayer.RasterLayer and \
                    layer.publicSource() == fileName :
                rlayer = layer
                print("TileIndex plugin : found raster %s in legend or registry" % fileName)
                break

        if not rlayer:
            print("TileIndex plugin : reading raster %s" % fileName)
            rlayer = QgsRasterLayer(fileName, QFileInfo(fileName).baseName())

        if not rlayer or not rlayer.isValid():
            print("TileIndex plugin : raster %s is invalid" % fileName)
            return None

        #create pixmap from raster
        size = QSize(width,width * float(rlayer.height())/float(rlayer.width()))
        if ( QGis.QGIS_VERSION_INT >= 20300 ):
            # with qgis >= 2.3 (master) use previewAsImage for MTR, and set background as transparent
            if "previewAsImage" in dir(rlayer):
                pixmap = rlayer.previewAsImage(size,Qt.transparent,QImage.Format_ARGB32_Premultiplied)
            else:
                print("TileIndex plugin : using qgis >= 2.3 but QgsRasterLayer::previewAsImage() is missing... upgrade QGIS" )
                return None
        elif ( QGis.QGIS_VERSION_INT >= 10900 ) and ( "previewAsPixmap" in dir(rlayer) ):
            # with qgis >= 1.9 set background as transparent
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
