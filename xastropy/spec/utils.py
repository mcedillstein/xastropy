"""
#;+ 
#; NAME:
#; utils
#;    Version 1.0
#;
#; PURPOSE:
#;    Module for spectral utilities
#;       Primarily overloads of Spectrum1D
#;   07-Sep-2014 by JXP
#;-
#;------------------------------------------------------------------------------
"""
from __future__ import print_function, absolute_import, division, unicode_literals

import numpy as np
import os
import astropy as apy

from astropy import units as u

from specutils import Spectrum1D
from xastropy.xutils import xdebug as xdb

# Child Class of specutils/Spectrum1D 
#    Generated by JXP to add functionality before it gets ingested in the specutils distribution
class XSpectrum1D(Spectrum1D):

    #### ###############################
    #  Instantiate from Spectrum1D [best to avoid!]
    @classmethod
    def from_spec1d(cls, spec1d):
            
        # Giddy up
        return cls(flux=spec1d.flux, wcs=spec1d.wcs, unit=spec1d.unit,
                   uncertainty=spec1d.uncertainty, mask=spec1d.mask, meta=spec1d.meta)
        

    #### ###############################
    #  Grabs spectrum pixels in a velocity window
    def pix_minmax(self, *args):
        """Pixels in velocity range

        Parameters
        ----------
        Option 1: wvmnx
          wvmnx: Tuple of 2 floats
            wvmin, wvmax in spectral units

        Option 2: zabs, wrest, vmnx
          zabs: Absorption redshift
          wrest: Rest wavelength
          vmnx: Tuple of 2 floats
            vmin, vmax in km/s
    
        Returns:
        pix: array
          Integer list of pixels
        """
        if len(args) == 1: # Option 1
            wvmnx = args[0]
        elif len(args) == 3: # Option 2
            from astropy import constants as const
            # args = zabs, wrest, vmnx
            wvmnx = (args[0]+1) * (args[1] + (args[1] * np.array(args[2]) / const.c.to('km/s')).value )

        # Locate the values
        pixmin = np.argmin( np.fabs( self.dispersion-wvmnx[0] ) )
        pixmax = np.argmin( np.fabs( self.dispersion-wvmnx[1] ) )

        gdpix = np.arange(pixmin,pixmax+1)

        # Fill + Return
        self.sub_pix = gdpix
        return gdpix, wvmnx, (pixmin, pixmax)

    #### ###############################
    #  Box car smooth
    def box_smooth(self, nbox):
        """ Box car smooth spectrum and return a new one
        Is a simple wrapper to the rebin routine

        Parameters
        ----------
        nbox: integer
          Number of pixels to smooth over

        Returns:
          XSpectrum1D of the smoothed spectrum
        """
        from xastropy.xutils import arrays as xxa
        # Truncate arrays as need be
        npix = len(self.flux)
        new_npix = npix // nbox # New division
        orig_pix = np.arange( new_npix * nbox )

        # Rebin (mean)
        new_wv = xxa.scipy_rebin( self.dispersion[orig_pix], new_npix )
        new_fx = xxa.scipy_rebin( self.flux[orig_pix], new_npix )
        new_sig = xxa.scipy_rebin( self.sig[orig_pix], new_npix ) / np.sqrt(nbox)

        # Return
        return XSpectrum1D.from_array(new_wv, new_fx,
                                      uncertainty=apy.nddata.StdDevUncertainty(new_sig))

