# -*- coding: utf-8 -*- copy from the version used by Nico, Will and Floor in LD400 

# Form implementation generated from reading ui file 'param_viewer_GUI_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tab_menu = QtWidgets.QTabWidget(self.centralwidget)
        self.tab_menu.setObjectName("tab_menu")
        self.realgates = QtWidgets.QWidget()
        self.realgates.setObjectName("realgates")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.realgates)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.scrollArea = QtWidgets.QScrollArea(self.realgates)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 756, 470))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.layout_real = QtWidgets.QGridLayout()
        self.layout_real.setObjectName("layout_real")
        self.gridLayout_6.addLayout(self.layout_real, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_7.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.tab_menu.addTab(self.realgates, "")
        self.virtualgates = QtWidgets.QWidget()
        self.virtualgates.setObjectName("virtualgates")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.virtualgates)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.layout_virtual = QtWidgets.QGridLayout()
        self.layout_virtual.setObjectName("layout_virtual")
        self.gridLayout_5.addLayout(self.layout_virtual, 0, 0, 1, 1)
        self.tab_menu.addTab(self.virtualgates, "")
        self.RFsettings = QtWidgets.QWidget()
        self.RFsettings.setObjectName("RFsettings")
        self.layoutWidget = QtWidgets.QWidget(self.RFsettings)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 761, 501))
        self.layoutWidget.setObjectName("layoutWidget")
        self.layout_RF = QtWidgets.QGridLayout(self.layoutWidget)
        self.layout_RF.setContentsMargins(0, 0, 0, 0)
        self.layout_RF.setObjectName("layout_RF")
        self.tab_menu.addTab(self.RFsettings, "")
        self.settings = QtWidgets.QWidget()
        self.settings.setObjectName("settings")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.settings)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.step_size = QtWidgets.QDoubleSpinBox(self.settings)
        self.step_size.setMinimumSize(QtCore.QSize(80, 0))
        self.step_size.setMaximum(100.0)
        self.step_size.setProperty("value", 1.0)
        self.step_size.setObjectName("step_size")
        self.gridLayout_2.addWidget(self.step_size, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.settings)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(120, 0))
        self.label.setBaseSize(QtCore.QSize(0, 0))
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.settings)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 1, 2, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.tab_menu.addTab(self.settings, "")
        self.gridLayout.addWidget(self.tab_menu, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lock = QtWidgets.QCheckBox(self.centralwidget)
        self.lock.setObjectName("lock")
        self.horizontalLayout_2.addWidget(self.lock)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tab_menu.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tab_menu.setTabText(self.tab_menu.indexOf(self.realgates), _translate("MainWindow", "Normal gates"))
        self.tab_menu.setTabText(self.tab_menu.indexOf(self.virtualgates), _translate("MainWindow", "Virtual Gates"))
        self.tab_menu.setTabText(self.tab_menu.indexOf(self.RFsettings), _translate("MainWindow", "RF Settings"))
        self.label.setText(_translate("MainWindow", "Voltage step"))
        self.label_2.setText(_translate("MainWindow", "mV"))
        self.tab_menu.setTabText(self.tab_menu.indexOf(self.settings), _translate("MainWindow", "Settings"))
        self.lock.setText(_translate("MainWindow", "Lock parameter viewer"))

