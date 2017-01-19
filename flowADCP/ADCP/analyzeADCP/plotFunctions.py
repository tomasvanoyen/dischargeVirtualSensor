"""
Created on Mon Aug 01 14:26:55 2016

@author: vanoyeto
Plotting functions on ADCP data
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

def plotAmpl(ji, dfListDepthInt, dfAmpl):

    X = date2num(dfListDepthInt[0].index)
    Xtt = X[0::ji]
    xlabel = [i.strftime("%d/%m %H:%M") for i in dfListDepthInt[0].index[0::ji]]

    fig, ax = plt.subplots(figsize = (15,10) ,dpi = 80)

    ax.plot(X, dfListDepthInt[0]['Sum'], label = 'Vel. East')
    ax.plot(X, dfListDepthInt[1]['Sum'], label = 'Vel. North')
    ax.plot(X, dfListDepthInt[2]['Sum'], label = 'Vel. Up')
    ax.plot(X, dfAmpl['Sum'], label = 'Vel. Amplitude')

    ax.legend(fontsize = 15)

    ax.set_xticks(Xtt)

    # Set the xtick labels to correspond to just the dates you entered.
    ax.set_xticklabels(xlabel, size = 15)

    # Set the fontsize of the ylabel
    ax.tick_params(axis = 'y', labelsize = 15)

    # Set the x label
    ax.set_xlabel('Time', size = 15)

    # Set the y label
    ax.set_ylabel('Depth integrated velocity [$m^{2}/2$]', size = 15)

    plt.show()


def plotContour(ji, velComp, dfListFoc, presFoc, ttle, yoffset):
    '''
    :param ji: value to specify distance between the Xticks
    :param velComp: select the velocity component: 0 = North, 1 = East, 2, Vertical
    :param dfListFoc: the list of pandas dataframes holding the velocity values
    :param presFoc: the pandas dataframe with the free surface information
    :param ttle: title of the plot
    :param yoffset: offset on y-axes used for plt.ylim
    :return:
    '''


    X = date2num(dfListFoc[velComp].index)
    X = X[:-1]
    Y = list(dfListFoc[velComp].columns.values)

    ddf = dfListFoc[velComp].transpose()
    Q = list(dfListFoc[velComp].index)
    Q = Q[:-1]
    Z = ddf[Q]

    presFoc = presFoc[:-1]

    Xtt = X[0::ji]
    xlabel = [i.strftime("%d/%m %H:%M") for i in dfListFoc[velComp].index[0::ji]]

    fig, ax = plt.subplots(figsize = (10,5), dpi = 120)

    xx, yy = np.meshgrid(X, Y)
    origin = 'lower'
    CS = ax.contourf(xx, yy, Z, 15,
                      #[-1, -0.1, 0, 0.1],
                      #alpha=0.5,
                      cmap=plt.cm.bone,
                      origin=origin)

    levels = [0.]

    CS1 = ax.contour(xx, yy, Z, levels,
                    colors=('r',),
                    linewidths=(3,),
                    origin=origin)

    ax.plot(X,presFoc, c = 'k', linewidth = 2.5, label = 'Free Surface Level [m]')

    # set legend
    ax.legend(fontsize = 13)

    # Set the xtick locations to correspond to just the dates you entered.
    ax.set_xticks(X[0::ji])

    # Set the xtick labels to correspond to just the dates you entered.
    ax.set_xticklabels(xlabel)

    # Set the x label
    ax.set_xlabel('Time', size = 15)

    # Set color bar
    cbar = plt.colorbar(CS)
    cbar.add_lines(CS1)
    labelList = ['Vel of North-component [m/s]', 'Vel of East-component [m/s]', 'Vel of Vertical-component [m/s]']
    cbar.ax.set_ylabel(labelList[velComp])


    # Set limit of the y-axes
    ma = np.max(presFoc) + yoffset
    mi = np.min(presFoc) - yoffset
    plt.ylim(mi, ma)

    # set the title
    plt.title(ttle,fontsize=15)

    plt.show()


def plotVectorTime(ttle, dfListInput, ticks, ji):

    print " PLEASE NOTE THAT THE TIME LABELLING IS NOT CORRECT!"

    size = len(dfListInput[0].index[0::ji])
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))

    # X, Y = np.meshgrid(date2num(dfListDepthAver[0].index), np.ones(size))

    Q = ax.quiver(date2num(dfListInput[0].index[0::ji]), np.ones(size) * 1., dfListInput[0][0::ji],
                  dfListInput[1][0::ji])  # , pivot = 'mid')

    qk = plt.quiverkey(Q, 0.25, 0.82, 0.3, r'0.3 $m \ s^{-1}$  direction East', labelpos='N',
                       fontproperties={'size': 13})  # '{'weight': 'bold'})
    l, r, b, t = plt.axis()
    dx, dy = r - l, t - b
    plt.axis([l - 0.05 * dx, r + 0.05 * dx, b - 0.05 * dy, t + 0.05 * dy])

    a = float(len(dfListInput[0].index[0::ji]))
    stepsize = ji*(a / (ticks - 1.) - 1.)

    xlabel = [0.]
    for i in dfListInput[0].index[0::stepsize]:
        t = i.strftime("%d/%m %H:%M")
        xlabel.append(t)

    # Set ylabel
    ylabel = []
    ax.set_yticklabels(ylabel)

    # Set the xtick labels to correspond to just the dates you entered.
    ax.set_xticklabels(xlabel)

    # Set the x label
    ax.set_xlabel('Time', size=15)

    plt.title(ttle, fontsize=13)
    plt.show()

def plotDepthAver(ji, dfListInput):

    X = date2num(dfListInput[0].index)
    Xtt = X[0::ji]
    xlabel = [i.strftime("%d/%m %H:%M") for i in dfListInput[0].index[0::ji]]

    fig, ax = plt.subplots(figsize = (15,10) ,dpi = 80)

    ax.plot(X, dfListInput[0], label = 'Vel. East')
    ax.plot(X, dfListInput[1], label = 'Vel. North')
    ax.plot(X, dfListInput[2], label = 'Vel. Up')

    ax.legend(fontsize = 15, loc = 2)

    ax.set_xticks(Xtt)

    # Set the xtick labels to correspond to just the dates you entered.
    ax.set_xticklabels(xlabel, size = 15)

    # Set the fontsize of the ylabel
    ax.tick_params(axis = 'y', labelsize = 15)

    # Set the x label
    ax.set_xlabel('Time', size = 15)

    # Set the y label
    ax.set_ylabel('Depth averaged velocity [$m/2$]', size = 15)

    plt.show()

def plotVelComp(ji,  velComp, dfListFoc, level, presFoc):

    X = date2num(dfListFoc[velComp].index)
    X = X[:-1]
    Xtt = X[0::ji]
    xlabel = [i.strftime("%d/%m %H:%M") for i in dfListFoc[velComp].index[0::ji]]

    fig, ax = plt.subplots(2, sharex = True, figsize = (15,10) ,dpi = 80)

    labelList = ['Vel of North-component [m/s]', 'Vel of East-component [m/s]', 'Vel of Vertical-component [m/s]']

    presFoc = presFoc[:-1]
    velPlotComp = dfListFoc[velComp][level][:-1]

    ax[0].plot(X, presFoc, c='k', linewidth=2.5, label='Free Surface Level [m]')
    ax[1].plot(X, velPlotComp, label = labelList[velComp])

    ax[0].legend(fontsize=15)
    ax[1].legend(fontsize=15)

    ax[0].set_xticks(Xtt)
    ax[1].set_xticks(Xtt)

    # Set the xtick labels to correspond to just the dates you entered.
    ax[1].set_xticklabels(xlabel, size = 15)

    # Set the fontsize of the ylabel
    ax[0].tick_params(axis='y', labelsize=15)
    ax[1].tick_params(axis='y', labelsize=15)

    # Set the x label
    ax[1].set_xlabel('Time', size = 15)

    # Set the y label
    ax[0].set_ylabel('Free Surface Level [m/s] ', size=15)
    ax[1].set_ylabel('Velocity [ m/s ] at %s m above the bed' % level, size=15)

    plt.show()