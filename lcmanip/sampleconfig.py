# This file configures lcmanip.
# 1) copy this sampleconfig.py into config.py (staying in the current directory).
# 2) Set lcmanipdir below
#    This is the path to the directory containing the exported cosmouline pkl database that
#    you want to manipulate. By default, this would be cosmoulines configdir, as the pkl
#    is saved there.
# 3) Copy samplelcmanip.py as some_name_of_your_choice_lcmanip.py *into the lcmanipdir* (i.e., next to the database pkl) 
# 4) All further settings are done in some_name_of_your_choice_lcmanip.py
#    To extract several deconvolutions etc, simply use several some_name_of_your_choice_lcmanip.py


lcmanipdir = "/Users/mtewes/Desktop/lensdecs/Q1355_C2" # In there is the cosmouline output file !
lcmanipfile = "2012-01-11_f_Q1355_C2_lcmanip.py" # This file contains all further settings.
# This last filename will be used also for lcmanip output files.


# Normally you do not have to change anything below this line.
################################################################################################

import os
import shutil
import sys
import numpy as np
#sys.path.append("../modules")
sys.path.append("modules")

import groupfct
import variousfct
import rdbexport



exec(compile(open(os.path.join(lcmanipdir, lcmanipfile), "rb").read(), os.path.join(lcmanipdir, lcmanipfile), 'exec'))

print("    ### Working on %s ###" % dbfilename)
outputname = os.path.splitext(lcmanipfile)[0]

dbfilepath = os.path.join(lcmanipdir, dbfilename)

print("    Deconvolution : %s" % (deconvname))
print("    Point sources : %s" % ", ".join(sourcenames))


