#
#	write a report about the convertion of the image from ADU to electron
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *


fields = ['imgname','gain', 'origin_gain']

db = KirbyBase()
reporttxt = ""

setreport = db.select(imgdb, ['recno'], ['*'], fields, returnType='report')
reporttxt += setreport

reporttxtfile = open(os.path.join(workdir, "report_convert.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()

