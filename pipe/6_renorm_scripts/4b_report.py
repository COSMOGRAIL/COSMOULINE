#
#	write a report about the normalization
#	not sure if useful... let's see
#

import sys
import os
# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')
from config import imgdb, settings, normerrfieldname, normcommentfieldname
from modules.kirbybase import KirbyBase

normname = settings['normname']
workdir = settings['workdir']

fields = ['imgname', normname, normerrfieldname, normcommentfieldname]


db = KirbyBase(imgdb)
reporttxt = ""

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])


for setname in sorted(list(usedsetnames)):
	
	reporttxt += f"\n\n\n################# {setname:10} ##################\n\n"
	
	setreport = db.select(imgdb, ['gogogo','treatme','setname'], 
                                 [True, True, setname],
                                 fields, 
                                 sortFields=[normname], 
                                 returnType='report')
	reporttxt += setreport
		

reportname = "report_norm_" + normname + ".txt"

reporttxtfile = open(os.path.join(workdir, reportname), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()


