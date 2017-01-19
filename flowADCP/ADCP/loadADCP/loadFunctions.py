"""
Auxiliary script to load the data from an ADCP
Author:Tomas Van Oyen 

"""

import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import matplotlib.cm as cm
from math import pi
import os
import errno
import Tkinter, tkFileDialog
import datetime

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
            
class fileHandling(object):

    '''
    Basic Object Properties for file handling
    '''

    def __init__(self,ddir):
        self.ddir = ddir

    def initializeDict(self):
        self.dataRawAmpl = {}
        self.Ampl = {}
        self.dataRawVel = {}
        self.Vel = {}

    def openVel(self,option):
        for fn in os.listdir(self.ddir):
            fnExt = fn.split('.')[1]
            if (fnExt == option):
                fileName = self.ddir + '/' + fn
                f2 = open(fileName,"r")
                self.dataRawVel[option] = f2.readlines()
                f2.close

    def openAmpl(self, option):
        for fn in os.listdir(self.ddir):
            fnExt = fn.split('.')[1]
            if (fnExt == option):
                fileName = self.ddir + '/' + fn
                f2 = open(fileName,"r")
                self.dataRawAmpl[option] = f2.readlines()
                f2.close()

    def openHeader(self):
        for fn in os.listdir(self.ddir):
            fnExt = fn.split('.')[1]
            if (fnExt == 'hdr'): 
                fileName = self.ddir + '/' + fn
                f2 = open(fileName,"r")
                self.dataRaw = f2.readlines()
                f2.close

    def openErrorLog(self):
        for fn in os.listdir(self.ddir):
            fnExt = fn.split('.')[1]
            if (fnExt == 'ssl'):
                fileName = self.ddir + '/' + fn
                f2 = open(fileName, "r")
                self.dataRaw = f2.readlines()
                f2.close

    def openDataLog(self):
        for fn in os.listdir(self.ddir):
            fnExt = fn.split('.')[1]
            if (fnExt == 'sen'):
                fileName = self.ddir + '/' + fn
                f2 = open(fileName, "r")
                self.dataRaw = f2.readlines()
                f2.close


    def openDatFile(self):
        for fn in os.listdir(self.ddir):
            fnExt = fn.split('.')[1]
            if (fnExt == 'dat'):
                fileName = self.ddir + '/' + fn
                f2 = open(fileName, "r")
                self.dataRaw = f2.readlines()
                f2.close

class loadData(fileHandling):
    '''
    read ADCP characteristics from the files
    '''
    def __init__(self,ddir):
        """

        :rtype: object
        """
        super(loadData,self).__init__(ddir)

    def makeTimeSeries(self):
        self.errorRTS = 0
        self.timeSeries = []

        for line in self.dataRaw:
            try: 
                RTsplit = line.split()
                month = int(RTsplit[0])
                day = int(RTsplit[1])
                year = int(RTsplit[2])
                hour = int(RTsplit[3])
                minute = int(RTsplit[4])
                seconds = int(RTsplit[5]) 
                
                self.timeSeries.append(datetime.datetime(year, month, day, hour, minute, seconds))
            
            except ValueError:
                dum1 = line
                self.errorRTS += 1
                print RTsplit[1]

            except IndexError:
                dum1 = line
                self.errorRTS += 2
                print RTsplit[1]

    def makeErrorTimeSeries(self):
        self.errorRTS = 0
        self.errorTimeSeries = []
        self.errorValue = []

        for line in self.dataRaw:
            if not line.startswith('Da'):
                try:
                    RTsplit = line.split()
                    datum = RTsplit[0]

                    tijd = RTsplit[1]
                    datum = datum.split('/')
                    day = int(datum[0])
                    month = int(datum[1])
                    year = int(datum[2])

                    tijd = tijd.split(':')
                    hour = int(tijd[0])
                    minute = int(tijd[1])
                    seconds = int(tijd[2])

                    self.errorTimeSeries.append(datetime.datetime(year, month, day, hour, minute, seconds))
                    self.errorValue.append(int(1))

                except ValueError:
                    dum1 = line
                    self.errorRTS += 1
                    print RTsplit[1]

                except IndexError:
                    dum1 = line
                    self.errorRTS += 2
                    print RTsplit[1]

    def readADCPcharacteristics(self):
        self.errorRADCP = 0
        self.charSeries = []

        it = 0

        for line in self.dataRaw:
            try:
                RTsplit = line.split()

                errorCode = RTsplit[6]
                statusCode = RTsplit[7]
                cSound = RTsplit[9]
                direc = float(RTsplit[10])
                pitch = float(RTsplit[11])
                roll = float(RTsplit[12])
                pressure = float(RTsplit[13])
                temp = float(RTsplit[14])
                logInput1 = float(RTsplit[15])
                logInput2 = float(RTsplit[16])

                char = []
                char.append(pressure)
                char.append(direc)
                char.append(errorCode)
                char.append(statusCode)
                char.append(cSound)
                char.append(pitch)
                char.append(roll)
                char.append(temp)
                char.append(logInput1)
                char.append(logInput2)

                char = np.array(char)
                dchar = np.array([char])

                if it == 0:
                    self.charSeries = dchar
                else:
                    self.charSeries = np.concatenate((self.charSeries, dchar))

                it += 1

            except ValueError:
                dum1 = line
                self.errorRADCP += 1

            except IndexError:
                dum1 = line
                self.errorRADCP += 2

    def readAmpl(self,option):
        self.errorRAMPL = 0
        self.Ampl[option] = []

        it = 0
        for line in self.dataRawAmpl[option]:
            RTsplit = line.split()

            amp = []
            for vel in RTsplit:
                amp.append(float(vel))

            amp = np.array(amp)
            damp = np.array([amp])

            if it == 0:
                self.Ampl[option] = damp

            else:
                self.Ampl[option] = np.concatenate((self.Ampl[option], damp))

            it += 1

    def readVel(self,option):
        self.errorRV = 0
        self.Vel[option] = []

        it = 0
        for line in self.dataRawVel[option]:
            RTsplit = line.split()
            flow = []
            for vel in RTsplit:
                flow.append(float(vel))

            flow = np.array(flow)
            dflow = np.array([flow])

            if it == 0:
                self.Vel[option] = dflow
            else:
                self.Vel[option] = np.concatenate((self.Vel[option], dflow))

            it += 1

    def readDistanceMeasPoints(self):
        self.errorRDMP = 0
        self.distanceMeasPoints = []        
        
        for line in self.dataRaw: 
            if line.startswith('Number of cells'):
                RTsplit = line.split() 
                self.numberOfCells = int(RTsplit[3])

        jt = 0 
        it = 0
        
        for line in self.dataRaw:             
            if(jt == 0):
                it += 1
                if line.startswith('Current profile cell center distance from h'):   
                    jt = 1      

        for i in range(it + 1,it + 1 + self.numberOfCells): 
            line = self.dataRaw[i]
            RTsplit = line.split()
            self.distanceMeasPoints.append(float(RTsplit[1]))                   


    def readDatFile(self):

        self.errorDatFile = 0
        self.errorRTS = 0

        self.timeSeries = []
        self.charSeries = []
        self.resultantVel = []
        self.resultantDir = []

        it = 0
        jt = 0
        lt = 0

        flow = []
        direc = []

        for line in self.dataRaw:
            RTsplit = line.split()

            if it == 0:

                # put here the time and other points
                self.numberOfCells = float(RTsplit[18])

                try:
                    month = int(RTsplit[0])
                    day = int(RTsplit[1])
                    year = int(RTsplit[2])
                    hour = int(RTsplit[3])
                    minute = int(RTsplit[4])
                    seconds = int(RTsplit[5])

                    self.timeSeries.append(datetime.datetime(year, month, day, hour, minute, seconds))

                    errorCode = RTsplit[6]
                    statusCode = RTsplit[7]
                    cSound = RTsplit[9]
                    direct = float(RTsplit[10])
                    pitch = float(RTsplit[11])
                    roll = float(RTsplit[12])
                    pressure = float(RTsplit[13])
                    temp = float(RTsplit[14])
                    logInput1 = float(RTsplit[15])
                    logInput2 = float(RTsplit[16])

                    char = []
                    char.append(pressure)
                    char.append(direct)
                    char.append(errorCode)
                    char.append(statusCode)
                    char.append(cSound)
                    char.append(pitch)
                    char.append(roll)
                    char.append(temp)
                    char.append(logInput1)
                    char.append(logInput2)

                    char = np.array(char)
                    dchar = np.array([char])

                    if jt == 0:
                        self.charSeries = dchar
                    else:
                        self.charSeries = np.concatenate((self.charSeries, dchar))
                    jt += 1

                except ValueError:
                    #dum1 = line
                    self.errorRTS += 1
                    print RTsplit[1]

                except IndexError:
                    #dum1 = line
                    self.errorRTS += 2
                    print RTsplit[1]

            else:
                # take the velocity and direction points
                vel = float(RTsplit[8])
                ddire = float(RTsplit[9])

                flow.append(vel)
                direc.append(ddire)

            it += 1

            if it == int(self.numberOfCells + 1):
                it = 0

                flow = np.array(flow)
                dflow = np.array([flow])
                direc = np.array(direc)
                ddirec = np.array([direc])

                if lt == 0:
                    self.resultantVel = dflow
                    self.resultantDir = ddirec
                else:
                    self.resultantVel = np.concatenate((self.resultantVel, dflow))
                    self.resultantDir = np.concatenate((self.resultantDir, ddirec))
                lt += 1

                flow = []
                direc = []
