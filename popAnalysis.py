import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets 
from pyqtgraph import GraphicsLayoutWidget
import numpy as np
import functionAnalysis
import PandaModel
from Parser.parser import Concat_Table_With_IDX

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setLabel(text='Time', units=None)

class Dialog(QtGui.QDialog):

    def __init__(self,dataY=None,dataX=None,dir=None,stockInfo=None,parent=None):
        super(Dialog, self).__init__(parent)
        self.resize(800,800)
        self.gridContainer = None
        self.gridContainer = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(self.gridContainer.sizePolicy().hasHeightForWidth())
        self.gridContainer.setSizePolicy(sizePolicy)
        self.gridContainer.setFocusPolicy(QtCore.Qt.NoFocus)
        self.gridContainer.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.gridContainer.setObjectName("Graphgrid")  
        self.gridContainer.layout = QtWidgets.QGridLayout()
        self.dir = dir
        self.stockInfo = stockInfo


        self.dataX = dataX
        self.dataY = dataY
        self.rasingRange= []
        self.failingRange = []

        # setup Plot
        self.graph = None
        self.PlotDataItemList = None
        self.PlotLocalMaximaData = None
        self.PlotLocalMinimaData = None
        self.p1 = None
        self.colorStyle = ['r','g','y','b','w','o']
        self.setupGraph()
        self.gridContainer.layout.addWidget(self.graph, 0, 0, 10, 10)

        self.TableDAT = Concat_Table_With_IDX(self.dir,self.stockInfo.code)
        self.initUI()
        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        

    def initUI(self):


        #check box
        self.AVGRadioButton = QtWidgets.QCheckBox("AVG")
        self.AVGRadioButton.setObjectName("avgRadioButton")
        self.gridContainer.layout.addWidget(self.AVGRadioButton, 0, 11, 1, 1)
        self.AVGRadioButton.setStyleSheet("color: rgb(0, 255, 0);")
        self.AVGRadioButton.toggled.connect(lambda:self.toggleFunc(self.AVGRadioButton,'avg'))       
        self.AVGRadioButton.click()

        self.LPFRadioButton = QtWidgets.QCheckBox("LPF")
        self.LPFRadioButton.setObjectName("avgRadioButton")
        self.gridContainer.layout.addWidget(self.LPFRadioButton, 1, 11, 1, 1)
        self.LPFRadioButton.setStyleSheet("color: rgb(255,0,0);")
        self.LPFRadioButton.toggled.connect(lambda:self.toggleFunc(self.LPFRadioButton,'lpf'))  
        self.LPFRadioButton.click()

        #set Data
        self.PlotDataItemList = self.setPlot()
        self.setData(self.dataX,self.dataY)

        #set avg slide
        self.avgSld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.avgSld.setRange(5, 120)
        self.avgSld.setFocusPolicy(QtCore.Qt.NoFocus)
        # it seems not work
        #self.avgSld.setPageStep(5)
        # self.avgSld.setTickInterval(5)
        # self.avgSld.setSingleStep(5)
        self.avgSld.valueChanged.connect(self.updateAvg)
        self.gridContainer.layout.addWidget(self.avgSld, 11, 1, 1, 2)
        self.avg = functionAnalysis.moving_average(self.dataY['close'], self.avgSld.value())     

        self.AvgEdit = QtWidgets.QLabel('5日線')
        self.AvgEdit.setObjectName("avg")
        self.gridContainer.layout.addWidget(self.AvgEdit, 11, 0, 1, 1)


        self.OrderLabel = QtWidgets.QLabel('Order')
        self.OrderLabel.setObjectName("orderLabel")
        self.gridContainer.layout.addWidget(self.OrderLabel, 12, 0, 1, 1)

        self.OrderEdit = QtWidgets.QLineEdit("2")
        self.OrderEdit.setObjectName("orderEdit")
        self.gridContainer.layout.addWidget(self.OrderEdit, 12, 1, 1, 1)

        self.CutoffEdit = QtWidgets.QLabel("Cutoff ： 2")
        self.CutoffEdit.setObjectName("Cutoff")
        self.gridContainer.layout.addWidget(self.CutoffEdit, 12, 3, 1, 1)

        self.cutoffSld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.cutoffSld.setRange(2,60)
        
        self.cutoffSld.setFocusPolicy(QtCore.Qt.NoFocus)
        self.smoothData = functionAnalysis.butterworth_filter(self.dataY['close'], self.cutoffSld.value(), len(self.dataY['close'])/2 ,2)   
        self.cutoffSld.valueChanged.connect(self.updateLPF)
        self.cutoffSld.setValue(5)

        self.gridContainer.layout.addWidget(self.cutoffSld, 12, 4, 1, 10)
        

        self.PlotDataItemList[1].setData(y=self.avg)
        self.PlotDataItemList[2].setData(y=self.smoothData)

        self.gridContainer.setLayout(self.gridContainer.layout)

        #make AVG is invisiable by default
        self.AVGRadioButton.setChecked(False)
        
        self.tableView = QtWidgets.QTableView()
        

        self.TableDAT = self.TableDAT.round(2)
        #Temporary, we delete 1st level colums, for showing columns in TableView 
        self.TableDAT.columns = self.TableDAT.columns.droplevel(0)
        print(self.TableDAT)
        self.model = PandaModel.DataFrameModel(self.TableDAT)
        self.tableView.setModel(self.model)

        #Resize cell size to 
        self.tableView.resizeColumnsToContents()
        self.gridContainer.layout.addWidget(self.tableView, 13, 0, 1, 10)
            

    def setupGraph(self):
        self.date_axis = TimeAxisItem(orientation='bottom')
        self.graph = GraphicsLayoutWidget()
        self.graph.setObjectName("Graph UI")
        self.date_axis = TimeAxisItem(orientation='bottom')
        self.label = pg.LabelItem(justify='right')
        self.graph.addItem(self.label)
        
        self.p1 = self.graph.addPlot(row=1, col=0,axisItems = {'bottom':  self.date_axis})
        #p1 zoom in/out, move viewbox can auto scaling Y, Important!
        self.p1.vb.sigXRangeChanged.connect(self.setYRange)
        
        self.PlotDataItemList = self.setPlot()
        self.PlotLocalMaximaData = pg.ScatterPlotItem(pen='r', brush='b',symbol='d', pxMode=True, size=10)
        self.PlotLocalMinimaData = pg.ScatterPlotItem(pen='g', brush='b',symbol='t', pxMode=True, size=10)
        # self.p1.addItem(self.PlotLocalMaximaData)
        # self.p1.addItem(self.PlotLocalMinimaData)
                               


    # def showEvent(self, event):
    # 	geom = self.frameGeometry()
    # 	geom.moveCenter(QtGui.QCursor.pos())
    # 	self.setGeometry(geom)
    # 	super(Dialog, self).showEvent(event)

    def setPlot(self):
        PlotDataItemList = []
        self.name = ['close','avg','lpf']
        for i in range(0, 3):
               PlotDataItemList.append( self.p1.plot(pen=self.colorStyle[i], name=self.name[i] ))
        return PlotDataItemList

    def setYRange(self,plotitem):
        plotitem.enableAutoRange(axis='y')
        plotitem.setAutoVisible(y=True)

    def setData(self,dataX,dataY):
        ticks=dict(enumerate(dataX))
        '''set X-value'''
        self.date_axis.setTicks([list(ticks.items())[::120], list(ticks.items())[::1]])
        self.PlotDataItemList[0].setData(y=dataY['close'])

    def updateAvg(self, value):
        self.AvgEdit.setText(str(value) +'日線')
        self.avg = functionAnalysis.moving_average(self.dataY['close'], self.avgSld.value())            
        self.PlotDataItemList[1].setData(y=self.avg)

    def updateLPF(self, value):
        self.CutoffEdit.setText("Cutoff ： " + str(value))
        self.smoothData = functionAnalysis.butterworth_filter(self.dataY['close'], self.cutoffSld.value(), len(self.dataY['close'])/2 , int(self.OrderEdit.text()))               
        self.PlotDataItemList[2].setData(y=self.smoothData)
        maxidx, minidx = functionAnalysis.getlocalMaxMin(self.smoothData,True,True)
        
        #Split Range
        sortRange = []
        lastRoundIdx  = 0
        for idxMax,idxMin in zip(maxidx,minidx):
            if idxMax > idxMin:
                sortRange.append([lastRoundIdx, idxMin])  
                sortRange.append([idxMin, idxMax])  
                lastRoundIdx = idxMax
            else:
                sortRange.append([lastRoundIdx, idxMax])
                sortRange.append([idxMax, idxMin])  
                lastRoundIdx = idxMin
        sortRange.append([maxidx[-1], -1]) if maxidx[-1] > minidx[-1] else sortRange.append([minidx[-1], -1])

        self.PlotLocalMaximaData.setData(x=maxidx,y=[self.dataY['close'][i] for i in  maxidx] )
        self.PlotLocalMinimaData.setData(x=minidx,y=[self.dataY['close'][i] for i in  minidx] )



    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()
            event.accept()
        else:
            super(Dialog, self).keyPressEvent(event)

    def toggleFunc(self,rdb,name):
        plotItem = None
        for plot in self.PlotDataItemList:
            if plot.name() == name:
                plotItem = plot
        if rdb.isChecked():
            self.p1.addItem(plotItem)
        else:
            self.p1.removeItem(plotItem)

    def mouseMoved(self,evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple

        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.p1.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            
            if index > 0 and index < len(self.dataX):
                idx = int(mousePoint.x())
                self.label.setText("<span style='font-size: 12pt'>x=%s,   <span style='color: red'>收盤價=%0.1f</span>" % (self.dataX[idx], self.dataY['close'][idx]))

    # def moving_average(self, data, days):
    #     result = []
    #     NanList = [np.nan for i in range(0,days - 1)]
    #     data = data[:]
    #     for _ in range(len(data) - days + 1):
    #         result.append(round(sum(data[-days:]) / days, 2))
    #         data.pop()
    #     result = result[::-1]
    #     return NanList + result