exec (open("../config.py").read())
import os
from variousfct import *
import star


photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)

print("I will run a full deconvolution for the following stars:")
print([star.name for star in photomstars])
proquest(True)

if thisisatest == False:
    print("Warning : This is NOT a test !")
    print("You did not forget to update your photomstar.cat with only the good stars, right ?")
    proquest(True)
    

def dodeconv(star):
    os.system(f"{python} 3_fillinfile_NU.py "+ star.name)
    os.system(f"{python} 4_deconv_NU.py "+ star.name)
    os.system(f"{python} 5b_showptsrc_NU.py " + star.name)
    os.system(f"{python} 5a_decpngcheck_NU.py "+ star.name)

from multiprocessing import Pool

p = Pool(8)
p.map(dodeconv, photomstars)

if thisisatest == False: 
    print("You can now check the png and readout the good stars.")
