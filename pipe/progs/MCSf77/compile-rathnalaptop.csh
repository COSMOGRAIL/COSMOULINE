# for rathnas laptop, with f95 and scisofts libcfitsio
# October 2010


f95 -O -o extract.exe extract.f /scisoft/lib/libcfitsio.a -lm
f95 -O -o psf.exe psf.f /scisoft/lib/libcfitsio.a -lm
f95 -O -o deconv.exe deconv.f /scisoft/lib/libcfitsio.a -lm

f95 -O -o psf_silence.exe psf_silence.f /scisoft/lib/libcfitsio.a -lm
f95 -O -o deconv_silence.exe deconv_silence.f /scisoft/lib/libcfitsio.a -lm

