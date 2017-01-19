"""
Created on Mon Aug 01 14:26:55 2016

@author: vanoyeto
Analyzing functions on ADCP data
"""

# --
# Import libraries
# --
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import datetime
import matplotlib.cm as cm
from math import pi
import os
import errno
from scipy.signal import savgol_filter
from matplotlib.dates import date2num
from matplotlib import gridspec

def loadADCPPickle(ddir, fileL):
    dfL = []
    for fn in fileL:
        fileName = ddir + "/" + fn
        dfRead = pd.read_pickle(fileName)
        dfL.append(dfRead)
    return dfL

def dfFilterDates(dfInput, dStart, dEnd):
    dfL = []
    for dfIter in dfInput:
        dfReturn = dfIter.ix[dStart:dEnd]
        dfL.append(dfReturn)
    return dfL

def dfResampleTimeAndDrop(dfInput, resT):
    iter = 0
    dfL = []
    for dfIter in dfInput:
        dfReturn = dfIter.resample(resT)

        if iter < (len(dfInput)-1):
            dfReturn = dfReturn.drop(['Error'], axis = 1)
        else:
            dfReturn = dfReturn.drop(['Direction','errCode','statCode','cSound','Pitch','Roll','Temp','Log1','Log2','Error'], axis = 1)
        iter += 1

        dfL.append(dfReturn)

    return dfL

def dfConcatenate(dfInput, dfPr):
    dfL = []
    for dfIter in dfInput:
        dfReturn = pd.concat([dfIter, dfPr], axis=1)
        dfL.append(dfReturn)
    return dfL

def dfFilterAboveFS(dfInput):
    depthPoints = list(dfInput[0].columns.values)
    depthPoints = depthPoints[:-1]

    # met die loop hier ben ik eigenlijk echt niet gelukkig ..
    # #messy
    for x in depthPoints:
        for i in range(len(dfInput[0].index)):
            if x > dfInput[0]['Pressure'].ix[i]:
                dfInput[0][x].ix[i] = np.nan
                dfInput[1][x].ix[i] = np.nan
                dfInput[2][x].ix[i] = np.nan

    dfL = []
    for dfIter in dfInput:
        dfReturn = dfIter.dropna(axis = 1, how='all')
        dfReturn = dfReturn.drop(['Pressure'], axis = 1)
        dfReturn = dfReturn.dropna(axis = 0, how='all')
        dfL.append(dfReturn)

    dfP = dfInput[0].dropna(axis=1, how='all')
    dfP = dfP['Pressure']
    dfP = dfP.ix[dfL[0].index].values

    return dfL, dfP

def dfDepthInt(dfInput):
    depthPoints = list(dfInput[0].columns.values)
    dfL = []
    for dfIter in dfInput:
        dfIter.loc[:,depthPoints[0]] *= depthPoints[0]

        j = 1
        for it in depthPoints[1:]:
            dfIter.loc[:,it] *= depthPoints[j] - depthPoints[j-1]

            j += 1

        dfIter['Sum'] = dfIter.sum(axis = 1)

        dfL.append(dfIter)

    return dfL

def dfDepthAver(dfInput):
    depthPoints = list(dfInput[0].columns.values)
    dfL = []
    for dfIter in dfInput:
        dfCopy = dfIter.copy()
        notnan = dfIter.notnull()
        dfCopy[notnan] = 1

        dfIter.loc[:,depthPoints[0]] *= depthPoints[0]
        dfCopy.loc[:,depthPoints[0]] *= depthPoints[0]

        j = 1
        for it in depthPoints[1:]:
            dfIter.loc[:,it] *= depthPoints[j] - depthPoints[j-1]
            dfCopy.loc[:,it] *= depthPoints[j] - depthPoints[j-1]

            j += 1

        dfIter['Sum'] = dfIter.sum(axis = 1)
        dfCopy['Depth'] = dfCopy.sum(axis = 1)

        dfCopy['DepthAver'] = dfIter['Sum'] / dfCopy['Depth']
        dfCopy = dfCopy['DepthAver']

        dfL.append(dfCopy)

    return dfL

def dfCompAmplitude(dfInput):
    j = 0
    for dfIter in dfInput:
        dfKw = dfIter.mul(dfIter,1)
        if (j == 0):
            dfS = dfKw
        else:
            dfS = dfS.add(dfKw, fill_value = None)

        j += 1

    dfSqrt = dfS.apply(np.sqrt)

    return dfSqrt

def dfFilterAboveFSDatFile(dfInput):
    depthPoints = list(dfInput[0].columns.values)
    depthPoints = depthPoints[:-1]

    # TODO: met die loop hier ben ik eigenlijk echt niet gelukkig ..
    # #messy
    for x in depthPoints:
        for i in range(len(dfInput[0].index)):
            if x > dfInput[0]['Pressure'].ix[i]:
                dfInput[0][x].ix[i] = np.nan
                dfInput[1][x].ix[i] = np.nan

    dfL = []
    for dfIter in dfInput:
        dfReturn = dfIter.dropna(axis = 1, how='all')
        dfReturn = dfReturn.drop(['Pressure'], axis = 1)
        dfReturn = dfReturn.dropna(axis = 0, how='all')
        dfL.append(dfReturn)

    dfP = dfInput[0].dropna(axis=1, how='all')
    dfP = dfP['Pressure']
    dfP = dfP.ix[dfL[0].index].values

    return dfL, dfP

def dfDepthAverDatFile(dfInput):
    depthPoints = list(dfInput[0].columns.values)
    dfL = []
    dfVel = dfInput[0]
    dfDir = dfInput[1]

    dfVelX = dfVel*np.cos(dfDir*2.*np.pi/360.)
    dfVelY = dfVel*np.sin(dfDir*2.*np.pi/360.)

    dfInput = [dfVelX, dfVelY]

    for dfIter in dfInput:
        dfCopy = dfIter.copy()
        notnan = dfIter.notnull()
        dfCopy[notnan] = 1

        dfIter.loc[:,depthPoints[0]] *= depthPoints[0]
        dfCopy.loc[:,depthPoints[0]] *= depthPoints[0]

        j = 1
        for it in depthPoints[1:]:
            dfIter.loc[:,it] *= depthPoints[j] - depthPoints[j-1]
            dfCopy.loc[:,it] *= depthPoints[j] - depthPoints[j-1]

            j += 1

        dfIter['Sum'] = dfIter.sum(axis = 1)
        dfCopy['Depth'] = dfCopy.sum(axis = 1)

        dfCopy['DepthAver'] = dfIter['Sum'] / dfCopy['Depth']
        dfCopy = dfCopy['DepthAver']

        dfL.append(dfCopy)

    return dfL