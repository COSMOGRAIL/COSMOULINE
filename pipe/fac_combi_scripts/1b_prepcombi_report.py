#
#	write a report about the combination
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *

combinamenum = 'combibynight_' + combiname +'_num'

fields = ['imgname', combinamenum]

db = KirbyBase(imgdb)
reporttxt = ""

setreport = db.select(imgdb, ['gogogo','treatme'], ['True', 'True'], fields, returnType='report')
reporttxt += setreport

reporttxtfile = open(os.path.join(workdir, "report_prepcombi.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()
