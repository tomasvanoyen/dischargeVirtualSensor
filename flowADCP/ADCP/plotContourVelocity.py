# -*- coding: utf-8 -*-
"""
Created on Mon Aug 01 14:26:55 2016

@author: vanoyeto
contact: tomas.vanoyen@mow.vlaanderen.be

This script plots the a contour plot of a velocity - component below the free surface,
together with the free surface, measured with an ADCP.
The data is loaded from pkl files which were previously written away.

Last changes:  19 - 01 - 2017
"""

# --
# Import libraries
# --

import datetime
import Tkinter, tkFileDialog
import ADCP.analyzeADCP.analyzeFunctions as adcpAnalyze
import ADCP.analyzeADCP.plotFunctions as adcpPlot

# 0. load and filter of data
# -----------------

# 0.0 read from file

switchGUI = True

if switchGUI:
    root = Tkinter.Tk()
    datadir = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Select the folder with ADCP pickle file(s)')
    if len(datadir ) > 0:
        print '============================================='
        print "You chose %s" % datadir

else:
    # TODO
    # switch for windows / linux
    operSystem = 'windows'
    if(operSystem == 'windows'):
        datadir = "P:/16_068-metingZwin/3_Uitvoering/analyse/positie 2/analyseI"
    else:
        pass

fileList = ["v1CompTotal.pkl", "v2CompTotal.pkl", "v3CompTotal.pkl", "charCompTotal.pkl"]
dfList = adcpAnalyze.loadADCPPickle(datadir, fileList)

# 0.1 filtering Data on dates
# this is not generic but is due to the fact that the
# second tidal period measured is much better.
# please just comment out if not applicable for your case

dateStart = datetime.datetime(2016,6,30,8)
dateEnd = datetime.datetime(2016,6,30,11,15)
dfList = adcpAnalyze.dfFilterDates(dfList, dateStart, dateEnd)

# 0.2 resample data on Time and drop several columns of the dataFrames
# in the Char dataFrame the values are not all floats.
# Here below a conversion is made before the resampling to float types

dfChar = dfList[3]
for str in dfChar.columns.values:
    dfChar[str] = dfChar[str].astype(float)
dfList[3] = dfChar

resTime = '5min'
dfList = adcpAnalyze.dfResampleTimeAndDrop(dfList, resTime)

# 0.3 concatenate pressure and velocity
nu = len(dfList) - 1
dfPres = dfList[nu]
dfVelComp = dfList[:nu]
dfListAug = adcpAnalyze.dfConcatenate(dfVelComp, dfPres)

# 0.4 filter out points where ADCP measures above the Free Surface
dfListFoc, presFoc = adcpAnalyze.dfFilterAboveFS(dfListAug)


# Z.0 contour plot velocity components
# -----------------

ttle = 'North Component of the Velocity [m/s]'
adcpPlot.plotContour(25, 0, dfListFoc, presFoc, ttle, 0.05)

