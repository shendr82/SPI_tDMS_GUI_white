# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 15:21:44 2021

@author: ShendR
"""

from SPI_GUI_white_5 import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QDialog

import spi_data_class_white_5

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np


class SPI_GUI(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
            # Canvas on GUI       
        self.Big_graphicsView = Canvas(parent=self.centralwidget)
        self.Big_graphicsView.setMinimumSize(QtCore.QSize(500, 400))
        self.Big_graphicsView.setObjectName("Big_graphicsView")
#        self.Big_graphicsView.setStyleSheet("background-color: rgb(58, 59, 61);\n"
#"border-color: rgb(0, 0, 0);")
        self.gridLayout.addWidget(self.Big_graphicsView, 2, 0, 1, 1)
        
            # Toolbar on GUI
        self.toolbar = NavigationToolbar(self.Big_graphicsView, self.Big_graphicsView) 
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        
            # SPI data Class
        self.spi_tdms = spi_data_class_white_5.SPI_tDMS_Data()
            # Open file with GUI - button or Ctrl+O
        self.menuFile.triggered.connect((lambda: self.open_file()))
        self.actionOpen_TDMS_file.setShortcut('Ctrl+O')
        
            # Set up TextBox - for adding text messages
        self.setup_logbook()
            
            # Button cliked - select channel from list
        self.ParamterPlot_button.clicked.connect(lambda: self.plot_button(self.Big_graphicsView, from_t=self.from_time1.text(), to_t=self.to_time1.text(), channel=self.selected_item))
        self.from_time1.returnPressed.connect(lambda: self.plot_button(self.Big_graphicsView, from_t=self.from_time1.text(), to_t=self.to_time1.text(), channel=self.selected_item))
        self.to_time1.returnPressed.connect(lambda: self.plot_button(self.Big_graphicsView, from_t=self.from_time1.text(), to_t=self.to_time1.text(), channel=self.selected_item))
        self.filtered_button.clicked.connect(lambda: self.filtered_list())
        self.allchannels_button.clicked.connect(lambda: self.show_all_list())
        
        self.plot_multi_button.clicked.connect(lambda: self.multi_plot_button(self.Big_graphicsView, from_t=self.from_time2.text(), to_t=self.to_time2.text(), multi_channels=self.x))
        self.from_time2.returnPressed.connect(lambda: self.multi_plot_button(self.Big_graphicsView, from_t=self.from_time2.text(), to_t=self.to_time2.text(), multi_channels=self.x))
        self.to_time2.returnPressed.connect(lambda: self.multi_plot_button(self.Big_graphicsView, from_t=self.from_time2.text(), to_t=self.to_time2.text(), multi_channels=self.x))
        
        self.overplot_button.clicked.connect(lambda: self.overplot_button1(self.Big_graphicsView, from_t=self.from_time2.text(), to_t=self.to_time2.text(), multi_channels=self.x))
        self.diff_button.clicked.connect(lambda: self.diff_button_func(self.Big_graphicsView, from_t=self.from_time2.text(), to_t=self.to_time2.text(), multi_channels=self.x))
        

        # After a file is opened - update GUI        
    def open_file(self):          
        self.Parameter_listView.clear()
        self.Parameter_listView_2.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.Parameter_listView.setAlternatingRowColors(False)
        self.Parameter_listView_2.clear()
        self.Parameter_listView_2.setAlternatingRowColors(False)
        self.ShotID_box.clear()
        self.spi_tdms = spi_data_class_white_5.SPI_tDMS_Data()
        self.spi_tdms.run_open_tdms()
        shot_id = self.spi_tdms.root_obj_values[0]
        self.ShotID_box.setText(shot_id)
        channels = self.spi_tdms.channels
        for i in channels:
            self.Parameter_listView.addItem(str(i))
            self.Parameter_listView_2.addItem(str(i))
        self.Parameter_listView.itemClicked.connect(self.listitemclicked)
        self.Parameter_listView_2.itemClicked.connect(self.listitemsclicked)
        
        
        
        # Button cliked - select single channel from list
    def listitemclicked(self):
        self.selected_item = self.Parameter_listView.currentItem().text()
        self.logbook.append('Item in the list is clicked:  ' + self.selected_item)
        return self.selected_item
    
    
    
        # Select multiple channels from list - max. 6 channels
    def listitemsclicked(self):
        self.selected_items = self.Parameter_listView_2.currentItem().text()
        items = self.Parameter_listView_2.selectedItems()
        self.x = []
        for i in range(len(items)):
            self.x.append(str(self.Parameter_listView_2.selectedItems()[i].text()))
            if len(self.x) > 6:
                self.x.pop(0)                
        print(self.x)
        self.logbook.append('Item is added to selection:  ' + self.selected_items)
        return self.x
    
    
    
        # Set up TextBox - for adding messages
    def setup_logbook(self, text='check'):
        self.logbook = self.Big_textBrowser
        font = self.logbook.font()
        font.setFamily("Courier")
        font.setPointSize(8)        
        self.logbook.append("Welcome to SPI sensor data: Open tDMS file")
        self.logbook.moveCursor(QtGui.QTextCursor.End)
        self.logbook.ensureCursorVisible()
        
        
        
        # When Plot Single Channel Button is pushed - running this method
    def plot_button(self, canvas, from_t, to_t, channel):
        try:
            self.logbook.append('Plotting selected item: ' + channel)
            if from_t == "None":
                from_t = None
            else:
                from_t = int(from_t)
            if to_t == "None":
                to_t = None
            else:
                to_t = int(to_t)    
                
            self.spi_tdms.plot_one_channel(canvas, from_t, to_t, channel)
            
            interval_data = np.array(self.spi_tdms.get_data_interval(from_t, to_t, channel)[0])
            self.max_lineEdit.setText(str(round(interval_data.max(),3)))
            self.min_lineEdit.setText(str(round(interval_data.min(),3)))
            self.mean_lineEdit.setText(str(round(interval_data.mean(),3)))
                       
        except:
            self.logbook.append("<span style=\"color:#ff0000\" >"+'Error plotting request'+"</span>")
            
            
                
         # When Plot Multiple Channel Button is pushed - running this method        
    def multi_plot_button(self, canvas, from_t, to_t, multi_channels):
        try:
            no_of_channels = len(multi_channels)
            print("Number of channels selected: " + str(no_of_channels))
            self.logbook.append("Number of channels selected: " + str(no_of_channels))
            if from_t == "None":
                from_t = None
            else:
                from_t = int(from_t)
            if to_t == "None":
                to_t = None
            else:
                to_t = int(to_t)   
            self.spi_tdms.plot_multi_ch(canvas, from_t, to_t, multi_channels)
        except:
            self.logbook.append("<span style=\"color:#ff0000\" >"+'Error plotting request'+"</span>")

                
                
    def overplot_button1(self, canvas, from_t, to_t, multi_channels):
        try:
            no_of_channels = len(multi_channels)
            print("Number of channels selected: " + str(no_of_channels))
            self.logbook.append("Number of channels selected: " + str(no_of_channels))
            if from_t == "None":
                from_t = None
            else:
                from_t = int(from_t)
            if to_t == "None":
                to_t = None
            else:
                to_t = int(to_t)   
            self.spi_tdms.overplot_multi_ch(canvas, from_t, to_t, multi_channels)
        except:
            self.logbook.append("<span style=\"color:#ff0000\" >"+'Error plotting request'+"</span>")
 
                
                
    def diff_button_func(self, canvas, from_t, to_t, multi_channels):
        try:
            no_of_channels = len(multi_channels)
            print("Number of channels selected: " + str(no_of_channels))
            self.logbook.append("Number of channels selected: " + str(no_of_channels))
            if from_t == "None":
                from_t = None
            else:
                from_t = int(from_t)
            if to_t == "None":
                to_t = None
            else:
                to_t = int(to_t)   
            self.spi_tdms.diff_plot(canvas, from_t, to_t, multi_channels)
        except:
            self.logbook.append("<span style=\"color:#ff0000\" >"+'Error plotting request'+"</span>")
                

                
    def filtered_list(self):
        filtered_list = ['Cryo Press 0 (PM1)', 
                         'Cryo Press 1 (PM2)',
                         'Cryo Press 2 (PM3)',
                         'Cryo Press 3 (PM4)',
                         'Cryo Press 4 (PM5)',
                         'T1 - Barrel Temp',
                         'T2 - CHead Bottom',
                         'T3 - CHead Top',
                         'T4 - He Connection',
                         'T5 - He Distributor',
                         'T6 - Heat Shield',
                         'T7 - HeatExc DownStr ',
                         'T8 - HeatExc UpStr']
        
        self.Parameter_listView.clear()
        self.Parameter_listView_2.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.Parameter_listView.setAlternatingRowColors(False)
        self.Parameter_listView_2.clear()
        self.Parameter_listView_2.setAlternatingRowColors(False)
        for i in filtered_list:
            self.Parameter_listView.addItem(str(i))
            self.Parameter_listView_2.addItem(str(i))
        self.Parameter_listView.itemClicked.connect(self.listitemclicked)
        self.Parameter_listView_2.itemClicked.connect(self.listitemsclicked)
        
                
    def show_all_list(self):
        self.Parameter_listView.clear()
        self.Parameter_listView_2.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.Parameter_listView.setAlternatingRowColors(False)
        self.Parameter_listView_2.clear()
        self.Parameter_listView_2.setAlternatingRowColors(False)
        channels = self.spi_tdms.channels
        for i in channels:
            self.Parameter_listView.addItem(str(i))
            self.Parameter_listView_2.addItem(str(i))
        self.Parameter_listView.itemClicked.connect(self.listitemclicked)
        self.Parameter_listView_2.itemClicked.connect(self.listitemsclicked)
        
                
                

    # Canvas on GUI to plot on
class Canvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure()
        self.fig.clear()
#        self.fig.patch.set_facecolor('None')
        self.axes = self.fig.add_subplot(111)
#        self.axes.set_facecolor('None')
        self.axes.axis('off')
        super(Canvas, self).__init__(self.fig)      
        
       
         
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    
    widget = SPI_GUI()
    widget.show()
    
    app.exec_()