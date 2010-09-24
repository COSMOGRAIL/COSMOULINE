# Compilation of F77 MCS for cosmouline
# You might have to adapt this, but it gives the idea.

# We need :
# - extract.exe
# - psf.exe
# - deconv.exe
# For the last two, we also want versions with reduced verbosity (but otherwise identical) :
# - psf_silence.exe
# - deconv_silence.exe


# I will have to update this


# on obsds23 et cie :

f77 -O -o extract.exe extract.f /usr/lib/libcfitsio.a -lm
f77 -O -o psf.exe psf.f /usr/lib/libcfitsio.a -lm
f77 -O -o deconv.exe deconv.f /usr/lib/libcfitsio.a -lm

f77 -O -o psf_silence.exe psf_silence.f /usr/lib/libcfitsio.a -lm
f77 -O -o deconv_silence.exe deconv_silence.f /usr/lib/libcfitsio.a -lm







# on my Mac, with optional vectorize option :

#gfortran -o extract.exe extract.f /Applications/scisoft/i386/lib/libcfitsio.a -O3 -ftree-vectorize
#gfortran -o psf.exe psf.f /Applications/scisoft/i386/lib/libcfitsio.a -O3 -ftree-vectorize
#gfortran -o dec-noquest.exe deconv-noquest.f /Applications/scisoft/i386/lib/libcfitsio.a -O3 -ftree-vectorize




# Lines to tweak for psf_silence :
#	69
#	656


