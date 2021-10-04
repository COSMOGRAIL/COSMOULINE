# compiled cfitsio from source: used cfitsio3250.tar.gz  from their ftp server at https://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/
lib="/home/fred/lib/lib/libcfitsio.a"

f95 -O -o extract.exe extract.f $lib -lm
f95 -O -o psf.exe psf.f $lib -lm
f95 -O -o deconv.exe deconv.f $lib -lm

f95 -O -o psf_silence.exe psf_silence.f $lib -lm
f95 -O -o deconv_silence.exe deconv_silence.f $lib -lm

