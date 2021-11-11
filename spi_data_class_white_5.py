# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 10:09:05 2021

@author: ShendR


"""

from nptdms import TdmsFile
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import *


class SPI_tDMS_Data(object):
    def __init__(self):
        self.channels = []
        self.groups = []
        self.root_obj_keys=[]
        self.root_obj_values=[]
        self.time_sec = []
            
    
    def run_open_tdms(self):
        root = Tk()
        root.withdraw()
        root.call('wm', 'attributes', '.', '-topmost', True)
        root.filename = filedialog.askopenfilename(initialdir='C:\ShendR\Python\SPI tDMS\TDMS files' , title='Select a file', filetypes=(('TDMS files', '*.tdms'),('All files','*.*')))
        self.tdms_file = TdmsFile(root.filename)
        root.destroy()
        root.mainloop()
        
            # Get basic info from file
        root_properties=self.tdms_file.properties.items()
        for key, value in root_properties:
            self.root_obj_keys.append(key)
            self.root_obj_values.append(value)
            
            # Get Channels names from file Groups
        self.groups = self.tdms_file.groups()   
        group = self.groups[0]
        channel_list = group.channels()
        for c in channel_list:
            self.channels.append(c.name)
            
        self.time_convert()
                    
        return self.tdms_file
    
    
        # Get data and unit from tdms file in to numpy array
    def get_data_nparray(self, channel='TimeStamp'):
        group = self.groups[0].name
        channels_data = self.tdms_file[group][channel]
        data = channels_data.data
        unit = channels_data.properties['Unit'] #-------------Unit
        nparray = np.array(data)
        return [nparray, unit]
    
    
        # Shows how long was the measurement
    def measurement_length(self):
        time_array = self.get_data_nparray()[0]
        time_length = time_array[-1]-time_array[0]
        time_length_item = time_length.item()
        time_length_sec = time_length_item.seconds
        print("Measurement start: {}".format(time_array[0]))
        print("Measurement length is {}".format(str(time_length)))
        print("Measurement length is {} seconds".format(str(time_length_sec)))
 

        # Converts and saves datetime64 into u-seconds - self.time_sec       
    def time_convert(self):
        time_array = self.get_data_nparray()[0]
#        time_sec = []
        for i in range(len(time_array)):
            a = time_array[i] - time_array[0]
            b = a.astype(float)/1000000
            self.time_sec.append(b)
#        return time_sec
    
    
        # Get the index of TimeStamp from time list
    def get_time_index(self, time_val=None):
        if time_val == None:
            index = self.time_sec.index(self.time_sec[-1]) + 1
        else:
            closest_val = min(self.time_sec, key=lambda x: abs(x - time_val))
            index = self.time_sec.index(closest_val)
        return index
    
    
        # Get tdms data (with unit) from a time window - from_t to to_t
    def get_data_interval(self, from_t=None, to_t=None, channel='TimeStamp'):
        if from_t == None:
            from_time = 0
        else:
            from_time = self.get_time_index(from_t)
        if to_t == None:
            to_time = self.get_time_index()
        else:
            to_time = self.get_time_index(to_t)
        if channel == "TimeStamp":
            data = self.time_sec[from_time:to_time]
            unit = 's'
        else:
            data = self.get_data_nparray(channel)[0][from_time:to_time]
            unit = self.get_data_nparray(channel)[1]
        return [data, unit]


        
        # Plot one channel data in function of time       
    def plot_one_channel(self, canvas, from_t=None, to_t=None, channel='Cryo Press 1 (PM2)'):
        x_data = self.get_data_interval(from_t, to_t)
        y_data = self.get_data_interval(from_t, to_t, channel)
        canvas.fig.clf()
        axes = canvas.fig.add_subplot(111)
        axes.plot(x_data[0], y_data[0])
        
        canvas.draw()
        
        
        # Compare multiple channels data in function of time - max 6 channels
    def plot_multi_ch(self, canvas, from_t=None, to_t=None, multi_channels=None):
        dict1 = {}
        channels_data = multi_channels
        x_data = self.get_data_interval(from_t, to_t, "TimeStamp")
        if len(channels_data) == 1:
            self.plot_one_channel(canvas, from_t, to_t, channel = str(channels_data[0]))
        else:
            
            for i in channels_data:
                if i != None:
                    dict1[i] = self.get_data_interval(from_t, to_t, i)
                else:
                    break
                    
            channels_no = 0
            for j in channels_data:
                if j != None:
                    channels_no+=1
                    
            nrow=channels_no
            if channels_no == 2:
                nrow = 2
                ncol = 1
            elif channels_no == 3:
                nrow = 3
                ncol = 1
            elif channels_no == 4:
                nrow = 2
                ncol = 2
            elif channels_no == 5 or 6:
                nrow = 3
                ncol = 2
            else:
                ncol=1
                nrow=channels_no
                
            canvas.fig.clf()
            axes = canvas.fig.subplots(nrow, ncol, sharex=True)
            count=0
            for r in range(nrow):
                
                if ncol==1:  
                    axes[r].plot(x_data[0], dict1[channels_data[count]][0])
                    axes[r].set_xlabel('Time [s]')
                    axes[r].set_ylabel(channels_data[count] + " [" + dict1[channels_data[count]][1] + "]")
                    count+=1
                else:
                    for c in range(ncol):
                        if channels_no==5 and [r,c]==[2,1]:
                            axes[r,c].plot(0,0)                         
                        else:                      
                            axes[r,c].plot(x_data[0], dict1[channels_data[count]][0])
                            axes[r,c].set_xlabel('Time [s]')
                            axes[r,c].set_ylabel(channels_data[count] + " [" + dict1[channels_data[count]][1] + "]")
                            count+=1
            canvas.draw()

    
    
    def overplot_multi_ch(self, canvas, from_t=None, to_t=None, multi_channels=None):
        dict1 = {}
        channels_data = multi_channels
        x_data = self.get_data_interval(from_t, to_t, "TimeStamp")
        for i in channels_data:
            if i != None:
                dict1[i] = self.get_data_interval(from_t, to_t, i)
            else:
                break
                
        channels_no = 0
        for j in channels_data:
            if j != None:
                channels_no+=1
        
        canvas.fig.clf()
        axes = canvas.fig.subplots(1,1)  
        
        part1 = axes.twinx()
        
        for i in range(channels_no):
            if dict1[channels_data[0]][1] == dict1[channels_data[i]][1]:
                axes.plot(x_data[0], dict1[channels_data[i]][0], label=channels_data[i])
                axes.set_ylabel(channels_data[i] + " [" + dict1[channels_data[i]][1] + "]")          
                legend = axes.legend(loc='upper left')

            else:
                part1.plot(x_data[0], dict1[channels_data[i]][0], label=channels_data[i])
                part1.set_ylabel(channels_data[i] + " [" + dict1[channels_data[i]][1] + "]")        
                legend = part1.legend(loc='upper right')

            axes.set_xlabel('TimeStamp [s]')   
        

        canvas.draw()
        
        
        
                # Return diff. values of given channel
    def diff_channel(self, from_t=None, to_t=None, channel='T1 - Barrel Temp'):
        array = self.get_data_interval(from_t, to_t, channel)[0]
        dchannel = np.diff(array)
        return dchannel
            
            
        # Plot diff. values of given channels
    def diff_plot(self, canvas, from_t=None, to_t=None, multi_channels=None):
        dict1 = {}
        channels_data = multi_channels
        if from_t != None:
            x_data = self.get_data_interval(from_t + 1, to_t, "TimeStamp")
        else:
            x_data = self.get_data_interval(1, to_t, "TimeStamp")
            
        for i in channels_data:
            if i != None:
                dict1[i] = self.diff_channel(from_t, to_t, i)
            else:
                break
                
        channels_no = 0
        for j in channels_data:
            if j != None:
                channels_no+=1
                
        canvas.fig.clf()
        axes = canvas.fig.subplots(1,1)
                
        for i in range(channels_no):
            axes.plot(x_data[0], dict1[channels_data[i]], label='diff. ' + channels_data[i])
            axes.set_xlabel('TimeStamp [s]')           
            legend = axes.legend()

        canvas.draw()
       


    # Testing SPI_Data Class methods
#spi_data = SPI_tDMS_Data()
