import numpy as np 
from analyzeShapeFile import analyzeShapeFileFunctions as analyzeSh 
from scipy.signal import argrelextrema 

# ----------------------------------------------------------------------------------------------------------------- #
class analyzeDischarge(object):
    """
    Object to analyze the discharge through the inlet.  
    """
    def __init__(self, dfTrans, dfPoints): 
        self.dfTrans = dfTrans 
        self.dfPoints = dfPoints  

    
# ----------------------------------------------------------------------------------------------------------------- #
    def defineSections(self):
        idxmaxL = []
        # take the first into account
        idxmax = self.dfTrans.index[0]
        idxmaxL.append(idxmax)
        for i in np.arange(len(self.dfPoints['xRelPoints']) - 1):
            j = i + 1
            xF = self.dfPoints['xRelPoints'][i]
            xL = self.dfPoints['xRelPoints'][j]
            dfSec = self.dfTrans[ (xF <= self.dfTrans['xRel']) & (xL >= self.dfTrans['xRel'])]

            checkMax = np.array(dfSec['zAdj'].values)
            if len(argrelextrema(checkMax, np.greater)[0]) > 0: 
                idxmax = dfSec['zAdj'].idxmax()
                print idxmax, dfSec['zAdj'].loc[idxmax]
                idxmaxL.append(idxmax)
                
            else:
                dx = np.abs(dfSec['xRel'].iloc[0] - dfSec['xRel'].iloc[-1])
                targetX = dfSec['xRel'].iloc[0] + dx*0.5 
                idxArray, value = analyzeSh.find_nearest(dfSec['xRel'].values, targetX)
                indices = list(np.where( dfSec['xRel'] == value )[0])
                idxmax = dfSec.iloc[indices].index.values[0]
                print idxmax, dfSec['zAdj'].loc[idxmax]
                idxmaxL.append(idxmax)
                
        
        # take the last into account
        idxmax = self.dfTrans.index[-1]
        idxmaxL.append(idxmax)
        
        dfListSlices = []
        
        for i in np.arange(len(idxmaxL) - 1): 
            j = i + 1
            idxF = idxmaxL[i]
            idxL = idxmaxL[j]
            print idxF, idxL 
            dfSlice = self.dfTrans.loc[idxF:idxL]
            dfListSlices.append(dfSlice)

        self.sectionInfo = {'points': [p for p in self.dfPoints['xRelPoints'].values], 
                            'sections' : dfListSlices }
            

# ----------------------------------------------------------------------------------------------------------------- #
    def computeArea(self, dfSection, point, level):
        # check section below level - continuous 
        # 0. reindex the df
        indexArray = np.arange(len(dfSection))
        self.dfSlice = dfSection.set_index(indexArray) 
        print self.dfSlice
        
        # 1. check if level is above point level 
        indexP = list(np.where(self.dfSlice['xRel'] == point)[0])
        zlevel = self.dfSlice['zAdj'].iloc[indexP].values[0]   

        if (zlevel < level):
   
            # 2. get points where bottom is below given level 
            self.dfSlice = self.dfSlice[self.dfSlice['zAdj'] < level]
            print self.dfSlice

            # 3. add index values to df
            self.dfSlice['indexV'] = self.dfSlice.index.values

            # 3.1 substract from eachother 
            self.dfSlice['diff'] = self.dfSlice['indexV'].diff()

            # 3.2 find index related to differences larger than 1 
            listLarger = list(self.dfSlice[self.dfSlice['diff'] > 1].index)

            # 4. remove section with larger difference that has larger index values 
            try: 
                del indexRight
            except NameError: 
                pass
            
            listRemaining = []
            for ind in listLarger: 
                if(ind > indexP[0]):
                    indexRight = ind 
                    break
                    listRemaining.append(ind)
                    
            try: 
                indexE = self.dfSlice.index.values[-1] 
                dropList = np.arange(indexRight, indexE + 1)
                self.dfSlice = self.dfSlice.drop(dropList)
            except NameError: 
                print 'No IndexRight' 
                pass 
                
            # 5. remove section with larger difference that has smaller inder values
            if (listRemaining): 
                indexLeft = np.amax(listRemaining)
                indexE = self.dfSlice.index.values[-1]
                self.dfSlice = self.dfSlice.loc[indexLeft:indexE]

            del self.dfSlice['diff']
            del self.dfSlice['indexV']

            print self.dfSlice 
            
            self.dfSlice['deltaZ'] = level - self.dfSlice['zAdj']
            self.dfSlice['deltaX'] = self.dfSlice['xRel'].diff()
            self.dfSlice['t'] = self.dfSlice['deltaZ'].rolling(window=2, center=False).sum()
            self.dfSlice['zSum'] = self.dfSlice['t'].apply(lambda x: x*0.5)
            del self.dfSlice['t']
            self.dfSlice['area'] = self.dfSlice['zSum']*self.dfSlice['deltaX']
            self.area = self.dfSlice['area'].sum()
            print self.dfSlice
            print self.area
        





            
            
