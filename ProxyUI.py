import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets 
from pyqtgraph.Point import Point
from pyqtgraph import GraphicsLayoutWidget
import numpy as np
import abc
from twstock import Stock, proxy
import multiprocessing as mp 
from multiprocessing import Lock
import re
import aiohttp
import asyncio
import pandas as pd 
from StockGraph import StockGraph


class CustomerText(QtWidgets.QPlainTextEdit):
    processUpdateSIG = QtCore.pyqtSignal(str,str)
    def __init__(self):
        super().__init__()   
        self.processUpdateSIG.connect(self.processUpdate)

    @QtCore.pyqtSlot(str,str)
    def processUpdate(self, stockNo, date):
        self.setPlainText(self.toPlainText() + 'Stock NO :'+ stockNo + ' date : ' +date + '\r\n')



class ToolItem(abc.ABC):  
    @abc.abstractmethod
    def ret_widget(self):
        return NotImplemented

    @abc.abstractmethod
    def setStockInfo(self, stockInfo, dir):
        return


class ProxyPanel(ToolItem):
    def __init__(self,dir=None,stockInfo=None,callback=None):    
        self.ProxyWidget = None
        self.ProxyWidget = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(self.ProxyWidget.sizePolicy().hasHeightForWidth())
        self.ProxyWidget.setSizePolicy(sizePolicy)
        self.ProxyWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ProxyWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.ProxyWidget.setObjectName("Proxy")  
        self.button_calllback = None
        self.construct_widget()
        self.callback = callback
        self.getResult = None
        self.dir = dir
        self.stockInfo = stockInfo
        sema = mp.Semaphore(1)
        self.pool = mp.Pool(initializer = init_child,initargs=(sema,))

    def construct_widget(self):      
        # Method 1 : Widget in the ProxygridLayoutWidget will not autoresize
        # self.ProxyWidget.layout = QtWidgets.QGridLayout() 
        # self.ProxygridLayoutWidget = QtWidgets.QWidget(self.ProxyWidget)
        # self.ProxygridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 301, 441))
        # self.ProxygridLayoutWidget.setObjectName("ProxygridLayoutWidget")
        # self.ProxygridLayout = QtWidgets.QGridLayout(self.ProxygridLayoutWidget)  
        # self.ProxygridLayout.setContentsMargins(0, 0, 0, 0)
        # self.ProxygridLayout.setObjectName("ProxygridLayout")
        # self.ProxyList =QtWidgets.QPlainTextEdit(self.ProxygridLayoutWidget)
        # self.ProxyList.setObjectName("ProxyList")
        # self.ProxygridLayout.addWidget(self.ProxyList, 4, 0, 1, 1)
        # self.ProxyValidList = QtWidgets.QPlainTextEdit(self.ProxygridLayoutWidget)
        # self.ProxyValidList.setObjectName("plainTextEdit")
        # self.ProxygridLayout.addWidget(self.ProxyValidList, 2, 0, 1, 1)
        # self.pushButton = QtWidgets.QPushButton(self.ProxygridLayoutWidget)
        # self.pushButton.setObjectName("pushButton")
        # self.ProxygridLayout.addWidget(self.pushButton, 3, 0, 1, 1)
        # self.Setting.addItem(self.Proxy, "")

        # Method 2 : Widget in the GridLayout will autoresize
        self.ProxyWidget.layout = QtWidgets.QGridLayout()  
        self.fileName = QtWidgets.QLineEdit()
        self.fileName.setObjectName("lineEdit")
        self.ProxyWidget.layout.addWidget(self.fileName, 0, 1, 1, 1)
        self.fileButton = QtWidgets.QPushButton()
        self.fileButton.setObjectName("fileButton")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./QTDesignerUI/file.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fileButton.setIcon(icon)
        self.fileButton.clicked.connect(self.file_selection)
        self.ProxyWidget.layout.addWidget(self.fileButton, 0, 0, 1, 1)

        self.ProxyList =QtWidgets.QPlainTextEdit()
        self.ProxyList.setObjectName("ProxyList")
        self.ProxyWidget.layout.addWidget(self.ProxyList, 2, 0, 1, 2)


        self.StartTime = QtWidgets.QDateEdit(calendarPopup=True)
        self.StartTime.setObjectName("StartTime")
        self.StartTime.setDateTime(QtCore.QDateTime.currentDateTime().addYears(-3))
        self.ProxyWidget.layout.addWidget(self.StartTime, 3, 0, 1, 1)

        self.EndTime = QtWidgets.QDateEdit(calendarPopup=True)
        self.EndTime.setObjectName("EndTime")
        self.EndTime.setDateTime(QtCore.QDateTime.currentDateTime())
        self.ProxyWidget.layout.addWidget(self.EndTime, 3, 1, 1, 2)

        self.stockNoEdit = QtWidgets.QLineEdit()
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.StarttimeEdit.sizePolicy().hasHeightForWidth())
        # self.StarttimeEdit.setSizePolicy(sizePolicy)
        self.stockNoEdit.setObjectName("stockNoEdit")
        self.ProxyWidget.layout.addWidget(self.stockNoEdit,  4, 0, 1, 1)

        self.GetButton = QtWidgets.QPushButton("Get")
        self.GetButton.setObjectName("pushButton")
        self.ProxyWidget.layout.addWidget(self.GetButton, 4, 1, 1, 2)
        self.GetButton.clicked.connect(self.download)
        

        self.result = CustomerText()
        self.result.setObjectName("plainTextEdit")
        self.ProxyWidget.layout.addWidget(self.result, 5, 0, 1, 2)

        self.ProxyWidget.setLayout(self.ProxyWidget.layout)


    def setStockInfo(self, stockInfo, dir):
        self.stockInfo = stockInfo
        self.dir = dir

    def file_selection(self):
        files = QtWidgets.QFileDialog.getOpenFileNames(None,
        "多檔案選擇",
        "./",
        "All Files (*);;Text Files (*.txt)")
        try:
            self.ProxyList.setPlainText('')
            self.fileName.setText(files[0][0])
            lines = ''
            with open(files[0][0], 'r') as fp:
                line = fp.readline()
                while line:                
                   lines += line  
                   line = fp.readline()
            self.ProxyList.setPlainText(lines)     

        except Exception as e:
           self.ProxyList.setPlainText(str(e))
    
    def download(self): 
        self.result.setPlainText("Start from: " + str(self.StartTime.date().toPyDate())
         + " End to: "+  str(self.EndTime.date().toPyDate()) + '\r\n')
        # print(self.result.getPaintContext())
        stockNo = self.stockNoEdit.text()

        stockItem = None
        for key in self.stockInfo.keys(): 
            for item in self.stockInfo[key]:
                if (item.code == stockNo):
                    stockItem = item
                    print(stockItem)
                    self.dir = "./"+stockItem.group+"/"+stockItem.code+"_"+stockItem.name+ "/"

        if (stockItem == None):
            print("The stock is not exist!")
            return
            

        if re.match(r'^([\d]+)$', stockNo) != None:
            # try:
            proxyProvider = None
            proxy_req_num=3
            stock = Stock(stockNo,False) 
            Text =  self.ProxyList.toPlainText().split()
            # print(self.ProxyList.toPlainText().split())
            proxy_list = []

        #     '''judge if input is an valid ip'''
        for i,proxyip in enumerate(Text):
            regx_ip = re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$',proxyip)
            if( re.split  != None and [0<=int(x)<256 for x in re.split('[\.]',re.split(':', regx_ip.group(0))[0]) ].count(True)==4 ):
                proxy_list.append(proxyip)

        proxy_req_num = (len(proxy_list))

        ''' Get data '''
        if (proxy_req_num !=0):
            ''' with proxy'''
            proxyProvider = proxy.RoundRobinProxiesProvider(proxy_list)
            if (proxy_req_num > 3):
                proxy_req_num = 3
            
            
            self.pool.apply_async(async_task, args=(stock,2020,8,proxyProvider,proxy_req_num),callback=self.async_finsh) 
            # 
            # tasks = asyncio.run( stock.async_fetch_from(2020, 3,proxyProvider,proxy_req_num))
        else:
            ''' without proxy'''
            
            i = 0
            while 1:
                date = self.StartTime.date().addMonths(i)
                year = date.year()
                month = date.month()
                self.pool.apply_async(sync_task, args=(stock,year,month,True,),callback=self.finish) 
                if (self.EndTime.date().year() ==  year and self.EndTime.date().month() == month) :
                    break
                i += 1
    

    def finish(self,result):
        fetch_data = result
        print("Creating file")
        self.result.processUpdateSIG.emit(fetch_data['stkno'] ,str(fetch_data['date']))
        if (self.dir != None):
            DF = pd.DataFrame(fetch_data['data'],columns=fetch_data['fields'])
            DF.to_csv(self.dir + fetch_data['stkno']+'_price_'+str(fetch_data['date'])+'.csv', encoding='utf_8_sig')


    def async_finsh(self,result):
        print("done")

    
    def ret_widget(self):
        return self.ProxyWidget

def async_task(stock,year,month,proxyProvider,proxy_req_num):
    tasks = asyncio.run( stock.async_fetch_from(year, month,proxyProvider,proxy_req_num))

def sync_task(stock,year,month,json_format):
    with sema:
        print("Get sema")
        result = stock.fetch(year,month,json_format)
        return result
    
def init_child(_sema):
    global sema 
    sema = _sema

class BasicPanel(ToolItem):
    def __init__(self,container=None,filedir=None,stockInfo=None):    
        self.BasicWidget = None
        self.BasicWidget = QtWidgets.QWidget()
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHeightForWidth(self.BasicWidget.sizePolicy().hasHeightForWidth())
        # self.BasicWidget.setSizePolicy(sizePolicy)
        # self.BasicWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.BasicWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.BasicWidget.setObjectName("Basic")  
        self.Tabcontainer = container
        self.dir = filedir
        self.construct_widget()
        self.stockInfo = stockInfo
        self._stockList = None
        self.stockGraph = None

    def construct_widget(self):      
        self.BasicWidget.layout = QtWidgets.QGridLayout()

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.BasicWidget.layout.addItem(spacerItem, 3, 2, 1, 1)

        self.StockNoEdit = QtWidgets.QLineEdit()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StockNoEdit.sizePolicy().hasHeightForWidth())
        self.StockNoEdit.setSizePolicy(sizePolicy)
        self.StockNoEdit.setObjectName("StarttimeEdit")
        self.BasicWidget.layout.addWidget(self.StockNoEdit, 0, 0, 1, 1)

        self.StartTime = QtWidgets.QDateEdit(calendarPopup=True)
        self.StartTime.setObjectName("StartTime")
        self.StartTime.setDateTime(QtCore.QDateTime.currentDateTime().addYears(-3))
        self.BasicWidget.layout.addWidget(self.StartTime, 0, 1, 1, 1)

        self.fileButton = QtWidgets.QPushButton("Get")
        self.fileButton.setObjectName("fileButton")
        self.BasicWidget.layout.addWidget(self.fileButton, 0, 2, 1, 1)
        self.fileButton.clicked.connect(self.click_read_history)

        self.BasicWidget.setLayout(self.BasicWidget.layout)

    def setStockInfo(self, stockInfo, dir):
        self.stockInfo = stockInfo
        self.dir = dir


    @staticmethod
    def set_click_event(self):
        print("ok")
        # self.minCheckbox.stateChanged.connect(self.state_changed)
    
    @staticmethod
    def state_changed():
        print("xx")


    def click_read_history(self):
        stockTab1 = QtWidgets.QWidget()
        stockTab1.setObjectName("stockTab1")
        

        stockNo = self.StockNoEdit.text()
        
        ''' check input and get relative dir'''
        stockItem = None
        for key in self.stockInfo.keys(): 
            for item in self.stockInfo[key]:
                if (item.code == stockNo):
                    stockItem = item
                    print(stockItem)
                    self.dir = "./"+stockItem.group+"/"+stockItem.code+"_"+stockItem.name+ "/"

        if (stockItem == None):
            print("The stock is not exist!")
            return

        '''1. Get files from Dir 
           2. Collect all data as a big dataFram by Panda'''
        file_list = []
        for file in os.listdir(self.dir):
            if 'price' in file:
                file_list.append( pd.read_csv(self.dir + file))
        

        '''Data processing '''
        df_price = pd.concat(file_list,axis=0)
        graphYdict = {}
        graphYdict['close'] = df_price['收盤價'].values.tolist()
        graphYdict['high'] = df_price['最高價'].values.tolist()
        graphYdict['low'] = df_price['最低價'].values.tolist()

        graphXdata = []
        for date in df_price['日期'].values.tolist():
            date = date.split('/',1)
            ''' To Common Era'''
            graphXdata.append( str(int(date[0])+1911)+'/'+date[1])


        '''Put data to TAB '''
        # Set layout
        stockTab1.layout = QtWidgets.QHBoxLayout()

        #Get a graph widget
        self.stockGraph = self._stockList.create()
        if self.stockGraph == None:
            return
        self.stockGraph.stockInfo = stockItem
        self.stockGraph.setDir("./"+stockItem.group+"/")
        stockTab1.layout.addWidget(self.stockGraph.ret_GraphicsLayoutWidget())
        stockTab1.setLayout(stockTab1.layout) 
        self.stockGraph.setData(graphXdata, graphYdict)

        '''add Tab'''
        self.Tabcontainer.addTab(stockTab1, stockNo)
    
    def append_graphList(self,stockList):
        self._stockList = stockList


    def ret_widget(self):
        return self.BasicWidget
 