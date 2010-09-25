# obssr1 (new fedora server @ LASTRO) :

# I compiled cfitsio from source 2010-09-26, on obssr1.
# The libcfitsio.a from scisoft is not working.

f77 -O -o extract.exe extract.f /home/epfl/tewes/progs/cfitsio/libcfitsio.a -lm
f77 -O -o psf.exe psf.f /home/epfl/tewes/progs/cfitsio/libcfitsio.a -lm
f77 -O -o deconv.exe deconv.f /home/epfl/tewes/progs/cfitsio/libcfitsio.a -lm

f77 -O -o psf_silence.exe psf_silence.f /home/epfl/tewes/progs/cfitsio/libcfitsio.a -lm
f77 -O -o deconv_silence.exe deconv_silence.f /home/epfl/tewes/progs/cfitsio/libcfitsio.a -lm

