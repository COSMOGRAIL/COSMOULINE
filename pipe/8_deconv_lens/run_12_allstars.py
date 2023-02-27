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
    

for star in photomstars :
    os.system(f"{python} 1_prepfiles.py " + star.name)
    os.system(f"{python} 2_applynorm_NU.py " + star.name)
    
