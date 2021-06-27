import os
import pyqtgraph as pg
import pandas as pd 
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets 
from functools import partial


class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        # print(type(self._dataframe[col]),col)
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles


class CustomNode(object):
    def __init__(self, data):
        self._data = data
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, '__getitem__'):
            self._data = [data]

        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0

    def data(self, column):
        if column >= 0 and column < len(self._data):
            return self._data[column]

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self._columncount = max(child.columnCount(), self._columncount)


class  TreeViewModel(QtCore.QAbstractItemModel):
    def __init__(self, header : list, nodes : list):
        QtCore.QAbstractItemModel.__init__(self)
        self._root = CustomNode(None)
        for node in nodes:
            self._root.addChild(node)
        self.header = header

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable 

    def rowCount(self, index):
        if index != None and index.isValid() :
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent):   
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        # if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
        #     return QtCore.QModelIndex()

        child = parent.child(row)
        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.data(index.column())
        return None



    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if self.header != None:
                    return self.header[section]
            else:
                # return str(self._dataframe.index[section])
                return QtCore.QVariant()
        return QtCore.QVariant()


class TableWidget():
    def __init__(self,width,height,Tbl=None):    
        self.Tbl = Tbl
        self.width = width
        self.height = height
        self.container = None
        self.container = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(self.container.sizePolicy().hasHeightForWidth())
        self.container.setSizePolicy(sizePolicy)
        self.container.setFocusPolicy(QtCore.Qt.NoFocus)
        self.container.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.container.setObjectName("Proxy")  
        self.container.layout = QtWidgets.QHBoxLayout()

        self.tableView = QtWidgets.QTableView()

        self.construct_widget()


    def construct_widget(self):      
        self.model = DataFrameModel(self.Tbl)
        self.tableView.setModel(self.model)
        self.fitsize()
        self.container.layout.addWidget(self.tableView)
        self.container.setLayout(self.container.layout)
        return


    def fitsize(self):
        self.tableView.setFixedWidth(self.width-100)
        print (self.width,self.height)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        return
        

    def ret_widget(self):
        return self.container
