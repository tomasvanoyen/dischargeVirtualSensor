import shapefile
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

# option 1
shDir = 'P:\\16_068-metingZwin\\3_Uitvoering\\metingINBO'
fileName = 'Zwin_8_7_2016'  #extension apparantly is not necessary
fn = os.path.join(shDir,fileName)
sf = shapefile.Reader(fn)

# option 2
fileName = 'Zwin_8_7_2016.shp'
fn = os.path.join(shDir,fileName)
myshp = open(fn, "rb")

fileName = 'Zwin_8_7_2016.dbf'
fn = os.path.join(shDir,fileName)
mydbf = open(fn, "rb")

sf = shapefile.Reader(shp=myshp, dbf=mydbf)

# get a list of the shapefile's geometry
shapes = sf.shapes()
print len(shapes)

# check the attributes of the shape records
for name in dir(shapes[3]):
    if not name.startswith('__'):
        print name

# for each 'shape' the x,y coordinate is set in shape.points
# e.g. shapes[0].points[0]
print shapes[0].points[0]

# catch the different fields in the shapefile
fields = sf.fields
print fields

# get list of shapefile's records
records = sf.records()
print len(records)

# get both geometry and records simultaneously
shapeRecs = sf.shapeRecords()
print len(shapeRecs)

# so, getting x,y and z can be done as follows:
# option 1
x, y, z = records[0][2], records[0][3], records[0][4]
print x,y,z
# option 2
x, y, z = shapes[0].points[0][0], shapes[0].points[0][1], shapeRecs[0].record[4]
print x,y,z

# Make scatter plot of x and y
xco = []
yco = []
for i in np.arange(len(shapes)):
    x,y = records[i][2], records[i][3]
    xco.append(x)
    yco.append(y)

fig, ax = plt.subplots()
#ax.scatter(xco,yco)

# make DataFrame of x, y, z

listShape = ['x-coor', 'y-coor', 'z-coor']
coordinates = []
for i in np.arange(len(shapes)):
    x, y, z = records[i][2], records[i][3], records[i][4]
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
print dfCoor.head()

dfInlaat = dfCoor[dfCoor['y-coor']>229160]

#ax.scatter(dfInlaat['x-coor'],dfInlaat['y-coor'],c='r')

slope, intercept, r_value, p_value, std_err = stats.linregress(dfInlaat['x-coor'], dfInlaat['y-coor'])
p = np.poly1d(np.polyfit(dfInlaat['x-coor'], dfInlaat['y-coor'],1))
lijn = p(dfInlaat['x-coor'])

#ax.plot(dfInlaat['x-coor'], lijn)

# project points on to the line
d = -1.0/slope
c = dfInlaat['y-coor'].values - d*dfInlaat['x-coor'].values
xe = (intercept - c) / (d - slope)
ye = slope*xe + intercept

#ax.scatter(xe,ye,c='g')
#ax.axis('equal')

xd = np.sqrt(np.multiply(xe,xe) + np.multiply(ye,ye))
plt.plot(xd, dfInlaat['z-coor'].values)
plt.show()




