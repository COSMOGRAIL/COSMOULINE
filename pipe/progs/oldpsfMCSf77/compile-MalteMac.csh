


gfortran -o extract.exe extract.f /Applications/cfitsio/libcfitsio.a -O3 -ftree-vectorize
gfortran -o psfm.exe psfm_public.f /Applications/cfitsio/libcfitsio.a -O3 -ftree-vectorize
gfortran -o psf-auto.exe psf_public_automatic.f /Applications/cfitsio/libcfitsio.a -O3 -ftree-vectorize
