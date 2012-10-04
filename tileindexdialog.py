# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TileIndexDialog
                                 A QGIS plugin
 shows a preview for each tile and allows to open raster layer
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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QSettings, QVariant

from ui_tileindex import Ui_TileIndex

# create the dialog for zoom to point
class TileIndexDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_TileIndex()
        self.ui.setupUi(self)

        s = QSettings()
        self.ui.spinBoxWidth.setValue(s.value('TileIndexPlugin/previewWidth', 1000).toInt()[0])
        self.ui.checkBoxContext.setChecked(s.value('TileIndexPlugin/contextMenu', True).toBool())
        self.ui.checkBoxTransparent.setChecked(s.value('TileIndexPlugin/transparentFix', True).toBool())
        self.ui.groupBoxAttribute.setChecked(s.value('TileIndexPlugin/attribute', False).toBool())
        self.ui.lineEditAttribute.setText(s.value('TileIndexPlugin/attributeStr', '').toString())

    def accept(self):
        s = QSettings()
        s.setValue('TileIndexPlugin/previewWidth', QVariant(self.ui.spinBoxWidth.value()))
        if not self.ui.checkBoxContext.isChecked():
            s.setValue('TileIndexPlugin/contextMenu', False)
        else:
            s.remove('TileIndexPlugin/contextMenu')
        if not self.ui.checkBoxTransparent.isChecked():
            s.setValue('TileIndexPlugin/transparentFix', False)
        else:
            s.remove('TileIndexPlugin/transparentFix')
        if self.ui.groupBoxAttribute.isChecked():
            s.setValue('TileIndexPlugin/attribute', True)
        else:
            s.setValue('TileIndexPlugin/attribute', False)
        attrStr = self.ui.lineEditAttribute.text()
        if not attrStr.isNull():
            s.setValue('TileIndexPlugin/attributeStr', QVariant(attrStr))
        else:
            s.remove('TileIndexPlugin/attributeStr')
        QtGui.QDialog.accept(self)
