"""
Auxiliary script to load the data from an ADCP measurement.
Input files are *.v* or *.a* and are output files from AquaPro.
Raw data is loaded and saved as pickle file for further analyses as pandas.DataFrame.

Author: Tomas Van Oyen
Last changes: 19-01-2017
contact: tomas.vanoyen@mow.vlaanderen.be
"""

import pandas as pd
import Tkinter, tkFileDialog
import ADCP.loadADCP.loadFunctions as adcpLoad
import numpy as np

# --
# A GUI tool is nice but can be annoying
# hence the following switch

switchGUI = True

if switchGUI:
    root = Tkinter.Tk()
    dataDirLoad = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Select the folder with ADCP data')
    if len(dataDirLoad ) > 0:
        print '============================================='
        print "You chose %s" % dataDirLoad

    root = Tkinter.Tk()
    dataDirSave = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Select the folder to save pickle file(s)')
    if len(dataDirSave ) > 0:
        print '============================================='
        print "You chose %s" % dataDirSave

else:
    # TODO: switch for windows / linux
    operSystem = 'windows'
    if(operSystem == 'windows'):
        dataDirLoad = "P:/16_068-metingZwin/3_Uitvoering/meting30062016/positie 1/convert"
        dataDirSave = "P:/16_068-metingZwin/3_Uitvoering/analyse/positie 1"
    else:
        pass

print '============================================='
print "Please indicate which files you want to load and save as pickle. "
print "This can take while, so"
print "  (1) take your precautions" 
print "  (2) limit the amount of parameters to load and save"
print '============================================='

charComp = raw_input('Do you want to load and save the measurement characteristics (yes or no!): ').lower()
v1Comp = raw_input('Do you want to load and save the v1-component (yes or no!): ').lower()
v2Comp = raw_input('Do you want to load and save the v2-component (yes or no!): ').lower()
v3Comp = raw_input('Do you want to load and save the v3-component (yes or no!): ').lower()

a1Comp = raw_input('Do you want to load and save the a1-component (yes or no!): ').lower()
a2Comp = raw_input('Do you want to load and save the a2-component (yes or no!): ').lower()
a3Comp = raw_input('Do you want to load and save the a3-component (yes or no!): ').lower()

# --
# collect requests
vComp = []
vComp.append((v1Comp, 'v1'))
vComp.append((v2Comp, 'v2'))
vComp.append((v3Comp, 'v3'))

aComp = []
aComp.append((a1Comp, 'a1'))
aComp.append((a2Comp, 'a2'))
aComp.append((a3Comp, 'a3'))

# --
# initialize instance
dataADCP = adcpLoad.loadData(dataDirLoad)

# --
# initialize dictionaries
dataADCP.initializeDict()

# --
# Read the time stamps of the measurements
print 'Reading the measurement timestamps'
dataADCP.openDataLog()
dataADCP.makeTimeSeries()

# --
# read header file and take the measured distances from the ADCP head
print "Read distance from head"
dataADCP.openHeader()
dataADCP.readDistanceMeasPoints()

# --
# Read the time stamps where a measurement error occured
print 'Reading the error timestamps'
dataADCP.openErrorLog()
dataADCP.makeErrorTimeSeries()

# --
# make pandas DataFrame of errorSeries
dfErr = pd.DataFrame(dataADCP.errorValue, index = dataADCP.errorTimeSeries, columns = ['Error'])

# --
# remove duplicates in dfErr
dfErr['index'] = dfErr.index
dfErr.drop_duplicates(cols = 'index', take_last=False, inplace=True)
del dfErr['index']

if charComp == 'yes':
    # --
    # Read the characteristics of the measurement in execution
    # 1. pressure
    # 2. direction of the flow
    # 3. ...

    print 'Reading in measurement characteristics'
    dataADCP.openDataLog()
    dataADCP.readADCPcharacteristics()
    listADCPchar = ['Pressure', 'Direction', 'errCode', 'statCode', 'cSound', 'Pitch', 'Roll', 'Temp', 'Log1', 'Log2']

    # --
    # make pandas DataFrame of all measurement characteristics
    dfChar = pd.DataFrame(dataADCP.charSeries, index=dataADCP.timeSeries, columns=listADCPchar)

    # --
    # concatenate the results with the error timeSeries
    result = pd.concat([dfChar, dfErr], axis=1)

    # --
    # drop the part where the measurements are with error
    result = result[result.Error != 1]

    # --
    # write the result ot pickle file for easy read lateron
    adcpLoad.make_sure_path_exists(dataDirSave)
    fileName = dataDirSave + '/' + 'charCompTotal.pkl'
    result.to_pickle(fileName)
    print "Writing measurement characteristics to: ", fileName

else:
    print 'measurement characteristics not read'

# -----------------------------------------

for i in np.arange(len(vComp)):
    comp = vComp[i][0]
    v = vComp[i][1]

    if comp == 'yes':

        # --
        # read v component of the velocity
        print 'Reading %s-component of the velocity' % v
        dataADCP.openVel(v)
        dataADCP.readVel(v)

        # --
        # make pandas DataFrame of v component of the velocity
        print "Make pandas DataFrame"
        dfVel = pd.DataFrame(dataADCP.Vel[v], index = dataADCP.timeSeries, columns = dataADCP.distanceMeasPoints)

        # --
        # concatenate the results with the error timeSeries
        result = pd.concat([dfVel, dfErr], axis=1)

        # --
        # drop the part where the measurements are with error
        result = result[result.Error != 1]

        # --
        # write the result ot pickle file for easy read lateron
        adcpLoad.make_sure_path_exists(dataDirSave)
        fN = '%sCompTotal.pkl' % v
        fileName = dataDirSave + '/' + fN
        result.to_pickle(fileName)
        print "Writing %s-component to: " % v, fileName

    else:
        print '%s-component not read' % v

# -----------------------------------------

for i in np.arange(len(aComp)):
    comp = aComp[i][0]
    a = aComp[i][1]

    if comp == 'yes':
        # --
        # read A component of the velocity
        print 'Reading %s-component of ADCP' % a

        dataADCP.openAmpl(a)
        dataADCP.readAmpl(a)

        # --
        # make pandas DataFrame of A component of the velocity
        print "Make pandas DataFrame"
        dfAmp = pd.DataFrame(dataADCP.Ampl[a], index=dataADCP.timeSeries, columns=dataADCP.distanceMeasPoints)

        # --
        # concatenate the results with the error timeSeries
        result = pd.concat([dfAmp, dfErr], axis=1)

        # --
        # drop the part where the measurements are with error
        result = result[result.Error != 1]

        # --
        # write the result ot pickle file for easy read lateron
        adcpLoad.make_sure_path_exists(dataDirSave)
        fn = '%sCompTotal.pkl' % a
        fileName = dataDirSave + '/' + fN
        result.to_pickle(fileName)
        print "Writing %s-component to: " % a, fileName

    else:
        print '%s-component not read' % a

# #-----------------------------------------
# END OF THE WORLD
#
# if v1Comp == 'yes':
#     # --
#     # read V1 component of the velocity
#     print 'Reading v1-component of the velocity'
#     dataADCP.openVel('v1')
#     dataADCP.readVel('v1')
#
#     # --
#     # make pandas DataFrame of V1 component of the velocity
#     print "Make pandas DataFrame"
#     dfVel = pd.DataFrame(dataADCP.Vel['v1'], index = dataADCP.timeSeries, columns = dataADCP.distanceMeasPoints)
#
#     # --
#     # concatenate the results with the error timeSeries
#     result = pd.concat([dfVel, dfErr], axis=1)
#
#     # --
#     # drop the part where the measurements are with error
#     result = result[result.Error != 1]
#
#     # --
#     # write the result ot pickle file for easy read lateron
#     adcpLoad.make_sure_path_exists(dataDirSave)
#     fileName = dataDirSave + '/' + 'v1CompTotal.pkl'
#     result.to_pickle(fileName)
#     print "Writing v1-component to: ", fileName
#
# else:
#     print 'v1-component not read'
#
#
# if v2Comp == 'yes':
#     # --
#     # read V2 component of the velocity
#     print 'Reading v2-component of the velocity'
#     dataADCP.openVel('v2')
#     dataADCP.readVel('v2')
#
#     # --
#     # make pandas DataFrame of V2 component of the velocity
#     print "Make pandas DataFrame"
#     dfVel = pd.DataFrame(dataADCP.Vel['v2'], index = dataADCP.timeSeries, columns = dataADCP.distanceMeasPoints)
#
#     # --
#     # concatenate the results with the error timeSeries
#     result = pd.concat([dfVel, dfErr], axis=1)
#
#     # --
#     # drop the part where the measurements are with error
#     result = result[result.Error != 1]
#
#     # --
#     # write the result ot pickle file for easy read lateron
#     adcpLoad.make_sure_path_exists(dataDirSave)
#
#     fileName = dataDirSave + '/' + 'v2CompTotal.pkl'
#     result.to_pickle(fileName)
#     print "Writing v2-component to: ", fileName
#
# else:
#     print 'v2-component not read'
#
# if v3Comp == 'yes':
#     # --
#     # read V3 component of the velocity
#     print 'Reading v3-component of the velocity'
#     dataADCP.openVel('v3')
#     dataADCP.readVel('v3')
#
#     # --
#     # make pandas DataFrame of V3 component of the velocity
#     print "Make pandas DataFrame"
#     dfVel = pd.DataFrame(dataADCP.Vel['v3'], index = dataADCP.timeSeries, columns = dataADCP.distanceMeasPoints)
#
#     # --
#     # concatenate the results with the error timeSeries
#     result = pd.concat([dfVel, dfErr], axis=1)
#
#     # --
#     # drop the part where the measurements are with error
#     result = result[result.Error != 1]
#
#     # --
#     # write the result ot pickle file for easy read lateron
#     adcpLoad.make_sure_path_exists(dataDirSave)
#
#     fileName = dataDirSave + '/' + 'v3CompTotal.pkl'
#     result.to_pickle(fileName)
#     print "Writing v3-component to: ", fileName
#
# else:
#     print 'v3-component not read'
#
# ----------------------------------------------------
#
# if a1Comp == 'yes':
#     # --
#     # read A1 component of the velocity
#     print 'Reading a1-component of ADCP'
#
#     dataADCP.openAmpl('a1')
#     dataADCP.readAmpl('a1')
#
#     # --
#     # make pandas DataFrame of A2 component of the velocity
#     print "Make pandas DataFrame"
#     dfAmp = pd.DataFrame(dataADCP.Ampl['a1'], index=dataADCP.timeSeries, columns=dataADCP.distanceMeasPoints)
#
#     # --
#     # concatenate the results with the error timeSeries
#     result = pd.concat([dfAmp, dfErr], axis=1)
#
#     # --
#     # drop the part where the measurements are with error
#     result = result[result.Error != 1]
#
#     # --
#     # write the result ot pickle file for easy read lateron
#     adcpLoad.make_sure_path_exists(dataDirSave)
#     fileName = dataDirSave + '/' + 'a1CompTotal.pkl'
#     result.to_pickle(fileName)
#     print "Writing a1-component to: ", fileName
#
# else:
#     print 'a1-component not read'
#
# if a2Comp == 'yes':
#     # --
#     # read A2 component of the velocity
#     print 'Reading a2-component of ADCP'
#
#     dataADCP.openAmpl('a2')
#     dataADCP.readAmpl('a2')
#
#     # --
#     # make pandas DataFrame of A2 component of the velocity
#     print "Make pandas DataFrame"
#     dfAmp = pd.DataFrame(dataADCP.Ampl['a2'], index=dataADCP.timeSeries, columns=dataADCP.distanceMeasPoints)
#
#     # --
#     # concatenate the results with the error timeSeries
#     result = pd.concat([dfAmp, dfErr], axis=1)
#
#     # --
#     # drop the part where the measurements are with error
#     result = result[result.Error != 1]
#
#     # --
#     # write the result ot pickle file for easy read lateron
#     adcpLoad.make_sure_path_exists(dataDirSave)
#     fileName = dataDirSave + '/' + 'a2CompTotal.pkl'
#     result.to_pickle(fileName)
#     print "Writing a2-component to: ", fileName
#
# else:
#     print 'a2-component not read'
#
# if a3Comp == 'yes':
#     # --
#     # read A3 component of the velocity
#     print 'Reading a3-component of ADCP'
#
#     dataADCP.openAmpl('a3')
#     dataADCP.readAmpl('a3')
#
#     # --
#     # make pandas DataFrame of A2 component of the velocity
#     print "Make pandas DataFrame"
#     dfAmp = pd.DataFrame(dataADCP.Ampl['a3'], index=dataADCP.timeSeries, columns=dataADCP.distanceMeasPoints)
#
#     # --
#     # concatenate the results with the error timeSeries
#     result = pd.concat([dfAmp, dfErr], axis=1)
#
#     # --
#     # drop the part where the measurements are with error
#     result = result[result.Error != 1]
#
#     # --
#     # write the result ot pickle file for easy read lateron
#     adcpLoad.make_sure_path_exists(dataDirSave)
#     fileName = dataDirSave + '/' + 'a3CompTotal.pkl'
#     result.to_pickle(fileName)
#     print "Writing a3-component to: ", fileName
#
# else:
#     print 'a3-component not read'
