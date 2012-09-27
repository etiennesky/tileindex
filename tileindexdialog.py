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
from ui_tileindex import Ui_TileIndex
# create the dialog for zoom to point
class TileIndexDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_TileIndex()
        self.ui.setupUi(self)
