# This file configures lcmanip.
# 1) copy this sampleconfig.py into config.py (staying in the current directory).
# 2) Set lcmanipdir below
#    This is the path to the directory containing the exported cosmouline pkl database that
#    you want to manipulate. By default, this would be cosmoulines configdir, as the pkl
#    is saved there.
# 3) Copy samplelcmanip.py as lcmanip.py *into the lcmanipdir* (i.e., next to the database pkl) 
# 4) All further settings are done in this lcmanip.py
#    You can change the name of this lcmanip.py, for instance to extract several deconvolutions etc.


lcmanipdir = "/Users/mtewes/Desktop/lensdecs/f_J1226_C2"
lcmanipfile = "lcmanip_lens.py"

# This last filename will be used also for output files.


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



execfile(os.path.join(lcmanipdir, "lcmanip.py"))
outputname = os.path.splitext(lcmanipfile)[0]

print "    ### Working on %s ###" % dbfilename

dbfilepath = os.path.join(lcmanipdir, dbfilename)

print "    Deconvolution : %s" % (deconvname)
print "    Point sources : %s" % ", ".join(sourcenames)


