# on obsds23 :

f77 -O -o extract.exe extract.f /usr/lib/libcfitsio.a -lm
f77 -O -o psf.exe psf.f /usr/lib/libcfitsio.a -lm
f77 -O -o deconv.exe deconv.f /usr/lib/libcfitsio.a -lm

f77 -O -o psf_silence.exe psf_silence.f /usr/lib/libcfitsio.a -lm
f77 -O -o deconv_silence.exe deconv_silence.f /usr/lib/libcfitsio.a -lm

