import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import python, configdir, settings
from modules.variousfct import proquest
import star


photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)

print("I will run a full deconvolution for the following stars:")
print([star.name for star in photomstars])
proquest(True)

if settings['thisisatest'] == False:
    print("Warning : This is NOT a test !")
    print("You did not forget to update your photomstar.cat",
          "with only the good stars, right ?")
    proquest(True)
    

for s in photomstars :
    os.system(f"{python} 1_prepfiles.py " + s.name)
    os.system(f"{python} 2_applynorm_NU.py " + s.name)
    os.system(f"{python} 3_fillinfile_NU.py "+ s.name)
    os.system(f"{python} 4_deconv_NU.py "+ s.name)
    os.system(f"{python} 5b_showptsrc_NU.py " + s.name)
    os.system(f"{python} 5a_decpngcheck_NU.py "+ s.name)
    

if settings['thisisatest'] == False: 
    print("You can now check the png and readout the good stars.")
