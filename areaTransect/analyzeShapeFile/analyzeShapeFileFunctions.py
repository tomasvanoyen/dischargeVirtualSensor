# -*- coding: utf-8 -*-
import shapefile
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import re
import matplotlib.patches as patches
import itertools
import pyproj

# ----------------------------------------------------------------------------------------------------------------- #
def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60);
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd;

# ----------------------------------------------------------------------------------------------------------------- #
def parse_dms(dms):
    parts = re.split('[°\'"]+', dms)
    dd = dms2dd(parts[0], parts[1], parts[2], parts[3])
    return dd

# ----------------------------------------------------------------------------------------------------------------- #
def find_nearest(array, value): 
    array = np.array(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx]

# ----------------------------------------------------------------------------------------------------------------- #
class fileHandling(object):

    '''
    Basic Object Properties for file handling
    '''

    def __init__(self,fn,ddir):
        self.shDir = ddir
        self.fn = fn

# ----------------------------------------------------------------------------------------------------------------- #
class analyzeShape(fileHandling):
    '''
    Functions to analyze shapefiles
    '''
    # ----------------------------------------------------------------------------------------------------------------- #
    def __init__(self,fn,ddir):
        """

        :rtype: object
        """
        super(analyzeShape,self).__init__(fn, ddir)
        fln = self.fn + '.shp'
        fn = os.path.join(self.shDir, fln)
        myshp = open(fn, "rb")

        fln = self.fn + '.dbf'
        fn = os.path.join(self.shDir, fln)
        mydbf = open(fn, "rb")

        self.sf = shapefile.Reader(shp=myshp, dbf=mydbf)

    # ----------------------------------------------------------------------------------------------------------------- #
    def scatterPlotPoints(self):
        """
        Funtion to scatter plot the points which are inside a shape file.
        Pay attention: fileName is the file name but without extension!
        :param fileName:
        :param shDir:
        :return:
        """

        # get both geometry and records simultaneously
        shapeRecs = self.sf.shapeRecords()

        # Make scatter plot of x and y
        xco = []
        yco = []
        for i in np.arange(len(shapeRecs)):
            x, y = shapeRecs[i].record[2], shapeRecs[i].record[3]
            xco.append(x)
            yco.append(y)

        fig, ax = plt.subplots()
        ax.scatter(xco,yco)
        plt.show()

    # ----------------------------------------------------------------------------------------------------------------- #
    def scatterPlotPointsAndChoseROI(self):
        """
        Chose your region of interest (ROI) by first clicking on the left bottom corner, and
        then on the upper right corner.
        :return:
        """

        # Simple mouse click function to store coordinates
        def onclick(event):
            global ix, iy
            ix, iy = event.xdata, event.ydata
            #print 'x = %d, y = %d'% (ix, iy)

            self.coords.append((ix, iy))

            # Disconnect after 2 clicks
            if len(self.coords) == 2:
                fig.canvas.mpl_disconnect(cid)
                plt.close(1)

            return

        # get both geometry and records simultaneously
        shapeRecs = self.sf.shapeRecords()

        # Make scatter plot of x and y
        xco = []
        yco = []
        for i in np.arange(len(shapeRecs)):
            x, y = shapeRecs[i].record[2], shapeRecs[i].record[3]
            xco.append(x)
            yco.append(y)

        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        ax.scatter(xco, yco)

        self.coords = []

        # Call click func
        cid = fig.canvas.mpl_connect('button_press_event', onclick)

        plt.title('Chose ROI (Rect.): 1/ left bottom 2/ upper right corner')

        plt.show(1)

        fig = plt.figure()
        ax = fig.add_subplot(111)  # , aspect = 'equal')
        ax.scatter(xco, yco)

        cornerx = self.coords[0][0]
        cornery = self.coords[0][1]
        width = np.abs(self.coords[0][0] - self.coords[1][0])
        height = np.abs(self.coords[0][1] - self.coords[1][1])

        ax.add_patch(patches.Rectangle((cornerx, cornery), width, height, fill=False))

        plt.show()

    # ----------------------------------------------------------------------------------------------------------------- #
    def shapeToDF(self, switchClicking):
        """

        :return:
        """

        #manual to avoid the clicking .. 
        if (switchClicking == False):
            self.coords = []
            self.coords.append((80136.2903226, 229159.375))
            self.coords.append((80449.5967742, 229340.625))

        # make DataFrame of x, y, z
        shapeRecs = self.sf.shapeRecords()
        listShape = ['x-coor', 'y-coor', 'z-coor']
        coordinates = []
        for i in np.arange(len(shapeRecs)):
            x, y, z = shapeRecs[i].record[2], shapeRecs[i].record[3], shapeRecs[i].record[4]
            co = []
            co.append(x)
            co.append(y)
            co.append(z)

            co = np.array(co)
            dco = np.array([co])
            if i == 0:
                coordinates = dco
            else:
                coordinates = np.concatenate((coordinates, dco))

        dfCoor = pd.DataFrame(coordinates, columns=listShape)
        
        cornerx = float(self.coords[0][0])
        cornery = float(self.coords[0][1])
        width = np.abs(self.coords[0][0] - self.coords[1][0])
        height = np.abs(self.coords[0][1] - self.coords[1][1])

        self.dfTransect = dfCoor[(cornerx <= dfCoor['x-coor']) & (dfCoor['x-coor'] <= cornerx + width) &
                                 (cornery <= dfCoor['y-coor']) & (dfCoor['y-coor'] <= cornery + height)]


    # ----------------------------------------------------------------------------------------------------------------- #
    def projectTransectToLine(self):
        """

        :return:
        """

        # 1. use polyfit
        #p = np.poly1d(np.polyfit(dfInlaat['x-coor'], dfInlaat['y-coor'], 1))
        #lijn = p(dfInlaat['x-coor'])
        # ax.plot(dfInlaat['x-coor'], lijn)

        # 2. uses stats library
        self.slope, self.intercept, r_value, p_value, std_err = stats.linregress(self.dfTransect['x-coor'], self.dfTransect['y-coor'])

        # project points on to the line
        d = -1.0 / self.slope
        c = self.dfTransect['y-coor'].values - d * self.dfTransect['x-coor'].values
        self.xe = (self.intercept - c) / (d - self.slope)
        self.ye = self.slope * self.xe + self.intercept

    # ----------------------------------------------------------------------------------------------------------------- #
    def projectPointToLine(self, measuredLoc):
        """

        :return:
        """

        # project points on to the line
        d = -1.0 / self.slope
        xlo = np.array(measuredLoc['x'])
        ylo = np.array(measuredLoc['y'])
        c = ylo - d * xlo
        self.xp = (self.intercept - c) / (d - self.slope)
        self.yp = self.slope * self.xp + self.intercept

    # ----------------------------------------------------------------------------------------------------------------- #
    def dmsloc2dd(self, s):
        s1, s2 = s.split(',')
        lat, long = parse_dms(s1), parse_dms(s2)
        return lat, long


    # ----------------------------------------------------------------------------------------------------------------- #
    def plotGPSCoor(self, gpsC, wgs84, lamb72New):

        z = 0
        fig, ax = plt.subplots()
        colors = itertools.cycle(["r", "c"])
        markers = itertools.cycle([">", "+"])

        for gpsCoor in gpsC:

            xList = []
            yList = []
            zList = []
            latList = []
            longList = []

            for s in gpsCoor:
                # 0. convert dms to dd
                lat, long = self.dmsloc2dd(s)

                # 1. transform coordinates
                #    from WGS84 to lamb72New 
                x, y, zt = pyproj.transform(wgs84, lamb72New, long, lat, z)

                latList.append(lat)
                longList.append(long)
                xList.append(x)
                yList.append(y)
                zList.append(z)

            measureloc = {'location': ['loc 2', 'loc 1', 'loc 3'],
                          'x': xList,
                          'y': yList}

            # ----------------------------------------------------------------------------------------------------------------- #
            # project measurement point on line
            self.projectPointToLine(measureloc)

            x = np.array(xList)
            y = np.array(yList)
            ax.scatter(x, y, color=next(colors), marker=next(markers))

        ax.scatter(self.xp, self.yp, color='b')
        ax.scatter(self.dfTransect['x-coor'], self.dfTransect['y-coor'], color='red')
        ax.plot(self.xe, self.ye)
        ax.axis('equal')
        plt.show()

    # ----------------------------------------------------------------------------------------------------------------- #
    def computeAngleY(self):
        diffX = np.amax(self.xe) - np.amin(self.xe)
        idxmin = (self.xe).argmin()
        idxmax = (self.xe).argmax()
        
        diffY = self.ye[idxmax] - self.ye[idxmin]

        self.angle = np.arctan2(diffX,diffY)*360./(2.*np.pi)
        self.normal = self.angle + 90. 

    # ----------------------------------------------------------------------------------------------------------------- #
    def probeVertValues(self):
        z = 0
        zl = self.dfTransect['z-coor'].values
        self.zp = []
        for xs in self.xp:
            # print xs
            ii = 0
            for x in self.xe:
                if xs > x:
                    # print x, ii
                    z = 0.5 * (zl[ii] + zl[ii - 1])
                    self.zp.append(z)
                    break
                ii += 1

    # ----------------------------------------------------------------------------------------------------------------- #
    def plotVertTrans(self):
        cornerx = np.amin(self.xe)
        cornery = np.amin(self.ye)

        self.xRelTransect = []
        for i in np.arange(len(self.xe)):
            xd = np.sqrt(np.power((self.xe[i] - cornerx), 2.) + np.power((self.ye[i] - cornery), 2.))
            self.xRelTransect.append(xd)

        fig, ax = plt.subplots()
        ax.plot(self.xRelTransect, self.dfTransect['z-coor'].values)

        self.xRelMeas = []
        for i in np.arange(len(self.xp)):
            xd = np.sqrt(np.power((self.xp[i] - cornerx), 2.) + np.power((self.yp[i] - cornery), 2.))
            self.xRelMeas.append(xd)

        ax.scatter(self.xRelMeas, self.zp, c='red')

        plt.show()

    # ----------------------------------------------------------------------------------------------------------------- #
    def adjustTrans(self, xL, xF): 
        
        zT = self.dfTransect['z-coor'].values
        
        idx, xLast = find_nearest(self.xRelTransect, xL)
        zLast = zT[idx]

        idx, xFirst = find_nearest(self.xRelTransect, xF)
        zFirst = zT[idx]
        
        grad = (zLast - zFirst) / (xLast - xFirst)

        self.zAdj = []
        for i in np.arange(len(self.xRelTransect)):
            if (xLast > self.xRelTransect[i] and xFirst < self.xRelTransect[i]):
                zz = zFirst + grad*(self.xRelTransect[i] - xFirst)
                self.zAdj.append(zz)
            else: 
                self.zAdj.append(zT[i])
        
        self.xRelTransect = np.array(self.xRelTransect)
        self.zAdj = np.array(self.zAdj)

        listShape = ['xRel']
        s = pd.Series(self.xRelTransect)
        self.dfAdjTrans = pd.DataFrame(s, columns=listShape)
        self.dfAdjTrans['zAdj'] = self.zAdj 

        self.dfAdjTrans = self.dfAdjTrans.sort_values(by ='xRel', ascending=True)

    # ----------------------------------------------------------------------------------------------------------------- #
    def adjustMeas(self, x1, x2, x3):
        xA = self.dfAdjTrans['xRel'].values
        zA = self.dfAdjTrans['zAdj'].values
        
        self.xAdj = []
        self.zAdj = [] 

        idx, xAdj1 = find_nearest(xA, x1)
        zAdj1 = zA[idx]

        self.xAdj.append(xAdj1)
        self.zAdj.append(zAdj1)

        idx, xAdj2 = find_nearest(xA, x2)
        zAdj2 = zA[idx]
        self.xAdj.append(xAdj2)
        self.zAdj.append(zAdj2)

        idx, xAdj3 = find_nearest(xA, x3)
        zAdj3 = zA[idx]
        self.xAdj.append(xAdj3)
        self.zAdj.append(zAdj3)
        
        listShape = ['xRelPoints']
        s = pd.Series(self.xAdj)
        self.dfAdjMeas = pd.DataFrame(s, columns=listShape)
        self.dfAdjMeas['zAdjPoints'] = self.zAdj 

        


        





