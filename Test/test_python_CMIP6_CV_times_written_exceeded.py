# Irf this example is not executed from the directory containing the
# CMOR code, please first complete the following steps:
#
#   1. In any directory, create 'Tables/', 'Test/' and 'CMIP6/' directories.
#
#   2. Download
#      https://github.com/PCMDI/cmor/blob/master/TestTables/CMIP6_Omon.json
#      and https://github.com/PCMDI/cmor/blob/master/TestTables/CMIP6_CV.json
#      to the 'Tables/' directory.
#
#   3. Download
#      https://github.com/PCMDI/cmor/blob/master/Test/<filename>.json
#      to the 'Test/' directory.

import cmor
import numpy
import unittest
import sys
import os
import tempfile
import base_CMIP6_CV


class TestCase(base_CMIP6_CV.BaseCVsTest):

    def testCMIP6(self):

        # -------------------------------------------
        # Try to write data with the number of times passed 
        # being greater than the length of the time axis
        # -------------------------------------------
        try:
            cmor.setup(inpath='Tables', 
                       netcdf_file_action=cmor.CMOR_REPLACE, 
                       logfile=self.tmpfile)
            cmor.dataset_json("Test/CMOR_input_example.json")

            # ------------------------------------------
            # load Omon table and create zhalfo variable
            # ------------------------------------------
            Time = [0.5, 1.5]
            bnds_time = [[0, 1], [1, 2]]
            lon_coords = [0]
            lat_coords = [80]
            lon_vertices = [-1, 1]
            lat_vertices = [79, 81]
            olev_val = [5000., 3000., 2000., 1000.]
            olev_bnds = [5000., 3000., 2000., 1000., 0]
            zhalfo_data = [274., 274., 274., 274.]

            cmor.load_table("CMIP6_Omon.json")
            itime = cmor.axis(table_entry="time", units='months since 1980',
                              length=2,
                              coord_vals=Time,
                              cell_bounds=bnds_time)
            ilat  = cmor.axis(table_entry="latitude", units='degrees_north',
                              coord_vals=lat_coords,
                              cell_bounds=lat_vertices)
            ilon  = cmor.axis(table_entry="longitude", units='degrees_east',
                              coord_vals=lon_coords,
                              cell_bounds=lon_vertices)
            idep  = cmor.axis(table_entry="depth_coord_half", units='m',
                              coord_vals=olev_val,
                              cell_bounds=olev_bnds)
            ivar = cmor.variable(
                table_entry="zhalfo",
                axis_ids=[itime, ilat, ilon, idep],
                units='m')

            for _ in range(3):
                cmor.write(ivar, zhalfo_data, ntimes_passed=1)
                
            self.delete_files += [cmor.close(ivar, True)]
            cmor.close()
        except BaseException:
            pass
        self.assertCV('The number of times passed combined with the '
                      'number of times written must not exceed '
                      'the length of the time axis')

if __name__ == '__main__':
    unittest.main()
