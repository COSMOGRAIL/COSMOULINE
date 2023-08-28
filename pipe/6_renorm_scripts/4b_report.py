#
#	write a report about the renormalization
#	not sure if useful... let's see
#

import sys
import os
# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')
from config import imgdb, settings, renormerrfieldname, renormcommentfieldname
from modules.kirbybase import KirbyBase

renormname = settings['renormname']
workdir = settings['workdir']

fields = ['imgname', renormname, renormerrfieldname, renormcommentfieldname]


db = KirbyBase(imgdb)
reporttxt = ""

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])


for setname in sorted(list(usedsetnames)):
	
	reporttxt += f"\n\n\n################# {setname:10} ##################\n\n"
	
	setreport = db.select(imgdb, ['gogogo','treatme','setname'], 
                                 [True, True, setname],
                                 fields, 
                                 sortFields=[renormname], 
                                 returnType='report')
	reporttxt += setreport
		

reportname = "report_renorm_" + renormname + ".txt"

reporttxtfile = open(os.path.join(workdir, reportname), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()


