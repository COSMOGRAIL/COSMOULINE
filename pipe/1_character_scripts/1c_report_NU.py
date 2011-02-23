#
#	write a report about the fishy things discovered in the analysis
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *


fields = ['datet', 'mhjd', 'imgname', 'telescopename', 'gogogo']
db = KirbyBase()
reporttxt = db.select(imgdb, ['recno'], ['*'], fields, sortFields=['mhjd'], returnType='report')

reporttxtfile = open(os.path.join(workdir, "report_chronocontent.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()

print "Done."
