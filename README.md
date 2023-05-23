# COSMOULINE

COSMOULINE is a pipeline designed to produce light curves of point sources from a set of wide field images. It uses [STARRED](https://gitlab.com/cosmograil/starred) to do PSF photometry of the point sources while estimating the contribution of the potential extended background via a starlet-regularized joint deconvolution.

It was developed within the  [COSMOGRAIL](http://www.cosmograil.org) (now part of [TDCOSMO](https://www.epfl.ch/labs/lastro/tdcosmo/)) to reduce the data from the lensed quasars monitoring campaign, which ultimately produced the time delays used to infer the Hubble constant via time delay cosmography of lensed quasars.

## Contents

The steps are as follows:

1. Convert the provided images (fits files with some information of exposure time and gain) to electrons.
2. Subtract the sky, estimate the seeing in each frame.
3. After a choice of a reference imaging (usually the best seeing one), align the rest of the images onto the reference one.
4. A GUI prompts the user for the location of the lens, as well as that of several reference stars (used to model the PSF and compute the flux normalization of each image). Then, extract the relevant regions from the images, stored into HDF5 files.
5. Model the PSF using STARRED. 
6. Calculate the flux in each reference star and image using STARRED ("deconvolution", although no background). Calculate the normalization from the obtained fluxes.
7. Deconvolution of the lens using STARRED.
8. Utilities to export the light curves into `rdb` text files, which can then be read by the [PyCS3](https://gitlab.com/cosmograil/PyCS3) toolbox to estimate time delays.



## License

If you use this code, please cite the [COSMOGRAIL](http://www.cosmograil.org) collaboration.

If you make use of the PyMCS PSF fitting and/or two-channel deconvolution scheme, please cite the corresponding publications ([Magain+1998](http://adsabs.harvard.edu/abs/1998ApJ...494..472M), [Cantale+2016](http://adsabs.harvard.edu/abs/2016A%26A...589A..81C)). Note that [STARRED](https://gitlab.com/cosmograil/starred) now implements this 2-channel deconvolution scheme in a more modern framework.

Copyright (©) 2008-2023 EPFL (Ecole Polytechnique Fédérale de Lausanne)
Laboratory of Astrophysics (LASTRO)

COSMOULINE is free software ; you can redistribute it and/or modify it under the terms of the 
GNU General Public License as published by the Free Software Foundation ; either version 3 
of the License, or (at your option) any later version.

COSMOULINE is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY ; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details (LICENSE.txt). You should have received a  copy of the GNU General Public License along with COSMOULINE; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
