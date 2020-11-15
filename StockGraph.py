import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from pyqtgraph.Point import Point
from pyqtgraph import GraphicsLayoutWidget
import numpy as np

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setLabel(text='Time', units=None)

class StockGraph():
    def __init__(self,numofplot = 2, name= None):

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

        self.data1 = [np.NAN for i in range(0,1200) ] 
        self.data2 = [np.NAN for i in range(0,1200) ] 

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
        self.colorStyle = ['r','g','b']
        self.PlotDataItemList = self.setPlot()

    def update_p1_tick(self,minX, maxX): 
        if self.dataX != None:

            #0 - minX
            lowNum = int(minX/60)
            #maxX - length
            HighNum = int( (len(self.dataX) -1 - maxX)/60)

            plotPoint = [(minX - 60*i) for i in range(1,lowNum+1) ]  + [minX] 
            if (maxX - minX) > 60 :
                plotPoint.append( int((maxX+minX)/2) )
            plotPoint = plotPoint + [maxX] + [(maxX + 60*i) for i in range(1,HighNum+1) ]

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
                self.label.setText("<span style='font-size: 12pt'>x=%s,   <span style='color: red'>收盤價=%0.1f</span>,   <span style='color: green'>最高價=%0.1f</span>  <span style='color: blue'>最低價=%0.1f</span>" % (self.dataX[idx], self.dataY['close'][idx],  self.dataY['high'][idx],  self.dataY['low'][idx]))
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

    def setData(self,dataX,dataYDict):
        #create numpy arrays
        #make the numbers large to show that the xrange shows data from 10000 to all the way 0
        self.dataX = dataX
        self.dataY = dataYDict
        ticks=dict(enumerate(dataX))

        self.date_axis.setTicks([list(ticks.items())[::120], list(ticks.items())[::1]])
        

        for dataY,PlotDataItem in zip( dataYDict.values(),self.PlotDataItemList):
            PlotDataItem.setData(y=dataY)
        
        #do not show label
        #self.p1.getAxis('bottom').showLabel(False)

        # self.date_axis.linkToView(self.p1.vb)
        self.p2.plot(x=list(ticks.keys()), y=dataYDict[self.name[0]], pen="w") 
        #set data view range
        self.p2.vb.setLimits(xMin=0, xMax=len(dataYDict[self.name[0]]))
        self.region.sigRegionChanged.connect(self.update)
        # print (self.p2.vb.viewRange())


        # print (self.p1.vb)
        # self.p1.sigRangeChanged.connect(self.updateRegion)

        self.region.setRegion([100, 200])


    def ret_GraphicsLayoutWidget(self):
        return self.graph



