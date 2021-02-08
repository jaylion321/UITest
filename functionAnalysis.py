import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets 
from pyqtgraph import GraphicsLayoutWidget
import numpy as np
import scipy.signal as signal


def moving_average(data, days):
    result = []
    NanList = [np.nan for i in range(0,days - 1)]
    data = data[:]
    for _ in range(len(data) - days + 1):
        result.append(round(sum(data[-days:]) / days, 2))
        data.pop()
    result = result[::-1]
    return NanList + result

def butterworth_filter(data , cutoff, nyq, order):
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = signal.filtfilt(b, a, data)
    return y

def getlocalMaxMin(data,Max :bool, Min :bool):
    maxinum = []
    mininum = []
    if (Max):
        maxinum = signal.argrelextrema(data, np.greater)
    if (Min):
        mininum = signal.argrelextrema(data, np.less) 
    #tuple to nd-array
    return maxinum[0].tolist(),mininum[0].tolist()
    