#! /usr/bin/env python

from netCDF4 import Dataset
from netCDF4 import MFDataset
import cmor
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import subprocess as sp
import sys


dformat = '%Y-%m-%d %H:%M'

dformat2 = '%Y%m%d%H%M%S'

dformat3 = 'ocean_%Y_%m_monmean.nc'

tmpdt = '-01-01 00:00'

strtdt = sys.argv[1] + tmpdt
enddt = sys.argv[2] + tmpdt

strtdate = dt.datetime.strptime(strtdt, dformat)
enddate = dt.datetime.strptime(enddt,dformat)

print(strtdate)
print(enddate)

timedelta=relativedelta(months=1)

vardf = pd.read_csv('Omon_3d_varlist',skipinitialspace=True)

vardf = vardf.fillna('')

nvar, m = vardf.shape


idir='/iitm1/cccr/sandeep/iitm-esm-preind-volcano/iitm-esm-cmip6/work/PREINDUSTRIAL-AERO_swap/OUTPUT/OCN/'
#idir='/iitm1/cccr/swapna/PREINDUSTRIAL-AERO/OUTPUT/OCN/'
#idir='/iitm4/cccr/cmip6/Sandeep/PREINDUSTRIAL_1926/OUTPUT/OCN/'

cmor.setup(inpath='cmip6-cmor-tables/Tables',netcdf_file_action=cmor.CMOR_REPLACE_4)


cmor.dataset_json('common_user_input.json')

    
tables = []
a = cmor.load_table("CMIP6_grids.json")
tables.append(a)
tables.append(cmor.load_table("CMIP6_Omon.json"))

cmor.set_table(tables[0])

gridnc = Dataset("grid_spec.nc")

nx=360
ny=200
nz=50

x = range(360)
y = range(200)
#x = gridnc.variables['gridlon_t'][:]
#y = gridnc.variables['gridlat_t'][:]



lat = gridnc.variables['geolat_t'][:]
y=lat[:,100]
lon = gridnc.variables['geolon_t'][:]
x=lon[180,:]
dep = gridnc.variables['zt']
tmp = gridnc.variables['zw'][:]

dep_bnds = tmp.tolist()

dep_bnds.insert(0,0.)


ilat = cmor.axis(table_entry= 'y_deg',
                 units= 'degrees_N',
                 coord_vals=y)
print('defined y')

ilon = cmor.axis(table_entry= 'x_deg',
                 units= 'degrees_E',
                 coord_vals=x)
print('defined x')


grid_id=cmor.grid( [ilat,ilon], lat, lon)


cmor.set_table(tables[1])

idep = cmor.axis(table_entry= 'depth_coord',
                 units='m',
                 coord_vals=dep[:],
		 cell_bounds=dep_bnds)



#file loop

ddate = strtdate

firsttime = True

while ddate < enddate:

	ddatec = ddate.strftime(dformat2)
	mdatec=sp.check_output(['./datefunc', 'incdatemid', 'julian '+ddatec+' 0,1,0,0,0,0'])
	mdate = dt.datetime.strptime(mdatec.strip(), dformat2)
	file = idir+mdate.strftime(dformat3)
	print(file)
	ddate += timedelta
	nc = Dataset(file)

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

		axis_ids1 = [itime,idep,grid_id]

		axis_ids = [itime,idep,grid_id]

		i = 0

		varidnm = []

		while i < nvar:

			varname = vardf.at[i,'varname']

			if varname[0] == '#':
				i += 1
				continue

			var = nc.variables[vardf.at[i,'varname']]

			print(vardf.at[i,'cmorname'],vardf.at[i,'varname'])

			units=str(var.units)
	
			if vardf.at[i,'units'] != "":
				units=vardf.at[i,'units']

			vid = cmor.variable(table_entry=vardf.at[i,'cmorname'], units=units,
					axis_ids=axis_ids, positive=vardf.at[i,'positive'],missing_value=var.missing_value)
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

