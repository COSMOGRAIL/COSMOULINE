Compilation of F77 MCS for cosmouline
The PSF here is the "new" one (old one is no longer supported)
deconv has been modified to support individual fwhm-des-g, in May 2010

We need :
 - extract.exe
 - psf.exe
 - deconv.exe
For the last two, we also want versions with reduced verbosity (but otherwise identical) :
 - psf_silence.exe
 - deconv_silence.exe


Some sample compilation commands can be found in the csh scripts of this directory.


Some hard-to find lines I had to tweak for psf_silence :
69
656




