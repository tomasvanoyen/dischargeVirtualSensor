# dischargeVirtualSensor
The code in this repository aims to compute the discharge through a transect based on ADCP measurements. 
The code currently consists of two 'packages' which work independently. One package allows to load, analyse and visualize raw ADCP measurements (flowADCP), while the other aims to compute a the area below a certain free surface level, corresponding to a point on the transect (the point where the ADCP measured the flow velocity). 
An overlying layer is anticipated which combines the depth-averaged velocity with the area at a certain time step to approximate the discharge. 
## some notes: 
1/ loading the raw data takes a while (the for loop going through the files needs to be reconsidered). The pickle files which allow analysis/plotting of data are also provided. 

2/ both packages are still quite under construction 

3/ code depends on pyproj (as non-usual package). Other packages are a.o. pandas, Tkinter, datetime 
