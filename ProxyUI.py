import os,sys
import json
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
from Parser.parser import Get_Stock_Performance_From_CSV,IDX_Search,Get_Sales_MonthInfo_From_From_CSV
from IdxTreeView import IdxTreeViewTab

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
    
    @abc.abstractmethod
    def construct_widget(self):
        return NotImplemented        

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
        #processes is the number of worker processes to use. If processes is None then the number returned by os.cpu_count() is used.
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
            if( regx_ip  != None and [0<=int(x)<256 for x in re.split('[\.]',re.split(':', regx_ip.group(0))[0]) ].count(True)==4 ):
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
           2. Sort by file name 
           2. Collect all data as a big dataFram by Panda'''
        file_list = []
        file_name_list = []
        #get files
        for file in os.listdir(self.dir):
            if 'price' in file:
                
                file_name_list.append(file)
        #insertion sort
        for i in range(1, len(file_name_list)):
            vTemp = file_name_list[i]
            j = i-1
            while (j >= 0 and vTemp < file_name_list[j]):    
                file_name_list[j + 1] = file_name_list[j]
                j -= 1
            file_name_list[j + 1] = vTemp

        #read file
        for file in file_name_list:
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

                      
class CustomerButton(QtWidgets.QPushButton):
    createTabSIG = QtCore.pyqtSignal(object,dict,dict,dict)
    def __init__(self,text):
        super().__init__(text)   
        self.createTabSIG.connect(self.createTab)

    @QtCore.pyqtSlot(object,dict,dict,dict)
    def createTab(self, Tabcontainer,json_data,stockinfo,Table):
        IdxTab1 = QtWidgets.QWidget()
        IdxTab1.setObjectName("IdxTab1")
        TreeViewTab = IdxTreeViewTab(stockDict=json_data,stockInfo = stockinfo, Tbl=Table) 
        # Set layout
        IdxTab1.layout = QtWidgets.QHBoxLayout()
        IdxTab1.layout.addWidget(TreeViewTab.ret_widget())
        IdxTab1.setLayout(IdxTab1.layout)
        Tabcontainer.addTab(IdxTab1, 'IDX')
    



class OverviewPanel(ToolItem):
    def __init__(self,container= None,dir=None,callback=None):     
        self.stockInfo = None
        self.dir = dir
        self.__process_num = 5
        self.toDoList = []
        self.Tabcontainer = container  

        # self.IdxTreeViewTab =  IdxTreeViewTab()
       
        semaII = mp.Semaphore(1)
        #processes is the number of worker processes to use. If processes is None then the number returned by os.cpu_count() is used.
        self.pool = mp.Pool(processes=self.__process_num, initializer = Overview_init_child,initargs=(semaII,))

        self.__OverViewWidget = None
        self.__OverViewWidget = QtWidgets.QWidget()
        self.__OverViewWidget.setObjectName("Overview")

        ''' index      '''
        self.__eps = None
        self.__roa = None
        self.__bps = None
        self.__roe = None
        self.__epsyear = None
        self.__roayear = None
        self.__bpsyear = None
        self.__roeyear = None

        self.__idxDict= {}

        self.construct_idxDict()
        self.construct_widget()

    def construct_idxDict(self):
        self.__idxDict['eps'] = {}
        self.__idxDict['bps'] = {}
        self.__idxDict['roa'] = {}
        self.__idxDict['roe'] = {}
        self.__idxDict['revM'] = {}
        self.__idxDict['revY'] = {}




        self.__idxDict['eps']['col'] = tuple(['EPS(元)','稅後EPS'])
        self.__idxDict['bps']['col'] = tuple(['BPS(元)','BPS(元)'])
        self.__idxDict['roa']['col'] = tuple(['ROA(%)','ROA(%)'])
        self.__idxDict['roe']['col'] = tuple(['ROE(%)','ROE(%)'])
        self.__idxDict['revM']['col'] = tuple(['營業收入','單月','月增(%)'])
        self.__idxDict['revY']['col'] = tuple(['營業收入','單月','年增(%)'])

        self.__idxDict['eps']['val'] = None
        self.__idxDict['bps']['val'] = None
        self.__idxDict['roa']['val'] = None
        self.__idxDict['roe']['val'] = None
        self.__idxDict['revM']['val'] = None
        self.__idxDict['revY']['val'] = None

        self.__idxDict['eps']['year'] = None
        self.__idxDict['roa']['year'] = None
        self.__idxDict['bps']['year'] = None
        self.__idxDict['roe']['year'] = None
        self.__idxDict['revM']['Month'] = None
        self.__idxDict['revY']['year'] = None

        self.__request_idx = {}
        self.__request_idx['performance'] = []
        self.__request_idx['yield'] = []
        self.__request_idx['per'] = []
        self.__request_idx['sales'] = []


    def construct_widget(self):      
        self.__OverViewWidget.layout = QtWidgets.QGridLayout()
        
        self.EPSlabel = QtWidgets.QLabel("EPS($) > ")
        self.EPSlabel.setObjectName("EPSlabel")
        self.EPSEdit = QtWidgets.QLineEdit()
        self.EPSEdit.setObjectName("EPSEdit")        
        self.EPSYear = QtWidgets.QSpinBox()
        self.EPSYear.setRange(1,5)
        self.EPSYearLabel = QtWidgets.QLabel("years")
        self.EPSYearLabel.setObjectName("EPSYearLabel")
        
        self.__OverViewWidget.layout.addWidget(self.EPSlabel, 0, 0, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.EPSEdit, 0, 1, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.EPSYear, 0, 2, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.EPSYearLabel, 0, 3, 1, 1)
          
        self.ROAlabel = QtWidgets.QLabel("ROA(%) > ")
        self.ROAlabel.setObjectName("ROAlabel")
        self.ROAEdit = QtWidgets.QLineEdit()
        self.ROAEdit.setObjectName("ROAEdit")
        self.ROAYear = QtWidgets.QSpinBox()
        self.ROAYear.setRange(1,5)
        self.ROAYearLabel = QtWidgets.QLabel("years")
        self.ROAYearLabel.setObjectName("ROAYearLabel")

        self.__OverViewWidget.layout.addWidget(self.ROAlabel, 1, 0, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.ROAEdit, 1, 1, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.ROAYear, 1, 2, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.ROAYearLabel, 1, 3, 1, 1)

        self.BPSlabel = QtWidgets.QLabel("BPS($) > ")
        self.BPSlabel.setObjectName("BPSlabel")
        self.BPSEdit = QtWidgets.QLineEdit()
        self.BPSEdit.setObjectName("BPSEdit")
        self.BPSYear = QtWidgets.QSpinBox()
        self.BPSYear.setRange(1,5)
        self.BPSYearLabel = QtWidgets.QLabel("years")
        self.BPSYearLabel.setObjectName("BPSYearLabel")        
        
        self.__OverViewWidget.layout.addWidget(self.BPSlabel, 2, 0, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.BPSEdit, 2, 1, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.BPSYear, 2, 2, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.BPSYearLabel, 2, 3, 1, 1)

        self.ROElabel = QtWidgets.QLabel("ROE(%) > ")
        self.ROElabel.setObjectName("ROElabel")
        self.ROEEdit = QtWidgets.QLineEdit()
        self.ROEEdit.setObjectName("ROEEdit")
        self.ROEYear = QtWidgets.QSpinBox()
        self.ROEYear.setRange(1,5)
        self.ROEYearLabel = QtWidgets.QLabel("years")
        self.ROEYearLabel.setObjectName("ROEYearLabel")  

        self.__OverViewWidget.layout.addWidget(self.ROElabel, 3, 0, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.ROEEdit, 3, 1, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.ROEYear, 3, 2, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.ROEYearLabel, 3, 3, 1, 1)


        self.RevernueMonthlabelP = QtWidgets.QLabel("Increase % ")
        self.RevernueMonthlabelP.setObjectName("Increase")
        self.RevernueMonthEditP = QtWidgets.QLineEdit()
        self.RevernueMonthEditP.setObjectName("Increase")        
        self.RevernueMonth = QtWidgets.QSpinBox()
        self.RevernueMonth.setRange(1,12)
        self.RevernueMonthLabel = QtWidgets.QLabel("Duration(Month))")
        self.RevernueMonthLabel.setObjectName("Duration")

        self.__OverViewWidget.layout.addWidget(self.RevernueMonthlabelP, 4, 0, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.RevernueMonthEditP, 4, 1, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.RevernueMonth, 4, 2, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.RevernueMonthLabel, 4, 3, 1, 1)


        self.RevernueYearlabelP = QtWidgets.QLabel("Increase % ")
        self.RevernueYearlabelP.setObjectName("Increase")
        self.RevernueYearEditP = QtWidgets.QLineEdit()
        self.RevernueYearEditP.setObjectName("Increase")   
        self.RevernueYear = QtWidgets.QSpinBox()
        self.RevernueYear.setRange(1,12)
        self.RevernueYearLabel = QtWidgets.QLabel("Duration(Year))")
        self.RevernueYearLabel.setObjectName("Duration")

        self.__OverViewWidget.layout.addWidget(self.RevernueYearlabelP, 5, 0, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.RevernueYearEditP, 5, 1, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.RevernueYear, 5, 2, 1, 1)
        self.__OverViewWidget.layout.addWidget(self.RevernueYearLabel, 5, 3, 1, 1)



        self.idxCheckBox = QtWidgets.QCheckBox("Save Idx Table")
        self.idxCheckBox.setObjectName("idxCheckBox")
        self.__OverViewWidget.layout.addWidget(self.idxCheckBox, 6, 0, 1, 1)
        self.idxCheckBox.click()

        self.SearchButton = CustomerButton("Match")
        self.SearchButton.setObjectName("fileButton")
        self.SearchButton.clicked.connect(self.matchFunc)
        self.__OverViewWidget.layout.addWidget(self.SearchButton, 6, 1, 1, 3)

        self.ROElabel = QtWidgets.QLabel("File")
        self.ROElabel.setObjectName("File")  
        self.__OverViewWidget.layout.addWidget(self.ROElabel,  7, 0, 1, 1)  
        self.fileButton = QtWidgets.QPushButton()
        self.fileButton.setObjectName("fileButton")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./QTDesignerUI/file.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fileButton.setIcon(icon)
        self.fileButton.clicked.connect(self.file_selection)
        self.__OverViewWidget.layout.addWidget(self.fileButton,  7, 1, 1, 1)  


        

        self.__OverViewWidget.setLayout(self.__OverViewWidget.layout)

    def setStockInfo(self, stockInfo, dir):
        self.stockInfo = stockInfo
        self.dir = dir

    def ret_widget(self):
        return self.__OverViewWidget
    
    ''' according to request, find the matched stocks'''
    def matchFunc(self):
        self.SearchButton.setEnabled(False)
        eps = self.EPSEdit.text()
        roa = self.ROAEdit.text()
        bps = self.BPSEdit.text()
        roe = self.ROEEdit.text()
        revM = self.RevernueMonthEditP.text()
        revY = self.RevernueYearEditP.text()
        #checking input format, it must be integer, float empty char
        #It is that we do not care the index which is empty char
        #If year is 0, we also do not care about this index for 1 year
        epsReg = re.match(r'^([\d]*)$|^([\d]+.)([\d]+)$', eps)
        roaReg = re.match(r'^([\d]*)$|^([\d]+.)([\d]+)$', roa)
        bpsReg = re.match(r'^([\d]*)$|^([\d]+.)([\d]+)$', bps)
        roeReg = re.match(r'^([\d]*)$|^([\d]+.)([\d]+)$', roe)
        revMReg = re.match(r'^([\d]*)$|^([\d]+.)([\d]+)$', revM)
        revYReg = re.match(r'^([\d]*)$|^([\d]+.)([\d]+)$', revY)

        if (epsReg == None or
            roaReg == None or
            bpsReg == None or
            roeReg == None or
            revMReg == None or
            revYReg == None):
            return
   
        if (eps != ''):
           self.__eps = float(eps)
           self.__idxDict['eps']['val'] = self.__eps
           self.__request_idx['performance'].append(self.__idxDict['eps']['col'])
        if (roa != ''):
            self.__roa = float(roa)
            self.__idxDict['roa']['val'] =  self.__roa
            self.__request_idx['performance'].append(self.__idxDict['roa']['col'])
        if (bps != ''):
            self.__bps = float(bps)
            self.__request_idx['performance'].append(self.__idxDict['bps']['col'])
        if (roe != ''):
            self.__roe = float(roe)
            self.__idxDict['roe']['val'] =   self.__roe
            self.__request_idx['performance'].append(self.__idxDict['roe']['col'])
        if (revM != ''):
            self.__revM = float(revM)
            self.__idxDict['revM']['val'] =   self.__revM
            self.__request_idx['sales'].append(self.__idxDict['revM']['col'])
        if (revY != ''):
            self.__revY  = float(revY)
            self.__idxDict['revY']['val'] =   self.__revY  
            self.__request_idx['sales'].append(self.__idxDict['revY']['col'])

        self.__epsyear = self.EPSYear.value() 
        self.__roayear = self.ROAYear.value()
        self.__bpsyear = self.BPSYear.value() 
        self.__roeyear = self.ROEYear.value() 
        self.__revMonth = self.RevernueMonth.value() 
        self.__revYear = self.RevernueYear.value() 
        self.__idxDict['eps']['year'] = self.__epsyear
        self.__idxDict['roa']['year'] = self.__roayear - 1
        self.__idxDict['bps']['year'] = self.__bpsyear
        self.__idxDict['roe']['year'] = self.__roeyear - 1
        self.__idxDict['revM']['month'] = self.__revMonth
        self.__idxDict['revY']['year'] = self.__revYear 


        Reqyear = max(self.__epsyear,self.__roayear,self.__bpsyear,self.__roeyear)
        curYear = QtCore.QDateTime.currentDateTime().addYears(-1).date().year()

        if (int(curYear) - Reqyear + 1== 0) :
            self.SearchButton.setEnabled(True)    
            return
        else:
            Reqyear = str(curYear - Reqyear + 1)
            print("Request Year",Reqyear)

        i = 0 
        request_idx =self.__request_idx
        # for group in self.stockInfo.keys():
        #     path = "./" + group 
        #     for stockInfo in self.stockInfo[group]:
        #         self.toDoList.append((path,stockInfo.code,group,stockInfo.name,Reqyear,request_idx))
        '''Quick Test'''
        path = "./" + '航運業' 
        for stockInfo in self.stockInfo['航運業']:
            self.toDoList.append((path,stockInfo.code,'航運業',stockInfo.name,Reqyear,request_idx))



        # IdxTab1 = QtWidgets.QWidget()
        # IdxTab1.setObjectName("IdxTab1")
        # IdxTreeView = IdxTreeViewTab() 
        # # Set layout
        # IdxTab1.layout = QtWidgets.QHBoxLayout()
        # IdxTab1.layout.addWidget(IdxTreeView.ret_widget())
        # IdxTab1.setLayout(IdxTab1.layout)
        # self.Tabcontainer.addTab(IdxTab1, 'IDX')
        
        # #callback will be called once, when all async func be finished
        self.pool.starmap_async(getEligibled,self.toDoList,callback=self.dumpMatched)            

    def dumpMatched(self,tupleList): 
        outcome = []
        __json_output = {}
        __Table_output = {}
        __idxList = []
        fileName = ''
        for key in self.__idxDict.keys():
            if (self.__idxDict[key]['val'] != None ):
                __idxList.append(key)
                if ( key != 'revM' ):
                    __year = str(self.__idxDict[key]['year']).replace('.','&')
                    fileName += '__'+key+'_'+str(self.__idxDict[key]['val'])+'_year_'+__year
                else:
                    fileName += '__'+key+'_'+str(self.__idxDict[key]['val'])+'_month_'+ str(self.__idxDict[key]['month'])
        fileName += '.json'
        print(fileName)
        for performanceTable,revTable,code,group,name in  tupleList:
            print(code,name)

            if (group not in  __json_output.keys()):
                __json_output[group] = {}
                __Table_output[group] = {}
            if ( type(performanceTable).__name__ == 'DataFrame'):
                performanceTable = performanceTable.round(2)
                for key in ['bps','eps','roa','roe']:
                    if (self.__idxDict[key]['val'] != None ):
                        ret = IDX_Search(performanceTable, int(self.__idxDict[key]['year']),self.__idxDict[key]['col'] , self.__idxDict[key]['val'])
                        outcome.append(ret)
            if ( type(revTable).__name__ == 'DataFrame'):
                for key in ['revM','revY']:
                    if (self.__idxDict[key]['val'] != None):
                        if key == 'revM':
                            ret = IDX_Search(revTable, self.__idxDict[key]['month'],self.__idxDict[key]['col'] , self.__idxDict[key]['val'])
                        elif key == 'revY':
                            ret = IDX_Search(revTable, self.__idxDict[key]['year'],self.__idxDict[key]['col'] , self.__idxDict[key]['val'])
                        outcome.append(ret)
            
            if( outcome.count(True) >= len(__idxList) ):
                ''' wrtie to file'''
                __json_output[group][code] = {}
                __json_output[group][code]['code'] = code
                __json_output[group][code]['name'] = name  

                __Table_output[group][code] = {}
                __Table_output[group][code]['code'] = code
                __Table_output[group][code]['name'] = name 
                __Table_output[group][code]['performanceTable'] = performanceTable
                __Table_output[group][code]['revTable'] = revTable

            outcome = []
        print('write file : ', fileName, 'save report :',self.idxCheckBox.isChecked())
        # print(__json_o     utput)
        with open(fileName, "w") as outfile:  
            json.dump(__json_output, outfile)

        self.SearchButton.createTabSIG.emit(self.Tabcontainer,__json_output, self.stockInfo,__Table_output)
        self.SearchButton.setEnabled(True)            

    def file_selection(self):
        files = QtWidgets.QFileDialog.getOpenFileNames(None,
        "多檔案選擇",
        "./",
        "All Files (*);;Text Files (*.json)")
        with open(files[0][0]) as json_file:
            data = json.load(json_file)
        self.SearchButton.createTabSIG.emit(self.Tabcontainer,data, self.stockInfo)

def Overview_init_child(_sema):
    global semaII 
    semaII = _sema 

def getEligibled(path,code,group,name,year,request_idxist):
    performanceTable = None
    yieldTable = None
    perTable = None
    revTable = None
    stockName = re.sub('[/\*?:\"<>|]','',name)
    print(os.listdir(path+ "/"+str(code)+'_'+ stockName))

    if len(request_idxist['sales']) != 0: 
        revTable = Get_Sales_MonthInfo_From_From_CSV(path+ "/"+str(code)+'_'+ stockName,  \
                code)

    if len(request_idxist['performance']) != 0: 
        performanceTable = Get_Stock_Performance_From_CSV(path+ "/"+str(code)+'_'+ stockName,  \
                code)

    return (performanceTable,revTable,code,group,stockName)

# as utf-8 to show chinese
# with open('eps.txt', 'w',encoding="utf-8") as file:
#     for key in self.stockInfo.keys(): 
#         path = "./" + key 
#         file.write (path)    
#         for stockInfo in self.stockInfo[key]:
#             file.write (key+":"+str(stockInfo.code))
#             table = Concat_Table_With_IDX(path,stockInfo.code)
#             if ( type(table).__name__ == 'DataFrame') :
#                 file.write (table.to_string())

def Revenue_init_child(_sema):
    global semaIII 
    semaIII = _sema

class RevenuePanel(ToolItem):
    def __init__(self,container= None,dir=None,callback=None): 
        self.stockInfo = None
        self.dir = dir
        self.__process_num = 5
        self.toDoList = []
        self.Tabcontainer = container  
        # self.IdxTreeViewTab =  IdxTreeViewTab()
       
        semaIII = mp.Semaphore(1)
        #processes is the number of worker processes to use. If processes is None then the number returned by os.cpu_count() is used.
        self.pool = mp.Pool(processes=self.__process_num, initializer = Revenue_init_child,initargs=(semaIII,))
        self.__RevenueWidget = None
        self.__RevenueWidget = QtWidgets.QWidget()
        self.__RevenueWidget.setObjectName("Revenue")



        self.construct_widget()

    def setStockInfo(self, stockInfo, dir):
        self.stockInfo = stockInfo
        self.dir = dir

    def ret_widget(self):
        return self.__RevenueWidget


    def construct_widget(self):      
        self.__RevenueWidget.layout = QtWidgets.QGridLayout()
        
        self.Revernuelabel = QtWidgets.QLabel("Increase %(last year) ")
        self.Revernuelabel.setObjectName("Increase")
        self.RevernueEdit = QtWidgets.QLineEdit()
        self.RevernueEdit.setObjectName("Increase")        
        self.RevernueMonth = QtWidgets.QSpinBox()
        self.RevernueMonth.setRange(1,12)
        self.RevernueMonthLabel = QtWidgets.QLabel("Duration(year)")
        self.RevernueMonthLabel.setObjectName("Duration")
        
        self.__RevenueWidget.layout.addWidget(self.Revernuelabel, 0, 0, 1, 1)
        self.__RevenueWidget.layout.addWidget(self.RevernueEdit, 0, 1, 1, 1)
        self.__RevenueWidget.layout.addWidget(self.RevernueMonth, 0, 2, 1, 1)
        self.__RevenueWidget.layout.addWidget(self.RevernueMonthLabel, 0, 3, 1, 1)
          

        self.idxCheckBox = QtWidgets.QCheckBox("Save Idx Table")
        self.idxCheckBox.setObjectName("idxCheckBox")
        self.__RevenueWidget.layout.addWidget(self.idxCheckBox, 1, 0, 1, 1)
        self.idxCheckBox.click()

        self.SearchButton = CustomerButton("Match")
        self.SearchButton.setObjectName("fileButton")
        self.SearchButton.clicked.connect(self.matchFunc)
        self.__RevenueWidget.layout.addWidget(self.SearchButton, 1, 1, 1, 3)

        self.Revernuelabel = QtWidgets.QLabel("Compare with")
        self.Revernuelabel.setObjectName("Compare")
        self.fileButton = QtWidgets.QPushButton()
        self.fileButton.setObjectName("fileButton")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./QTDesignerUI/file.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fileButton.setIcon(icon)
        # self.fileButton.clicked.connect(self.file_selection)
        self.__RevenueWidget.layout.addWidget(self.Revernuelabel, 2, 0, 1, 1)
        self.__RevenueWidget.layout.addWidget(self.fileButton, 2, 1, 1, 1)

        # self.ROElabel = QtWidgets.QLabel("File")
        # self.ROElabel.setObjectName("File")  
        # self.__OverViewWidget.layout.addWidget(self.ROElabel,  5, 0, 1, 1)  
        # self.fileButton = QtWidgets.QPushButton()
        # self.fileButton.setObjectName("fileButton")
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap("./QTDesignerUI/file.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # self.fileButton.setIcon(icon)
        # self.fileButton.clicked.connect(self.file_selection)
        # self.__OverViewWidget.layout.addWidget(self.fileButton,  5, 1, 1, 1)          

        self.__RevenueWidget.setLayout(self.__RevenueWidget.layout)

    ''' according to request, find the matched stocks'''
    def matchFunc(self):
        Revernue = self.RevernueEdit.text()

        
        #checking input format, it must be integer, float empty char
        #It is that we do not care the index which is empty char
        #If year is 0, we also do not care about this index for 1 year
        RevernueReg = re.match(r'^([\d]*)$|^([\d]+.)([\d]+)$', Revernue)
        self.__revernueMonthReg = self.RevernueMonth.value() 
        
        if (RevernueReg == None):
            return

        i = 0 
        for group in self.stockInfo.keys():
            path = "./" + group 
            for stockInfo in self.stockInfo[group]:
                self.toDoList.append((path,stockInfo.code,group,stockInfo.name,self.__revernueMonthReg))

        # #callback will be called once, when all async func be finished
        self.pool.starmap_async(getEligibled,self.toDoList,callback=self.dumpMatched)