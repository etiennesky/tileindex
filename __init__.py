# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TileIndex
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
 This script initializes the plugin, making it known to QGIS.
"""
def name():
    return "Tile Index Viewer"
def description():
    return "shows a preview of MapServer tile index rasters and allows to open raster layers"
def version():
    return "Version 0.2"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.0"
def author():
  return "Etienne Tourigny"
def author():
  return "Etienne Tourigny"
def email():
  return "etourigny.dev@gmail.com"
def classFactory(iface):
    # load TileIndex class from file TileIndex
    from tileindex import TileIndex
    return TileIndex(iface)
