# This file configures lcmanip.
# 1) copy this sampleconfig.py into config.py
# 2) Set lcmanipdir below
#    This is the path to the directory containing the exported cosmouline pkl database that
#    you want to manipulate. By default, this would be cosmoulines configdir, as the pkl
#    is saved there.
# 3) Copy samplelcmanip.py as lcmanip.py into the lcmanipdir. 
# 4) All further settings are done in this lcmanip.py



lcmanipdir = "/Users/mtewes/Desktop/f_Q1355_C2"



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

print "    ### Working on %s ###" % dbfilename

dbfilepath = os.path.join(lcmanipdir, dbfilename)

print "    Deconvolution : %s" % (deconvname)
print "    Point sources : %s" % ", ".join(sourcenames)


