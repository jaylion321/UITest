import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from pyqtgraph.Point import Point
from pyqtgraph import GraphicsLayoutWidget
import numpy as np
import abc
import os
from popAnalysis import ShowTableDialog
from PandaModel import TreeViewModel,CustomNode

class TabItem(abc.ABC):  
    @abc.abstractmethod
    def ret_widget(self):
        return NotImplemented
    

class IdxTreeViewTab(TabItem):

    def __init__(self,stockDict = None,stockInfo = None, Tbl = None):
        self.gridContainer = None
        self.Tbl = Tbl
        self.construct_gridlayout()
        # self.construct_controlPanel()
        self.treeView = QtWidgets.QTreeView()
        self.model = TreeViewModel(['group','code','name'],[])
        
        if stockDict != None:
            for group in stockDict.keys():
                self.model.addChild(CustomNode([group,'','']),None)
                groupIDX = self.model.index(self.model.rowCount(None) -1 ,0)
                for stockItem in stockDict[group].values():
                    #internalPointer to get the origin instance
                    groupIDX.internalPointer().addChild( CustomNode(data=['',stockItem['code'],stockItem['name']]))

        self.treeView.doubleClicked.connect(lambda index: self.DoubleClickFunc(index))
        self.treeView.setModel(self.model)
        # SIGNAL(doubleClicked(const QModelIndex &))
        
        self.gridContainer.layout.addWidget(self.treeView, 0, 0, 1, 1)
        self.gridContainer.setLayout(self.gridContainer.layout)
        self.stockDict = stockDict
        self.stockInfo = stockInfo

    def construct_gridlayout(self):
        self.gridContainer = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(self.gridContainer.sizePolicy().hasHeightForWidth())
        self.gridContainer.setSizePolicy(sizePolicy)
        self.gridContainer.setFocusPolicy(QtCore.Qt.NoFocus)
        self.gridContainer.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.gridContainer.setObjectName("Graphgrid")  
        self.gridContainer.layout = QtWidgets.QGridLayout()
        # self.gridContainer.setStyleSheet("background-color:black;") 

    def construct_controlPanel(self):
        self.maxRadioButton = QtWidgets.QCheckBox("Max")
        self.maxRadioButton.setObjectName("maxRadioButton")
        self.gridContainer.layout.addWidget(self.maxRadioButton, 0, 1, 1, 1)
        self.maxRadioButton.click()
        self.maxRadioButton.setStyleSheet("color: rgb(0, 255, 0);")
        

        self.minRadioButton = QtWidgets.QCheckBox("Min")
        self.minRadioButton.setObjectName("minRadioButton")
        self.gridContainer.layout.addWidget(self.minRadioButton, 1, 1, 1, 1)
        self.minRadioButton.click()
        self.minRadioButton.setStyleSheet("color: rgb(255, 255, 255);")
       

        self.closeRadioButton = QtWidgets.QCheckBox("Close")
        self.closeRadioButton.setObjectName("closeRadioButton")
        self.gridContainer.layout.addWidget(self.closeRadioButton, 2, 1, 1, 1)
        self.closeRadioButton.click()
        self.closeRadioButton.setStyleSheet("color: rgb(255,0,0);")
        

        self.avg10RadioButton = QtWidgets.QCheckBox("10 AVG")
        self.avg10RadioButton.setObjectName("avg10RadioButton")
        self.gridContainer.layout.addWidget(self.avg10RadioButton, 3, 1, 1, 1)
        self.avg10RadioButton.click()
        self.avg10RadioButton.setStyleSheet("color: rgb(255,255,0);")
       

        self.GetButton = QtWidgets.QPushButton("Advance")
        self.GetButton.setObjectName("Advance")
        self.GetButton.setStyleSheet("color: rgb(255, 255, 255);")
        self.gridContainer.layout.addWidget(self.GetButton, 4, 1, 1, 1)
    
    def ret_widget(self):
        return self.gridContainer

    def DoubleClickFunc(self,index):
        row = index.row()
        column = index.column()
        groupName = index.parent().data()
        code = index.parent().child(row,1).data()
        Name = index.parent().child(row,2).data()
        print(groupName , code , Name)
        d = ShowTableDialog(self.Tbl[groupName][code]['performanceTable'],self.Tbl[groupName][code]['revTable'])
        d.exec()




class TableTab(TabItem):

    def __init__(self,Tbl = None,width = 0,height = 0):
        self.Container = None
        self.Tbl = Tbl
        self.construct_container()

        
        self.gridContainer.layout.addWidget(self.treeView, 0, 0, 1, 1)


    def construct_container(self):
        self.gridContainer = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(self.gridContainer.sizePolicy().hasHeightForWidth())
        self.gridContainer.setSizePolicy(sizePolicy)
        self.gridContainer.setFocusPolicy(QtCore.Qt.NoFocus)
        self.gridContainer.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.gridContainer.setObjectName("Graphgrid")  
        self.gridContainer.layout = QtWidgets.QGridLayout()
        # self.gridContainer.setStyleSheet("background-color:black;") 

    def construct_widget(self):
        self.tableView = QtWidgets.QTableView()

    def fitsize(self):
        self.tableView.setFixedWidth(width-100)
        print (width,height)
        self.tableView.resizeColumnsToContents()
    
    def ret_widget(self):
        return self.gridContainer

