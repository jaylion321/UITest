# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\Stock.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from pyqtgraph.Point import Point
from pyqtgraph import GraphicsLayoutWidget
import numpy as np
import sys
from GraphLayoutExample import Graphexample
from StockGraph import StockGraph

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        # self.ui = Ui_MainWindow()
        self.setupUi(self)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1103, 509)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMaximumSize(QtCore.QSize(1400, 521))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_2.sizePolicy().hasHeightForWidth())
        self.checkBox_2.setSizePolicy(sizePolicy)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout_3.addWidget(self.checkBox_2)
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_3.sizePolicy().hasHeightForWidth())
        self.checkBox_3.setSizePolicy(sizePolicy)
        self.checkBox_3.setObjectName("checkBox_3")
        self.verticalLayout_3.addWidget(self.checkBox_3)
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox.sizePolicy().hasHeightForWidth())
        self.checkBox.setSizePolicy(sizePolicy)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_3.addWidget(self.checkBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        #first Tab
        self.stockTab1 = QtWidgets.QWidget()
        self.stockTab1.setObjectName("stockTab1")
        self.tabWidget.addTab(self.stockTab1, "")

        #set Tab layout
        self.stockTab1.layout = QtWidgets.QHBoxLayout()
        self.StockGraph = StockGraph(numofplot = 2, name= ["close","high"])
        #Create a graph widget
        self.stockTab1.layout.addWidget(self.StockGraph.ret_GraphicsLayoutWidget())
        self.stockTab1.setLayout(self.stockTab1.layout)


        #second Tab
        self.stockTab2 = QtWidgets.QWidget()
        self.stockTab2.setObjectName("tab_4")
        #set Tab layout
        self.stockTab2.layout = QtWidgets.QHBoxLayout()
        self.Graph = Graphexample()

        #layout add to TAB2
        self.stockTab2.layout.addWidget(self.Graph.ret_GraphicsLayoutWidget())
        self.stockTab2.setLayout(self.stockTab2.layout)


        self.tabWidget.addTab(self.stockTab2, "")
        self.horizontalLayout_4.addWidget(self.tabWidget)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def addGraphPlot(self):
        graph = GraphicsLayoutWidget(self.stockTab2)
        graph.setObjectName("stock UI")
        p1 = graph.addPlot(row=1, col=0)
        p2 = graph.addPlot(row=2, col=0)
        p1.showGrid(x=True, y=True, alpha=0.5)     
        return graph   

    def SetGraphData(self,dataXList,dataYList):
        self.StockGraph.setData(dataXList,dataYList )


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.checkBox_2.setText(_translate("MainWindow", "CheckBox"))
        self.checkBox_3.setText(_translate("MainWindow", "CheckBox"))
        self.checkBox.setText(_translate("MainWindow", "CheckBox"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.stockTab1), _translate("MainWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.stockTab2), _translate("MainWindow", "Tab 2"))



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
