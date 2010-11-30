
#
#	write a report about the convertion of the image from ADU to electron
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *


fields = ['imgname','gain', 'origin_gain', "satur_level"]

db = KirbyBase()
reporttxt = ""

usedsetnames = set(map(lambda x : x[0], db.select(imgdb, ['recno'], ['*'], ['setname'])))

for setname in usedsetnames:
	
	reporttxt += "\n\n" + 20*"=" +  "%10s "%setname + 20*"=" +"\n\n"

	setreport = db.select(imgdb, ['setname'], [setname], fields, returnType='report')
	reporttxt += setreport

reporttxtfile = open(os.path.join(workdir, "report_convert.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()

