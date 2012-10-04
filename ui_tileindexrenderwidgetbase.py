# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_tileindexrenderwidgetbase.ui'
#
# Created: Thu Oct  4 14:01:35 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TileIndexRenderWidgetBase(object):
    def setupUi(self, TileIndexRenderWidgetBase):
        TileIndexRenderWidgetBase.setObjectName(_fromUtf8("TileIndexRenderWidgetBase"))
        TileIndexRenderWidgetBase.resize(383, 163)
        TileIndexRenderWidgetBase.setWindowTitle(QtGui.QApplication.translate("TileIndexRenderWidgetBase", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(TileIndexRenderWidgetBase)
        self.gridLayout.setMargin(10)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.comboBoxAttr = QtGui.QComboBox(TileIndexRenderWidgetBase)
        self.comboBoxAttr.setObjectName(_fromUtf8("comboBoxAttr"))
        self.gridLayout.addWidget(self.comboBoxAttr, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(TileIndexRenderWidgetBase)
        self.label_3.setText(QtGui.QApplication.translate("TileIndexRenderWidgetBase", "Note: label properties (but not field) can be changed in labels tab", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.spinBoxWidth = QtGui.QSpinBox(TileIndexRenderWidgetBase)
        self.spinBoxWidth.setMaximum(9999)
        self.spinBoxWidth.setObjectName(_fromUtf8("spinBoxWidth"))
        self.gridLayout.addWidget(self.spinBoxWidth, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(TileIndexRenderWidgetBase)
        self.label_2.setText(QtGui.QApplication.translate("TileIndexRenderWidgetBase", "File name attribute", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label = QtGui.QLabel(TileIndexRenderWidgetBase)
        self.label.setText(QtGui.QApplication.translate("TileIndexRenderWidgetBase", "Preview image width", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem2, 0, 0, 1, 1)
        self.checkBoxShowLabels = QtGui.QCheckBox(TileIndexRenderWidgetBase)
        self.checkBoxShowLabels.setText(QtGui.QApplication.translate("TileIndexRenderWidgetBase", "Display labels with file name", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxShowLabels.setObjectName(_fromUtf8("checkBoxShowLabels"))
        self.gridLayout.addWidget(self.checkBoxShowLabels, 3, 0, 1, 1)

        self.retranslateUi(TileIndexRenderWidgetBase)
        QtCore.QMetaObject.connectSlotsByName(TileIndexRenderWidgetBase)

    def retranslateUi(self, TileIndexRenderWidgetBase):
        pass

