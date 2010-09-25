
# Mac, with optional vectorize option
# gfortran installed from here :
# http://hpc.sourceforge.net/
# cfitsio compiled from source



gfortran -o extract.exe extract.f /Applications/cfitsio/libcfitsio.a -O3 -ftree-vectorize
gfortran -o psf.exe psf.f /Applications/cfitsio/libcfitsio.a -O3 -ftree-vectorize
gfortran -o deconv.exe deconv.f /Applications/cfitsio/libcfitsio.a -O3 -ftree-vectorize
gfortran -o psf_silence.exe psf_silence.f /Applications/cfitsio/libcfitsio.a -O3 -ftree-vectorize
gfortran -o deconv_silence.exe deconv_silence.f /Applications/cfitsio/libcfitsio.a -O3 -ftree-vectorize


