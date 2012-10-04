# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_tileindex.ui'
#
# Created: Wed Oct  3 20:10:54 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TileIndex(object):
    def setupUi(self, TileIndex):
        TileIndex.setObjectName(_fromUtf8("TileIndex"))
        TileIndex.resize(309, 207)
        TileIndex.setWindowTitle(QtGui.QApplication.translate("TileIndex", "TileIndex", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(TileIndex)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(TileIndex)
        self.label_2.setText(QtGui.QApplication.translate("TileIndex", "Preview width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.spinBoxWidth = QtGui.QSpinBox(TileIndex)
        self.spinBoxWidth.setMaximum(10000)
        self.spinBoxWidth.setObjectName(_fromUtf8("spinBoxWidth"))
        self.gridLayout.addWidget(self.spinBoxWidth, 0, 1, 1, 1)
        self.checkBoxContext = QtGui.QCheckBox(TileIndex)
        self.checkBoxContext.setText(QtGui.QApplication.translate("TileIndex", "Add right-click context menu to canvas  map", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxContext.setObjectName(_fromUtf8("checkBoxContext"))
        self.gridLayout.addWidget(self.checkBoxContext, 1, 0, 1, 2)
        self.checkBoxTransparent = QtGui.QCheckBox(TileIndex)
        self.checkBoxTransparent.setText(QtGui.QApplication.translate("TileIndex", "Set white pixels transparent (bugfix for QGIS < 1.9)", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxTransparent.setObjectName(_fromUtf8("checkBoxTransparent"))
        self.gridLayout.addWidget(self.checkBoxTransparent, 2, 0, 1, 2)
        self.groupBoxAttribute = QtGui.QGroupBox(TileIndex)
        self.groupBoxAttribute.setTitle(QtGui.QApplication.translate("TileIndex", "Location attribute", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBoxAttribute.setCheckable(True)
        self.groupBoxAttribute.setChecked(False)
        self.groupBoxAttribute.setObjectName(_fromUtf8("groupBoxAttribute"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBoxAttribute)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.groupBoxAttribute)
        self.label.setText(QtGui.QApplication.translate("TileIndex", "Look for raster filenames in these attributes\n"
"(in addtion to \'location\')", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.lineEditAttribute = QtGui.QLineEdit(self.groupBoxAttribute)
        self.lineEditAttribute.setToolTip(QtGui.QApplication.translate("TileIndex", "Separate multiple attributes with spaces", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditAttribute.setObjectName(_fromUtf8("lineEditAttribute"))
        self.verticalLayout.addWidget(self.lineEditAttribute)
        self.gridLayout.addWidget(self.groupBoxAttribute, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(TileIndex)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)

        self.retranslateUi(TileIndex)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TileIndex.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TileIndex.reject)
        QtCore.QMetaObject.connectSlotsByName(TileIndex)

    def retranslateUi(self, TileIndex):
        pass

