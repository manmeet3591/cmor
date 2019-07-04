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

dformat3 = 'atm_6hr_inst'
undscr="_"

tmpdt = '-01-01 00:00'

strtdt = sys.argv[1] + tmpdt
enddt = sys.argv[2] + tmpdt

strtdate = dt.datetime.strptime(strtdt, dformat) 
enddate = dt.datetime.strptime(enddt,dformat)


timedelta=relativedelta(hours=6)

vardf = pd.read_csv('A6hourly_modellev_varlist',skipinitialspace=True)

vardf = vardf.fillna('')

nvar, m = vardf.shape


#idir='/iitm1/cccr/sandeep/iitm-esm-preind-volcano/iitm-esm-cmip6/work/PREINDUSTRIAL-AERO_swap/OUTPUT/ATM/6HR/'
idir='/iitm1/cccr/swapna/PREINDUSTRIAL-AERO/OUTPUT/ATM/6HR'
#idir='/iitm4/cccr/cmip6/Sandeep/PREINDUSTRIAL_1926/OUTPUT/ATM/6HR/'

cmor.setup(inpath='cmip6-cmor-tables/Tables',netcdf_file_action=cmor.CMOR_REPLACE_4)


cmor.dataset_json('common_user_input.json')

    
table='CMIP6_6hrLev.json'

nlev = 64

zlevb = np.linspace(0,1,nlev+1)

zlev = (zlevb[0:nlev]+zlevb[1:nlev+1])*0.5

cmor.load_table(table)

gridnc = Dataset("grid_spec.nc")

lat = gridnc.variables['yta'][::-1]
lon = gridnc.variables['xta'][:]

latb = gridnc.variables['yba'][::-1]
lonb = gridnc.variables['xba'][:]

akbk =  Dataset("akbk.nc")

ak = akbk.variables['coef_a'][:]
bk = akbk.variables['coef_b'][:]
ak_b = akbk.variables['coef_ai'][:]
bk_b = akbk.variables['coef_bi'][:]
ak = ak*1000.
ak_b = ak_b*1000.

ilat = cmor.axis(table_entry= 'latitude',
                 units= 'degrees_north',
                 coord_vals= lat,
                 cell_bounds= latb)


ilon = cmor.axis(table_entry= 'longitude',
                 units= 'degrees_east',
                 coord_vals= lon,
                 cell_bounds= lonb)

ilev = cmor.axis(table_entry= 'standard_hybrid_sigma',
		 units='1',
                 length=nlev, coord_vals=zlev, cell_bounds=zlevb)

error = cmor.zfactor(zaxis_id=ilev,zfactor_name='a', axis_ids=[ilev], zfactor_values = ak, zfactor_bounds=ak_b)
error = cmor.zfactor(zaxis_id=ilev,zfactor_name='b', axis_ids=[ilev], zfactor_values = bk, zfactor_bounds=bk_b)
error = cmor.zfactor(zaxis_id=ilev,zfactor_name='p0',units='Pa',zfactor_values = 1.e5)
#file loop

ddate = strtdate

firsttime = True

while ddate < enddate:

	ddatec = ddate.strftime(dformat2)
	mdatec=sp.check_output(['./datefunc', 'incdate', 'julian '+ddatec+' 0,0,0,6,0,0'])
        yy=mdatec[0:4]; mm=mdatec[4:6]; dd=mdatec[6:8]; hh=mdatec[8:10]; mns=mdatec[10:12]; sc=mdatec[12:14]
	fname = dformat3+undscr+yy+undscr+mm+undscr+dd+undscr+hh+".nc"
	file = idir+"/"+fname
	ddate += timedelta

	nc = Dataset(file)

	print(file)

	if firsttime:

		time = nc.variables['time']
		time_bnds=time[:].tolist()
		time_bnds.append(time_bnds[-1])

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

		axis_ids1 = [itime1,ilev,ilat,ilon]

		axis_ids = [itime1,ilat,ilon]

		#cmor.set_cur_dataset_attribute('frequency','6hr')

		i = 0

		varidnm = []

		while i < nvar:

			varname = vardf.at[i,'varname']

			if varname[0] == '#':
				i += 1
				continue

			var = nc.variables[vardf.at[i,'varname']]

			print(vardf.at[i,'cmorname'],vardf.at[i,'varname'])

		        if vardf.at[i,'cmorname'] == 'ps1':
				ps1id = cmor.zfactor(zaxis_id=ilev, zfactor_name='ps1', 
					axis_ids=axis_ids, units='Pa',)
				print("defined zfactor")
				ps1=var
				varidnm.append([ps1id,varname])
			else:

				vid = cmor.variable(table_entry=vardf.at[i,'cmorname'], units=str(var.units),
					axis_ids=axis_ids1, positive=vardf.at[i,'positive'])
				print("defined variable "+vardf.at[i,'cmorname'])
			
				varidnm.append([vid,varname])

				cmor.set_cur_dataset_attribute('frequency','6hr')

				cmor.write(vid, var[:],time_vals=time[:])
				cmor.write(ps1id, ps1[:],time_vals=time[:],store_with=vid)
			i += 1

		firsttime = False

	else:

		for vidnm in varidnm:

			varname = vidnm[1]

			vid = vidnm[0]

			var = nc.variables[varname]

			time = nc.variables['time']
		
			if varname == "ps":
				ps1 = var
				ps1id = vid
			else:
				cmor.write(vid, var[:],time_vals=time[:])
				cmor.write(ps1id, ps1[:],time_vals=time[:],store_with=vid)

cmor.close()

