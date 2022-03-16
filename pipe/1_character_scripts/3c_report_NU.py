exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *

fields = ['imgname', 'seeingpixels', 'seeing', 'ell', 'goodstars']


db = KirbyBase()
reporttxt = ""

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])


for setname in usedsetnames:
	
	reporttxt += "\n\n      ########### %10s    ########\n\n"%setname
		
	setreport = db.select(imgdb, ['gogogo','setname'], ['True', setname], fields, sortFields=['seeing'], returnType='report')
	reporttxt += setreport


reporttxtfile = open(os.path.join(workdir, "report_seeing.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()


