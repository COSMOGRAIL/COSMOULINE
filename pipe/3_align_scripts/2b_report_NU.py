#
#	write a report how the alignment went
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *

fields = ['imgname', 'seeingpixels', 'seeing', 'nbralistars', 'maxalistars', 'geomaprms', 'rotator', 'geomapangle', 'geomapscale']


db = KirbyBase()
reporttxt = ""

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])


for setname in sorted(list(usedsetnames)):
	
	reporttxt += "\n\n\n###################### %10s    ###################\n\n"%setname
	
	nbr = len(db.select(imgdb, ['flagali','setname'], ['!= 1', setname], returnType='dict'))
	setreport = db.select(imgdb, ['flagali','setname'], ['!= 1', setname], fields, sortFields=['seeing'], returnType='report')
	reporttxt += "\n  Not aligned (%4i images) :\n\n"% nbr
	reporttxt += setreport
	
	nbr = len(db.select(imgdb, ['flagali','setname'], ['== 1', setname], returnType='dict'))
	setreport = db.select(imgdb, ['flagali','setname'], ['== 1', setname], fields, sortFields=['nbralistars', 'geomaprms'], returnType='report')
	reporttxt += "\n  Aligned (%4i images) :\n\n"% nbr
	reporttxt += setreport
	
	


reporttxtfile = open(os.path.join(workdir, "report_postali.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()


