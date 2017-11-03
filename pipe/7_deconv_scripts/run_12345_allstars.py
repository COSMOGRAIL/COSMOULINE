execfile("../config.py")
import os
from variousfct import *
import star


photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)

print "I will run a test deconvolution for the following stars:"
print [star.name for star in photomstars]
proquest(True)

if thisisatest == False:
    print "Warning : This is NOT a test !"
    proquest(True)

for star in photomstars :
    os.system("python 1_prepfiles.py " + star.name)
    os.system("python 2_applynorm_NU.py " + star.name)
    os.system("python 3_fillinfile_NU.py "+ star.name)
    os.system("python 4_deconv_NU.py "+ star.name)
    os.system("python 5b_showptsrc_NU.py " + star.name)
    os.system("python 5a_decpngcheck_NU.py "+ star.name)
