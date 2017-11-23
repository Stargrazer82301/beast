import os.path
import filecmp

import numpy as np
import h5py

from astropy.utils.data import download_file
from astropy.tests.helper import remote_data
from astropy import units

from beast.physicsmodel.stars import isochrone
from beast.physicsmodel.stars import stellib
from beast.physicsmodel.stars.isochrone import ezIsoch
from beast.physicsmodel.model_grid import make_spectral_grid

@remote_data
def test_make_kurucz_tlusty_spectral_grid():

    # download the needed files
    url_loc = 'http://www.stsci.edu/~kgordon/beast/'
    kurucz_fname_dld = download_file('%s%s'%(url_loc,'kurucz2004.grid.fits'))
    tlusty_fname_dld = download_file('%s%s'%(url_loc,'tlusty.lowres.grid.fits'))
    filter_fname_dld = download_file('%s%s'%(url_loc,'filters.hd5'))
    iso_fname_dld = download_file('%s%s'%(url_loc,
                                          'beast_example_phat_iso_new.csv'))
    #kurucz_fname_dld = '/tmp/kurucz2004.grid.fits.tmp'
    #tlusty_fname_dld = '/tmp/tlusty.lowres.grid.fits.tmp'
    #filter_fname_dld = '/tmp/filters.hd5.tmp'

    # rename files to have the correct extensions
    kurucz_fname = '%s.fits'%(kurucz_fname_dld)
    os.rename(kurucz_fname_dld, kurucz_fname)
    tlusty_fname = '%s.fits'%(tlusty_fname_dld)
    os.rename(tlusty_fname_dld, tlusty_fname)
    filter_fname = '%s.hd5'%(filter_fname_dld)
    os.rename(filter_fname_dld, filter_fname)
    iso_fname = '%s.csv'%(iso_fname_dld)
    os.rename(iso_fname_dld, iso_fname)
    
    # download cached version of spectral grid
    filename = download_file('%s%s'%(url_loc,
                                     'beast_example_phat_spec_grid.hd5'))
    #filename = '/tmp/beast_example_phat_spec_grid_cache.hd5.tmp'
    
    hdf_cache = h5py.File(filename, 'r')
    
    ################
    # generate a the same spectral grid from the code
    
    # read in the cached isochrones
    oiso = ezIsoch(iso_fname)

    # define the distance
    distanceModulus = 24.47 * units.mag
    dmod = distanceModulus.value
    distance = 10 ** ( (dmod / 5.) + 1 ) * units.pc

    # define the spectral libraries to use
    osl = stellib.Tlusty(filename=tlusty_fname) \
        + stellib.Kurucz(filename=kurucz_fname)
    
    # Add in he 
    filters = ['HST_WFC3_F275W','HST_WFC3_F336W','HST_ACS_WFC_F475W',
               'HST_ACS_WFC_F814W', 'HST_WFC3_F110W','HST_WFC3_F160W']
    add_spectral_properties_kwargs = dict(filternames=filters)

    spec_fname = '/tmp/beast_example_phat_spec_grid.hd5'
    spec_fname, g = make_spectral_grid('test', oiso, osl=osl, distance=distance,
                                       spec_fname=spec_fname,
                                       filterLib=filter_fname,
         add_spectral_properties_kwargs=add_spectral_properties_kwargs)
    

    # open the hdf file with the specral grid
    hdf_new = h5py.File(spec_fname, 'r')

    # go through the file and check if it is exactly the same
    for sname in hdf_cache.keys():
        if isinstance(hdf_cache[sname], h5py.Dataset):
            cvalue = hdf_cache[sname]
            cvalue_new = hdf_new[sname]
            if cvalue.dtype.isbuiltin:
                np.testing.assert_equal(cvalue.value, cvalue_new.value,
                                        'testing %s'%(sname))
            else:
                for ckey in cvalue.dtype.fields.keys():
                    np.testing.assert_equal(cvalue.value, cvalue_new.value,
                                            'testing %s/%s'%(sname, ckey))
                    
        
if __name__ == '__main__':

    test_make_kurucz_tlusty_spectral_grid()
                       
