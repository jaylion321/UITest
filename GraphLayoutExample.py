import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from pyqtgraph.Point import Point
from pyqtgraph import GraphicsLayoutWidget
import numpy as np

class Graphexample():
    def __init__(self):
        self.graph = GraphicsLayoutWidget()
        self.graph.setObjectName("stock UI")
        self.label = pg.LabelItem(justify='right')
        self.graph.addItem(self.label)
        self.p1 = self.graph.addPlot(row=1, col=0)
        self.p2 = self.graph.addPlot(row=2, col=0)
        self.p1.showGrid(x=True, y=True, alpha=0.5)  
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this 
        # item when doing auto-range calculations.
        self.p2.addItem(self.region, ignoreBounds=True)

        #pg.dbg()
        self.p1.setAutoVisible(y=True)


        #create numpy arrays
        #make the numbers large to show that the xrange shows data from 10000 to all the way 0
        self.data1 = 10000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)
        self.data2 = 15000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)

        self.p1.plot(self.data1, pen="r")
        self.p1.plot(self.data2, pen="g")

        self.p2.plot(self.data1, pen="w")
        self.region.sigRegionChanged.connect(self.update)
        self.p1.sigRangeChanged.connect(self.updateRegion)

        self.region.setRegion([1000, 2000])

        #cross hair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.p1.addItem(self.vLine, ignoreBounds=True)
        self.p1.addItem(self.hLine, ignoreBounds=True)

        self.vb = self.p1.vb
        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)    

   

    def updateRegion(self,window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)

    
    def mouseMoved(self,evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if index > 0 and index < len(self.data1):
                self.label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), self.data1[index], self.data2[index]))
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def ret_GraphicsLayoutWidget(self):
        return self.graph



