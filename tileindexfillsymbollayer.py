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

from ui_tileindexrenderwidgetbase import Ui_TileIndexRenderWidgetBase

# Import the code for utils
import tileindexutil


class PixmapFillSymbolLayer(QgsFillSymbolLayerV2):

    def __init__(self, path, pixmap):
        QgsFillSymbolLayerV2.__init__(self)
        self.path = path
        self.pixmap = pixmap
        #if self.pixmap is None:
        #    self.pixmap = QPixmap()

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
            print('TileIndex plugin : polygon with rings not supported, ignoring inner rings')

        painter = context.renderContext().painter()    

        # draw pixmap
        if self.pixmap and not self.pixmap.isNull():
            if QGis.QGIS_VERSION_INT >= 10900:

                # compute boundingBox of feature, in case it falls outside of current extent
                ct = iface.mapCanvas().getCoordinateTransform()
                bbox = context.feature().geometry().boundingBox()
                bbox = QgsRectangle(ct.transform(QgsPoint(bbox.xMinimum(),bbox.yMaximum())), \
                                      ct.transform(QgsPoint(bbox.xMaximum(),bbox.yMinimum())))
                bbox = QRect(bbox.xMinimum(),bbox.yMinimum(),bbox.width(),bbox.height())
                          
                if isinstance(self.pixmap,QImage):
                    painter.drawImage(bbox,self.pixmap)
                else:
                    painter.drawPixmap(bbox,self.pixmap)

            else:
                if isinstance(self.pixmap,QImage):
                    painter.drawImage(points.boundingRect().toRect(),self.pixmap)
                else:
                    painter.drawPixmap(points.boundingRect().toRect(),self.pixmap)

        # draw border (selection color if selected)
        backupPen = painter.pen()
        pen = QPen()
        pen.setWidth(2)
        if context.selected():
            pen.setColor(context.renderContext().selectionColor())
        painter.setPen(pen)

        painter.drawPolygon(points)
        painter.setPen(backupPen)


    def clone(self):
        return PixmapFillSymbolLayer(self.path, self.pixmap)

	
class PixmapFillSymbolLayerMetadata(QgsSymbolLayerV2AbstractMetadata):

  def __init__(self):
    QgsSymbolLayerV2AbstractMetadata.__init__(self, "TileIndexFill", "Tile Index Fill", QgsSymbolV2.Fill)

  def createSymbolLayer(self, props):
      path = str(props["path"]) if "path" in props else ""
      return PixmapFillSymbolLayer(path,width)

  def createSymbolLayerWidget(self):
    #return PixmapFillSymbolLayerWidget()
    return None


class TileIndexRenderer(QgsFeatureRendererV2):

    def __init__(self, layer, width=0, attrId=None, attrStr=None, pixmaps=dict(), showLabels=True, clone=False):
        QgsFeatureRendererV2.__init__(self, "TileIndexRenderer")

        self.symbolOk = True
        self.showLabels = showLabels

        if width == 0:
            self.width = tileindexutil.tileindexutil.previewWidth
        else:
            self.width = width

        # get layerPath
        self.layerPath = QFileInfo(layer.publicSource()).dir().path()
        self.layer = layer
        if not QFileInfo(self.layerPath).exists():
            print("TileIndex plugin : layer %s does not exist" % self.layerPath)
            self.layerPath = None

        # get attribute where filename is stored
        self.attrStr = None
        if attrId is None or attrStr is None:
            (self.attrId, self.attrStr) = tileindexutil.tileindexutil.checkLayerAttribute(layer, False)
        else:
            self.attrId = attrId
            self.attrStr = attrStr
        if self.attrId is None or self.attrId == -1:
            print("TileIndex plugin : location attribute not found")
            self.symbolOk = False

        # add label using old label interface when object is first created
        label = self.layer.label()
        label.setLabelField(QgsLabel.Text, self.attrId)
        if not self.showLabels:
            self.layer.enableLabels(self.showLabels)
        if not clone:
            labelAttr = label.labelAttributes()
            labelAttr.setSize(12, QgsLabelAttributes.PointUnits)
            self.layer.enableLabels(self.showLabels)

        # setup pixmap dict and symbols
        self.pixmaps = pixmaps # map with key=fileName and value=pixmap
        self.pixmapSymbol = QgsFillSymbolV2()
        self.defaultSymbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)

    def symbolForFeature(self, feature):

        self.symbolOk = False
        if self.layerPath is None:
            return self.defaultSymbol

        # get fileName for feature
        if QGis.QGIS_VERSION_INT >= 10900:
            # this has not been tested when attribute is missing, but shouldn't get here anyway
            fileName = feature[self.attrStr]
            if fileName == '':
                return self.defaultSymbol
            fileName = fileName
        else:
            attrMap = feature.attributeMap()
            if not self.attrId in attrMap:
                return self.defaultSymbol
            fileName = attrMap[self.attrId]
        if QFileInfo(fileName).isRelative():
            if self.layerPath is None:
                print("TileIndex plugin : tile has relative path %s but tileindex path is unknown..." % fileName)
                return self.defaultSymbol
            fileName = self.layerPath + QDir.separator() + fileName
        if not QFileInfo(fileName).isFile():
            print("TileIndex plugin : got invalid raster %s for feature #%d, attribute %s" % (fileName,feature.id(),self.attrStr))
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
            if self.showLabels and not self.layer.hasLabelsEnabled():
                self.layer.enableLabels(True)
                self.layer.drawLabels(context)
                self.layer.enableLabels(False)
        else:
            self.defaultSymbol.stopRender(context)
        pass
    
    def usedAttributes(self):
        if self.attrStr is None:
            return []
        return [ self.attrStr ]
  
    def clone(self):
        return TileIndexRenderer(self.layer, self.width, self.attrId, self.attrStr, self.pixmaps, self.showLabels, True)

    def setWidth(self,width):
        if self.width != width:
            self.width = width
            self.pixmaps = []

    def setLocationAttribute(self,attrId,attrStr):
        if self.attrId != attrId and self.attrStr != attrStr:
            self.attrId = attrId
            self.attrStr = attrStr
            self.pixmaps = []



class TileIndexRendererWidget(QgsRendererV2Widget,Ui_TileIndexRenderWidgetBase):
    def __init__(self, layer, style, renderer):
        QgsRendererV2Widget.__init__(self, layer, style)
        if renderer is None or renderer.type() != "TileIndexRenderer":
            self.r = TileIndexRenderer(layer)
        else:
            self.r = renderer

        # setup UI
        self.setupUi(self)
        self.spinBoxWidth.setValue(self.r.width)
        provider = layer.dataProvider()
        for i in provider.fields():
            self.comboBoxAttr.addItem(provider.fields()[i].name())
        if self.r.attrId is not None and self.r.attrId > 0:
            self.comboBoxAttr.setCurrentIndex(self.r.attrId)
        # workaround that we can't activate show labels in UI
        self.checkBoxShowLabels.setChecked(self.r.showLabels)
        self.connect(self.spinBoxWidth, SIGNAL("editingFinished()"), self.setWidth)
        self.connect(self.comboBoxAttr, SIGNAL("currentIndexChanged(const QString&)"), self.setLocationAttribute)
        self.connect(self.checkBoxShowLabels, SIGNAL("toggled(bool)"), self.setShowLabels)

    def setWidth(self):
        if self.r.type() == "TileIndexRenderer":
            self.r.setWidth(self.spinBoxWidth.value())

    def setLocationAttribute(self):
        if self.r.type() == "TileIndexRenderer":
            self.r.setLocationAttribute(self.comboBoxAttr.currentIndex(),self.comboBoxAttr.currentText())

    def setShowLabels(self,checked):
        if self.r.type() == "TileIndexRenderer":
            self.r.showLabels = checked

    def renderer(self):
        return self.r


class TileIndexRendererMetadata(QgsRendererV2AbstractMetadata):

    def __init__(self):
        QgsRendererV2AbstractMetadata.__init__(self, "TileIndexRenderer", "TileIndex renderer")
        
    def createRenderer(self, element):
        return TileIndexRenderer()

    def createRendererWidget(self, layer, style, renderer):
        return TileIndexRendererWidget(layer, style, renderer)


