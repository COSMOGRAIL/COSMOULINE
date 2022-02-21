import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import imgdb, settings
from modules.kirbybase import KirbyBase




fields = ['imgname', 'seeingpixels', 'seeing', 'ell', 'goodstars']


db = KirbyBase()
reporttxt = ""

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])


for setname in usedsetnames:
	
	reporttxt += "\n\n      ########### %10s    ########\n\n"%setname
		
	setreport = db.select(imgdb, ['gogogo','setname'], ['True', setname], 
                          fields, sortFields=['seeing'], returnType='report')
	reporttxt += setreport


reporttxtfile = open(os.path.join(settings['workdir'], "report_seeing.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()


