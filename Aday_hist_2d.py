#! /usr/bin/env python

from netCDF4 import Dataset
from netCDF4 import MFDataset
import cmor
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import subprocess as sp
import sys
from strftime_1900 import strftime_1900

dformat = '%Y-%m-%d %H:%M'

dformat2 = '%Y%m%d%H%M%S'

dformat3 = 'atm_day_%Y_%m_%d_%H.nc'

tmpdt = '-01-01 00:00'

strtdt = sys.argv[1] + tmpdt
enddt = sys.argv[2] + tmpdt

strtdate = dt.datetime.strptime(strtdt, dformat)
enddate = dt.datetime.strptime(enddt,dformat)

print(strtdate)
print(enddate)

timedelta=relativedelta(days=1)

vardf = pd.read_csv('Aday_2d_varlist',skipinitialspace=True)

vardf = vardf.fillna('')

nvar, m = vardf.shape


#idir='/iitm1/cccr/sandeep/iitm-esm-preind-volcano/iitm-esm-cmip6/work/PREINDUSTRIAL-AERO_swap/OUTPUT/ATM/DAY/'
#idir='/iitm1/cccr/swapna/PREINDUSTRIAL-AERO/OUTPUT/ATM/DAY/'
#idir='/iitm4/cccr/cmip6/Sandeep/PREINDUSTRIAL_1926/OUTPUT/ATM/DAY/'
idir='/iitm4/cccr/cmip6/Sandeep/Historical_cmip6/OUTPUT/ATM/DAY/'

cmor.setup(inpath='cmip6-cmor-tables/Tables',netcdf_file_action=cmor.CMOR_REPLACE_4)


cmor.dataset_json('common_user_input.json')

    
table='CMIP6_day.json'

cmor.load_table(table)

gridnc = Dataset("grid_spec.nc")

lat = gridnc.variables['yta'][::-1]
lon = gridnc.variables['xta'][:]

latb = gridnc.variables['yba'][::-1]
lonb = gridnc.variables['xba'][:]


ilat = cmor.axis(table_entry= 'latitude',
                 units= 'degrees_north',
                 coord_vals= lat,
                 cell_bounds= latb)


ilon = cmor.axis(table_entry= 'longitude',
                 units= 'degrees_east',
                 coord_vals= lon,
                 cell_bounds= lonb)

#file loop

ddate = strtdate

firsttime = True

while ddate < enddate:

	ddatec = strftime_1900(ddate, dformat2)
	#ddatec = ddate.strftime(dformat2)
	mdatec=sp.check_output(['./datefunc', 'incdatemid', 'julian '+ddatec+' 0,0,1,0,0,0'])
	mdate = dt.datetime.strptime(mdatec.strip(), dformat2)
	file = idir+strftime_1900(mdate, dformat3)
	#file = idir+mdate.strftime(dformat3)
	ddate += timedelta

	nc = Dataset(file)

	print(file)

	if firsttime:

		time = nc.variables['time']
		time_bnds=nc.variables['time_bounds'][:]

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

		axis_ids = [itime,ilat,ilon]

		i = 0

		varidnm = []

		while i < nvar:

			varname = vardf.at[i,'varname']

			if varname[0] == '#':
				i += 1
				continue

			var = nc.variables[vardf.at[i,'varname']]

			print(vardf.at[i,'cmorname'],vardf.at[i,'varname'])

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
			time_bnds=nc.variables['time_bounds'][:]

			cmor.write(vid, var[:],time_vals=time,time_bnds=time_bnds)

cmor.close()

