#! /usr/bin/env python

from netCDF4 import Dataset
from netCDF4 import MFDataset
import cmor
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import subprocess as sp
import sys
import numpy as np

dformat = '%Y-%m-%d %H:%M'

dformat2 = '%Y%m%d%H%M%S'

#dformat3 = 'atm_day_%Y_%m_%d_%H_plev.nc'
dformat3 = 'temp_%Y%m%d00.nc'

#tmpdt = '-01-01 00:00'
tmpdt = ' 00:00'

strtdt = sys.argv[1] + tmpdt
enddt = sys.argv[2] + tmpdt

strtdate = dt.datetime.strptime(strtdt, dformat) 
enddate = dt.datetime.strptime(enddt,dformat)

timedelta=relativedelta(days=1)

vardf = pd.read_csv('Aday_3d_varlist',skipinitialspace=True)

vardf = vardf.fillna('')

nvar, m = vardf.shape


#idir='/iitm1/cccr/sandeep/iitm-esm-preind-volcano/iitm-esm-cmip6/work/PREINDUSTRIAL-AERO_swap/OUTPUT/ATM/DAY/'
#idir='/iitm1/cccr/swapna/PREINDUSTRIAL-AERO/OUTPUT/ATM/DAY/'
#idir='/iitm4/cccr/cmip6/Sandeep/PREINDUSTRIAL_1926/OUTPUT/ATM/DAY/'
idir='/iitm2/cccr-res/msingh/cmor_ncap/cmor_input/'



cmor.setup(inpath='cmip6-cmor-tables/Tables',netcdf_file_action=cmor.CMOR_REPLACE_4)


cmor.dataset_json('common_user_input.json')

    
table='CMIP6_day.json'

cmor.load_table(table)

gridnc = Dataset("/iitm2/cccr-res/msingh/cmor_ncap/cmor_input/temp_2015010100.nc")

lat = gridnc.variables['latitude'][::-1]
lon = gridnc.variables['longitude'][:]
#print(lat)
#print(lon)


latb = np.zeros((lat.shape[0]+1))
lonb = np.zeros((lon.shape[0]+1))

dellat = (lat[1] - lat[0])/2
dellon = (lon[1] - lon[0])/2

latb[0] = lat[0] - dellat
lonb[0] = lon[0] - dellon

dellat = (lat[lat.shape[0]-1] - lat[lat.shape[0]-2])/2
dellon = (lon[lon.shape[0]-1] - lon[lon.shape[0]-2])/2

latb[lat.shape[0]] = lat[lat.shape[0]-1] + dellat
lonb[lon.shape[0]] = lon[lon.shape[0]-1] + dellon
def make_bounds(data):
	data_b = np.zeros((data.shape[0]+1))
	if data.shape[0] == 1:
		data_b[0] = 0.0
		data_b[1] = 2* data[0]
	else:
		deldata = (data[1] - data[0])/2
		data_b[0] = data[0] - deldata

		deldata = (data[data.shape[0]-1] - data[data.shape[0]-2])/2
		data_b[data.shape[0]] = data[data.shape[0]-1] + deldata

		for i in range(data.shape[0]-1):
			data_b[i+1] = (data[i] + data[i+1])/2
	return data_b 


for i in range(lat.shape[0]-1):
	latb[i+1] = (lat[i] + lat[i+1])/2
for j in range(lon.shape[0]-1):
	lonb[j+1] = (lon[j] + lon[j+1])/2

#print(lon)
#print(lonb)
#print(sys.exit)
#latb = gridnc.variables['yba'][::-1]
#lonb = gridnc.variables['xba'][:]


#print(lonb)
#print(lon[:]<lonb[1:])
#print(lonb[299])
#sys.exit()
plevs=[100000., 97500., 95000., 92500., 90000., 87500., 85000., 82500., 80000., 77500., 75000., 70000., 65000., 60000., 55000., 50000., 45000., 40000., 35000., 30000., 25000., 22500., 20000., 17500., 15000., 12500., 10000.]

ilat = cmor.axis(table_entry= 'latitude',
                 units= 'degrees_north',
                 coord_vals= lat,
                 cell_bounds= latb)


ilon = cmor.axis(table_entry= 'longitude',
                 units= 'degrees_east',
                 coord_vals= lon,
                 cell_bounds= lonb)

iplev27 = cmor.axis(table_entry= 'plev27',
         units= 'Pa',
	 coord_vals=plevs)

#file loop

ddate = strtdate

firsttime = True

while ddate < enddate:

	ddatec = ddate.strftime(dformat2)
	mdatec=sp.check_output(['./datefunc', 'incdatemid', 'julian '+ddatec+' 0,0,1,0,0,0'])
	mdate = dt.datetime.strptime(mdatec.strip(), dformat2)
	file = idir+mdate.strftime(dformat3)
	print(file)
	ddate += timedelta

	nc = Dataset(file)

	print(file)

	if firsttime:

		time = nc.variables['time']

		#print(time)
		#time_bnds=nc.variables['time_bounds'][:]
		time_bnds = make_bounds(time)
		print("Test")
		print(time_bnds, time)

	#	itime = cmor.axis(table_entry= 'time',
	#			units= time.units,
	#			coord_vals= time[:],
	#			cell_bounds= time_bnds)

	#	itime1 = cmor.axis(table_entry= 'time1',
        #          		units= time.units,
        #          		coord_vals= time[:])

		itime = cmor.axis(table_entry= 'time',
				units= time.units)

		itime1 = cmor.axis(table_entry= 'time1',
                  		units= time.units)

		axis_ids1 = [itime,ilat,ilon]

		axis_ids = [itime,iplev27,ilat,ilon]

		i = 0

		varidnm = []

		while i < nvar:

			varname = vardf.at[i,'varname']

			if varname[0] == '#':
				i += 1
				continue

			var = nc.variables[vardf.at[i,'varname']]

			print(vardf.at[i,'cmorname'],vardf.at[i,'varname'])

			if vardf.at[i,'cmorname'] == 'psl':
				vid = cmor.variable(table_entry=vardf.at[i,'cmorname'], units=str(var.units),
					axis_ids=axis_ids1, positive=vardf.at[i,'positive'])

				varidnm.append([vid,varname])


				#cmor.write(vid, var[:])
				cmor.write(vid, var[:],time_vals=time,time_bnds=time_bnds)

				i += 1
				continue

			vid = cmor.variable(table_entry=vardf.at[i,'cmorname'], units=str(var.units),
					axis_ids=axis_ids, positive=vardf.at[i,'positive'])
			varidnm.append([vid,varname])

			#cmor.write(vid, var[:])
			cmor.write(vid, var[:],time_vals=time,time_bnds=time_bnds)
			i += 1

		firsttime = False

	else:

		for vidnm in varidnm:

			varname = vidnm[1]

			vid = vidnm[0]

			var = nc.variables[varname]

			time = nc.variables['time']
			time_bnds = make_bounds(time) 
			print("Test")
			print(time_bnds, time)

			cmor.write(vid, var[:],time_vals=time,time_bnds=time_bnds)

cmor.close()

