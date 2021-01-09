# -*- coding: utf-8 -*-
# https://stackoverflow.com/questions/4553304/understanding-form-layout-mechanisms-in-qt
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
 
from ProxyUI import ProxyPanel,BasicPanel
from twstock.listctl import StockList
from twstock import Stock
from StockGraph import StockGraph

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        # self.ui = Ui_MainWindow()
        self.setupUi(self)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1103, 509)

        # Create StockGraph and _stockList object
        self.shadowList = []
        self.usedList = []
        for i in range(0,10):
            stockGraph = StockGraph(numofplot = 3, name= ["close","high","low"])
            self.shadowList.append(stockGraph)
        self._stockList = StockList(self.shadowList, self.usedList)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMaximumSize(QtCore.QSize(1800, 700))
        self.centralwidget.setObjectName("centralwidget")

        self.mainBox = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainBox.setObjectName("mainBox")

        self.Container = QtWidgets.QHBoxLayout()
        self.Container.setObjectName("Container")

        '''Create Tab widget and settig'''
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.tabRemove)
        # self.tabWidget.tabCloseRequested.connect(lambda index: self.tabWidget.removeTab(index))


        #We fix the width of QToolBox, so that the width of Tabwidget will be not expanded when windows is enlarged
        self.Setting = QtWidgets.QToolBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setHeightForWidth(self.Setting.sizePolicy().hasHeightForWidth())
        self.Setting.setSizePolicy(sizePolicy)
        # self.Setting.setMinimumSize(QtCore.QSize(300, 520))
        self.Setting.setObjectName("Setting")

        self.ProxyPanel = ProxyPanel()
        self.Setting.addItem(self.ProxyPanel.ret_widget(), "Proxy")
        
        self.BasicPanel = BasicPanel(self.tabWidget)
        self.Setting.addItem(self.BasicPanel.ret_widget(), "Basic")
        self.BasicPanel.append_graphList(self._stockList)


        # #first Tab
        # self.stockTab1 = QtWidgets.QWidget()
        # self.stockTab1.setObjectName("stockTab1")
        # self.tabWidget.addTab(self.stockTab1, "")

        # #set Tab layout
        # self.stockTab1.layout = QtWidgets.QHBoxLayout()
        # self.StockGraph = StockGraph(numofplot = 3, name= ["close","high","low"])
        # #Create a graph widget
        # self.stockTab1.layout.addWidget(self.StockGraph.ret_GraphicsLayoutWidget())
        # self.stockTab1.setLayout(self.stockTab1.layout)


        # #second Tab
        # self.stockTab2 = QtWidgets.QWidget()
        # self.stockTab2.setObjectName("tab_4")
        # #set Tab layout
        # self.stockTab2.layout = QtWidgets.QHBoxLayout()
        # self.Graph = Graphexample()

        # #layout add to TAB2
        # self.stockTab2.layout.addWidget(self.Graph.ret_GraphicsLayoutWidget())
        # self.stockTab2.setLayout(self.stockTab2.layout)


        # self.tabWidget.addTab(self.stockTab2, "")
        self.Container.addWidget(self.tabWidget)
        self.Container.addWidget(self.Setting)
        self.mainBox.addLayout(self.Container)
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

    def setStockInfo(self, stockInfo, dir):
        self.stockInfo = stockInfo
        self.dir = dir
        self.ProxyPanel.setStockInfo( self.stockInfo, self.dir)
        self.BasicPanel.setStockInfo( self.stockInfo, self.dir)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.stockTab1), _translate("MainWindow", "Tab 1"))
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.stockTab2), _translate("MainWindow", "Tab 2"))
        # self.Setting.setItemText(self.Setting.indexOf(self.Proxy), _translate("MainWindow", "Proxy"))
        # self.pushButton.setText(_translate("MainWindow", "Test"))
        # self.Setting.setItemText(self.Setting.indexOf(self.Proxy), _translate("MainWindow", "Proxy"))
        # self.To.setText(_translate("MainWindow", "To"))
        # self.From.setText(_translate("MainWindow", "From"))
        # self.Setting.setItemText(self.Setting.indexOf(self.Basic), _translate("MainWindow", "Basic"))

    def tabRemove(self,index):
        print ("Close tab, index = %s" % index)
        self.tabWidget.removeTab(index)
        stockgraph = self._stockList.remove(index)
        
        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
