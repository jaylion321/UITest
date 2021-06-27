import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from pyqtgraph.Point import Point
from pyqtgraph import GraphicsLayoutWidget
import numpy as np
from popAnalysis import Dialog

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setLabel(text='Time', units=None)

class StockGraph():
    def __init__(self,numofplot = 2, name= None,stockInfo = None):
        self.gridContainer = None
        self.dir = None
        self.construct_gridlayout()
        if numofplot < 0:
            print("numofplot must be greater or equal than 0")
            return -1

        if name != None and len(name) > numofplot:
            print("Pls Checking numofplot")
            return -1
        #X-axis data
        self.dataX = None
        self.dataY = None
        self.name = name
        self.stockInfo = stockInfo
        self.graph = GraphicsLayoutWidget()
        self.graph.setObjectName("stock UI")
        self.label = pg.LabelItem(justify='right')
        self.graph.addItem(self.label)
        self.date_axis = TimeAxisItem(orientation='bottom')
        self.date_axis1 = TimeAxisItem(orientation='bottom')

        self.p1 = self.graph.addPlot(row=1, col=0,axisItems = {'bottom':  self.date_axis1})
        #p1 zoom in/out, move viewbox can auto scaling Y, Important!
        self.p1.vb.sigXRangeChanged.connect(self.setYRange)

        self.p2 = self.graph.addPlot(row=2, col=0,axisItems = {'bottom': self.date_axis})
        #p2 zoom in/out, move viewbox can auto scaling Y. Important!
        self.p2.vb.sigXRangeChanged.connect(self.setYRange)

        # self.p1.showGrid(x=True, y=True, alpha=0.5)  
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this 
        # item when doing auto-range calculations.
        self.p2.addItem(self.region, ignoreBounds=True)


        self.p1.setAutoVisible(y=True)

        #cross hair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.p1.addItem(self.vLine, ignoreBounds=True)
        self.p1.addItem(self.hLine, ignoreBounds=True)

        self.vb = self.p1.vb
        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        #Set PlotDataItem
        self.numofplot = numofplot
        self.name = name
        self.colorStyle = ['r','g','b','y','w','r']
        self.PlotDataItemList = self.setPlot()
        self.p2_plot = self.p2.plot(name='overview')

        #set gridContainer layout
        self.gridContainer.layout.addWidget(self.graph, 0, 0, 10, 1)
        self.gridContainer.setLayout(self.gridContainer.layout)

        self.calName = ['10avg','30avg','90avg']
        self.CalPlotDataItemList = self.setCalPlot()

        #consttuct graph control Panel
        self.construct_controlPanel()
        

    def construct_gridlayout(self):
        self.gridContainer = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(self.gridContainer.sizePolicy().hasHeightForWidth())
        self.gridContainer.setSizePolicy(sizePolicy)
        self.gridContainer.setFocusPolicy(QtCore.Qt.NoFocus)
        self.gridContainer.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.gridContainer.setObjectName("Graphgrid")  
        self.gridContainer.layout = QtWidgets.QGridLayout()
        self.gridContainer.setStyleSheet("background-color:black;") 

    def construct_controlPanel(self):
        self.maxRadioButton = QtWidgets.QCheckBox("Max")
        self.maxRadioButton.setObjectName("maxRadioButton")
        self.gridContainer.layout.addWidget(self.maxRadioButton, 0, 1, 1, 1)
        self.maxRadioButton.click()
        self.maxRadioButton.setStyleSheet("color: rgb(0, 255, 0);")
        self.maxRadioButton.toggled.connect(lambda:self.toggleFunc(self.maxRadioButton,'high'))

        self.minRadioButton = QtWidgets.QCheckBox("Min")
        self.minRadioButton.setObjectName("minRadioButton")
        self.gridContainer.layout.addWidget(self.minRadioButton, 1, 1, 1, 1)
        self.minRadioButton.click()
        self.minRadioButton.setStyleSheet("color: rgb(255, 255, 255);")
        self.minRadioButton.toggled.connect(lambda:self.toggleFunc(self.minRadioButton,'low'))

        self.closeRadioButton = QtWidgets.QCheckBox("Close")
        self.closeRadioButton.setObjectName("closeRadioButton")
        self.gridContainer.layout.addWidget(self.closeRadioButton, 2, 1, 1, 1)
        self.closeRadioButton.click()
        self.closeRadioButton.setStyleSheet("color: rgb(255,0,0);")
        self.closeRadioButton.toggled.connect(lambda:self.toggleFunc(self.closeRadioButton,'close'))    

        self.avg10RadioButton = QtWidgets.QCheckBox("10 AVG")
        self.avg10RadioButton.setObjectName("avg10RadioButton")
        self.gridContainer.layout.addWidget(self.avg10RadioButton, 3, 1, 1, 1)
        self.avg10RadioButton.click()
        self.avg10RadioButton.setStyleSheet("color: rgb(255,255,0);")
        self.avg10RadioButton.toggled.connect(lambda:self.toggleFunc(self.avg10RadioButton,'10avg'))  

        self.GetButton = QtWidgets.QPushButton("Advance")
        self.GetButton.setObjectName("Advance")
        self.GetButton.clicked.connect(self.Analysis)
        self.GetButton.setStyleSheet("color: rgb(255, 255, 255);")
        self.gridContainer.layout.addWidget(self.GetButton, 4, 1, 1, 1)

    def update_p1_tick(self,minX, maxX, interval =60): 
        if self.dataX != None:

            #0 - minX
            lowNum = int(minX/interval)
            #maxX - length
            HighNum = int( (len(self.dataX) -1 - maxX)/interval)

            plotPoint = [(minX - interval*i) for i in range(1,lowNum+1) ]  + [minX] 
            if (maxX - minX) > interval :
                plotPoint.append( int((maxX+minX)/2) )
            plotPoint = plotPoint + [maxX] + [(maxX + interval*i) for i in range(1,HighNum+1) ]

            p1_tick = ['' for i in range(0, len(self.dataX))]
            p1_tick = dict(enumerate(p1_tick))
            for index in plotPoint:
                p1_tick[index] = self.dataX[index]
            
            self.date_axis1.setTicks([list(p1_tick.items())[::1]])

    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0) 
        if (maxX < len(self.dataX) -1):   
            self.update_p1_tick(int(minX)+1 , int(maxX))
               
   
    def updateRegion(self,window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)

    
    def mouseMoved(self,evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple

        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            
            if index > 0 and index < len(self.dataX):
                idx = int(mousePoint.x())
                self.label.setText("<span style='font-size: 12pt'>x=%s,   <span style='color: red'>收盤價=%0.1f</span>,   <span style='color: green'>最高價=%0.1f</span>  <span style='color: white'>最低價=%0.1f</span>" % (self.dataX[idx], self.dataY['close'][idx],  self.dataY['high'][idx],  self.dataY['low'][idx]))
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
    def setYRange(self,plotitem):
        plotitem.enableAutoRange(axis='y')
        plotitem.setAutoVisible(y=True)

    def setPlot(self):
        PlotDataItemList = []
        for i in range(0,self.numofplot):
               PlotDataItemList.append( self.p1.plot(pen=self.colorStyle[i],name=self.name[i]))
        return PlotDataItemList

    def setCalPlot(self):
        CalPlotDataItemList = []
        for i in range(0,3):
               CalPlotDataItemList.append( self.p1.plot(pen=self.colorStyle[i+3],name=self.calName[i]))
        return CalPlotDataItemList

    def setData(self,dataX,dataYDict):
        #create numpy arrays
        #make the numbers large to show that the xrange shows data from 10000 to all the way 0
        self.dataX = dataX
        self.dataY = dataYDict
        ticks=dict(enumerate(dataX))
        

        '''set X-value of P2 and P1'''
        self.date_axis.setTicks([list(ticks.items())[::160], list(ticks.items())[::1]])
        self.date_axis1.setTicks([list(ticks.items())[::160], list(ticks.items())[::1]])
        
        
        '''set Y-value and Plot'''
        for dataY,PlotDataItem in zip( dataYDict.values(),self.PlotDataItemList):
            PlotDataItem.setData(y=dataY)
            
        
        #do not show label
        #self.p1.getAxis('bottom').showLabel(False)

        # self.date_axis.linkToView(self.p1.vb)
        '''set overview data'''
        self.p2_plot.setData(x=list(ticks.keys()), y=dataYDict[self.name[0]], pen="w") 
        #set data view range
        self.p2.vb.setLimits(xMin=0, xMax=len(dataYDict[self.name[0]]))
        self.region.sigRegionChanged.connect(self.update)
        # print (self.p2.vb.viewRange())


        # print (self.p1.vb)
        # self.p1.sigRangeChanged.connect(self.updateRegion)

        self.region.setRegion([0, len(dataYDict[self.name[0]])])

        #calculte Data
        avg10 = self.moving_average(dataYDict[self.name[0]], 10)
        self.CalPlotDataItemList[0].setData(y=avg10)
       

        #make Max and Min are invisiable by default
        self.minRadioButton.setChecked(False)
        self.maxRadioButton.setChecked(False)

    def toggleFunc(self,rdb,name):
        plotItem = None
        for plot in self.PlotDataItemList:
            if plot.name() == name:
                plotItem = plot
        for plot in self.CalPlotDataItemList:
            if plot.name() == name:
                plotItem = plot
        if rdb.isChecked():
            self.p1.addItem(plotItem)
        else:
            self.p1.removeItem(plotItem)

    def setDir(self,dir):
        self.dir = dir

    def Analysis(self):
        d = Dialog(self.dataY, self.dataX, self.dir,self.stockInfo)
        d.exec()

    def ret_GraphicsLayoutWidget(self):
        return self.gridContainer

    @staticmethod
    def removeEvent(self):
        return

    def moving_average(self, data, days):
        result = []
        NanList = [np.nan for i in range(0,days - 1)]
        data = data[:]
        for _ in range(len(data) - days + 1):
            result.append(round(sum(data[-days:]) / days, 2))
            data.pop()
        result = result[::-1]
        return NanList + result