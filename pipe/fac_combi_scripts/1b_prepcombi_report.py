#
#	write a report about the combination
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *

combinamenum = 'combibynight_' + combiname +'_num'

fields = ['imgname', combinamenum]

db = KirbyBase()
reporttxt = ""

setreport = db.select(imgdb, ['gogogo','treatme'], ['True', 'True'], fields, returnType='report')
reporttxt += setreport

reporttxtfile = open(os.path.join(workdir, "report_prepcombi.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()
