# -*- coding: utf-8 -*-
import numpy as np
from analyzeShapeFile import analyzeShapeFileFunctions as analyzeSh
from analyzeShapeFile import computeDischarge as analyzeDis
import matplotlib.pyplot as plt
import pyproj
from osgeo.osr import SpatialReference, CoordinateTransformation
import itertools

# ----------------------------------------------------------------------------------------------------------------- #
#shDir = 'P:\\16_068-metingZwin\\3_Uitvoering\\metingINBO'
#shDir = '/home/tomas/Documents/thuis/Misc/pythonScripts/rtkShapefiles/metingINBO'
shDir = '/projects/16_068_veld_meting_zwin/metingINBO'
fileName = 'Zwin_8_7_2016'  #extension apparantly is not necessary

switchClicking  = False

# ----------------------------------------------------------------------------------------------------------------- #
# make instance
ash = analyzeSh.analyzeShape(fileName,shDir)

# ----------------------------------------------------------------------------------------------------------------- #
# make scatter plot
#ash.scatterPlotPoints()

if switchClicking: 
    ash.scatterPlotPointsAndChoseROI()

# ----------------------------------------------------------------------------------------------------------------- #
# make x,y,z dataframe of the transect of interest
ash.shapeToDF(switchClicking)

# ----------------------------------------------------------------------------------------------------------------- #
# project points onto line
ash.projectTransectToLine()

# ----------------------------------------------------------------------------------------------------------------- #
# convert GPS coordinates to Lambert coordinates
wgs84 = pyproj.Proj(proj='latlong', datum='WGS84')
wgs84 = pyproj.Proj(init='EPSG:4326')
lamb72New = pyproj.Proj(init='EPSG:31370')
lamb72Old = pyproj.Proj(init='EPSG:31300')  # not the same results as Matlab ..
lamb2008 = pyproj.Proj(init='EPSG:3812')

# ----------------------------------------------------------------------------------------------------------------- #
# check on GPS coordinates measurements
gpsCoor0 = ["""51°22'5.89"N,  3°22'4.01"E""",
            """51°22'5.56"N,  3°22'2.31"E""",
            """51°22'6.22"N,  3°22'4.70"E"""]

gpsCoorPict = ["""51°22'5.9"N,  3°22'4.0"E""",
               """51°22'6.2"N,  3°22'5.35"E""",
               """51°22'6.22"N,  3°22'4.70"E"""]

gpsC = [gpsCoor0, gpsCoorPict]

#->
# ash.plotGPSCoor(gpsC, wgs84, lamb72New)
#-> we consider gpsCoor0 as the ones to go

# ----------------------------------------------------------------------------------------------------------------- #
# Plot the projection of the GPS coordinates on to the transect
gpsC = [gpsCoor0]
ash.plotGPSCoor(gpsC, wgs84, lamb72New)

# ----------------------------------------------------------------------------------------------------------------- #
# find corresponding vertical values
ash.probeVertValues()
ash.plotVertTrans()

# ----------------------------------------------------------------------------------------------------------------- #
# compute angle 
ash.computeAngleY() 

# ----------------------------------------------------------------------------------------------------------------- #
# Adjust transect 
ash.adjustTrans(307, 255)

# ----------------------------------------------------------------------------------------------------------------- #
# Adjust Measurement Points
ash.adjustMeas(135, 175, 225)

# ----------------------------------------------------------------------------------------------------------------- #
# Start computation of discharge 
dis = analyzeDis.analyzeDischarge(ash.dfAdjTrans, ash.dfAdjMeas)

# ----------------------------------------------------------------------------------------------------------------- #
# Compute sections 
dis.defineSections() 

# ----------------------------------------------------------------------------------------------------------------- #
# Compute area for certain free surface level 
level = 3.6
dfSection = dis.sectionInfo['sections'][2]
point = dis.sectionInfo['points'][2]

dis.computeArea(dfSection, point, level)


#####
#####
#####

## 3. get index values of points
#indexArray = dfSlice.index.values 
#indexC = indexArray[-1]
#indexE = indexArray[-1]

# 4. remove the discontinous parts on the right of the section middle 
#while (indexP[0] < indexC): 
#    for i in np.arange(len(indexArray) - 1):
#        j = len(indexArray) - i - 1 
#        diff = indexArray[j] - indexArray[j-1]
#        indexC = indexArray[j]
#        print indexArray[j], indexC
#        if(diff != 1):
#            print 'jump found'
#            indexRight = indexArray[j]
#            break 
#        if(indexP[0] == indexC):
#            print 'finished', indexP[0], indexC
#            break             
#    if(indexRight < (indexE+1)): 
#        dropList = np.arange(indexRight, indexE + 1)
#        dfSlice = dfSlice.drop(dropList)
#        indexE = dfSlice.index.values[-1]    
#        indexArray = dfSlice.index.values
#    else: 
#        print 'huh'
#        pass
#    print dfSlice
#    print indexRight

    

#fig, ax = plt.subplots()
#ax.plot(ash.dfAdjTrans['xRel'], ash.dfAdjTrans['zAdj'])
#ax.scatter(ash.xRelTransect, ash.dfTransect['z-coor'].values)
#ax.scatter(ash.xAdj, ash.zAdj, c ='red')
#plt.show()
    

        




