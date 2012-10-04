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
from qgis.gui import *
from qgis.utils import iface

# Import the code for utils
import tileindexutil


class PixmapFillSymbolLayer(QgsFillSymbolLayerV2):

    def __init__(self, path, pixmap):
        QgsFillSymbolLayerV2.__init__(self)
        self.path = path
        self.pixmap = pixmap
        if self.pixmap is None:
            self.pixmap = QPixmap()

    def layerType(self):
        return "TileIndexFill"

    def properties(self):
        return { "path" : str(self.path) }

    def startRender(self, context):
        pass

    def stopRender(self, context):
        pass

    def renderPolygon(self, points, rings, context):
        if rings is not None:
            print('polygon with rings not supported, ignoring inner rings')

        painter = context.renderContext().painter()    

        # draw pixmap
        if self.pixmap is not None and not self.pixmap.isNull():

            # compute boundingBox of feature, in case it falls outside of current extent
            ct = iface.mapCanvas().getCoordinateTransform()
            bbox = context.feature().geometry().boundingBox()
            bbox = QgsRectangle(ct.transform(QgsPoint(bbox.xMinimum(),bbox.yMaximum())), \
                                  ct.transform(QgsPoint(bbox.xMaximum(),bbox.yMinimum())))
            bbox = QRect(bbox.xMinimum(),bbox.yMinimum(),bbox.width(),bbox.height())

            painter.drawPixmap(bbox,self.pixmap)
            
        # draw border (selection color if selected)
        backupPen = painter.pen()
        pen = QPen()
        pen.setWidth(2)
        if context.selected():
            pen.setColor(context.selectionColor())
        painter.setPen(pen)

        painter.drawPolygon(points)
        painter.setPen(backupPen)


    def clone(self):
        return PixmapFillSymbolLayer(self.path, self.pixmap)

	
class PixmapFillSymbolLayerMetadata(QgsSymbolLayerV2AbstractMetadata):

  def __init__(self):
    QgsSymbolLayerV2AbstractMetadata.__init__(self, "TileIndexFill", "Tile Index Fill", QgsSymbolV2.Fill)

  def createSymbolLayer(self, props):
      path = str(props[QString("path")]) if QString("path") in props else ""
      return PixmapFillSymbolLayer(path,width)

  def createSymbolLayerWidget(self):
    #return PixmapFillSymbolLayerWidget()
    return None


class TileIndexRenderer(QgsFeatureRendererV2):

    def __init__(self, layer, width=0, attrId=None, attrStr=None):
        QgsFeatureRendererV2.__init__(self, "TileIndexRenderer")

        self.layerPath = QFileInfo(layer.publicSource()).dir().path()
        self.layer = layer
        if width == 0:
            self.width = tileindexutil.tileindexutil.previewWidth
        else:
            self.width = width

        if attrId is None or attrStr is None:
            (self.attrId, self.attrStr) = tileindexutil.tileindexutil.checkLayerAttribute(layer, False)
        else:
            self.attrId = attrId
            self.attrStr = attrStr
        if self.attrId is None or self.attrId == -1:
            print("location attribute not found")

        if not QFileInfo(self.layerPath).exists():
            print("layer %s does not exist" % self.layerPath)
            self.layerPath = None

        self.pixmaps = dict() # map with key=fileName and value=pixmap
        self.pixmapSymbol = QgsFillSymbolV2()
        self.defaultSymbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
        self.symbolOk = False

    def symbolForFeature(self, feature):

        self.symbolOk = False
        if self.layerPath is None:
            return self.defaultSymbol

        # get fileName for feature
        attrMap = feature.attributeMap()
        if not self.attrId in attrMap:
            return self.defaultSymbol
        fileName = attrMap[self.attrId].toString()
        if QFileInfo(fileName).isRelative():
            if self.layerPath is None:
                print("tile has relative path %s but tileindex path is unknown..." % fileName)
                return self.defaultSymbol
            fileName = QString(self.layerPath + QDir.separator() + fileName) 
        if not QFileInfo(fileName).isFile():
            print("got invalid raster %s for feature #%d, attribute %s" % (fileName,feature.id(),self.attrStr))
            return self.defaultSymbol

        # create pixmap if needed and add to pixmaps map
        if fileName not in self.pixmaps:
            self.pixmaps[fileName] = tileindexutil.tileindexutil.rasterThumbnail(fileName,self.width)
        # add symbol layer to symbol
        symbolLayer = PixmapFillSymbolLayer(fileName,self.pixmaps[fileName])    
        self.pixmapSymbol.deleteSymbolLayer(0)        
        self.pixmapSymbol.appendSymbolLayer(symbolLayer)

        self.symbolOk = True
        return self.pixmapSymbol

    def startRender(self, context, vlayer):
        if self.symbolOk:
            self.pixmapSymbol.startRender(context)
        else:
            self.defaultSymbol.startRender(context)
        pass

    def stopRender(self, context):
        if self.symbolOk:
            self.pixmapSymbol.stopRender(context)
        else:
            self.defaultSymbol.stopRender(context)
        pass
    
    def usedAttributes(self):
        return [ self.attrStr ]
  
    def clone(self):
        return TileIndexRenderer(self.layer, self.width, self.attrId, self.attrStr)

    def setWidth(self,width):
        if self.width != width:
            self.width = width
            self.pixmaps = []

    def setLocationAttribute(self,attrId,attrStr):
        if self.attrId != attrId and self.attrStr != attrStr:
            self.attrId = attrId
            self.attrStr = attrStr
            self.pixmaps = []



class TileIndexRendererWidget(QgsRendererV2Widget):
    def __init__(self, layer, style, renderer):
        QgsRendererV2Widget.__init__(self, layer, style)
        if renderer is None or renderer.type() != "TileIndexRenderer":
            self.r = TileIndexRenderer(layer)
        else:
            self.r = renderer

        # setup UI
        self.spinBoxWidth = QSpinBox()
        self.spinBoxWidth.setMaximum(10000)
        self.spinBoxWidth.setValue(self.r.width)

        self.comboBoxAttr = QComboBox()
        provider = layer.dataProvider()
        for i in provider.fields():
            self.comboBoxAttr.addItem(provider.fields()[i].name())
        if self.r.attrId is not None and self.r.attrId > 0:
            self.comboBoxAttr.setCurrentIndex(self.r.attrId)

        self.grid = QGridLayout()
        self.grid.addWidget(QLabel(self.tr("Preview width")),0,0)
        self.grid.addWidget(self.spinBoxWidth,0,1)
        self.grid.addWidget(QLabel(self.tr("Location attribute")),1,0)
        self.grid.addWidget(self.comboBoxAttr,1,1)
        self.setLayout(self.grid)

        self.connect(self.spinBoxWidth, SIGNAL("editingFinished()"), self.setWidth)
        self.connect(self.comboBoxAttr, SIGNAL("currentIndexChanged (const QString&)"), self.setLocationAttribute)

    def setWidth(self):
        if self.r.type() == "TileIndexRenderer":
            self.r.setWidth(self.spinBoxWidth.value())

    def setLocationAttribute(self):
        if self.r.type() == "TileIndexRenderer":
            self.r.setLocationAttribute(self.comboBoxAttr.currentIndex(),self.comboBoxAttr.currentText())

    def renderer(self):
        return self.r


class TileIndexRendererMetadata(QgsRendererV2AbstractMetadata):

    def __init__(self):
        QgsRendererV2AbstractMetadata.__init__(self, "TileIndexRenderer", "TileIndex renderer")
        
    def createRenderer(self, element):
        return TileIndexRenderer()

    def createRendererWidget(self, layer, style, renderer):
        return TileIndexRendererWidget(layer, style, renderer)


