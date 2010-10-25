# XPSM1530 by Dominik Klaes, AIfA Bonn:

# I compiled cfitsio from source 2010-09-26, on obssr1.
# The libcfitsio.a from scisoft is not working.

f95 -O -o extract.exe extract.f /scisoft/lib/libcfitsio.a -lm
f95 -O -o psf.exe psf.f /scisoft/lib/libcfitsio.a -lm
f95 -O -o deconv.exe deconv.f /scisoft/lib/libcfitsio.a -lm

f95 -O -o psf_silence.exe psf_silence.f /scisoft/lib/libcfitsio.a -lm
f95 -O -o deconv_silence.exe deconv_silence.f /scisoft/lib/libcfitsio.a -lm

