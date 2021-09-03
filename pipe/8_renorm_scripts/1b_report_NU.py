#
#	write a report about the renormalization
#	not sure if useful... let's see
#




exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *



fields = ['imgname', renormname, renormerrfieldname, renormcommentfieldname]


db = KirbyBase()
reporttxt = ""

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])


for setname in sorted(list(usedsetnames)):
	
	reporttxt += "\n\n\n###################### %10s    ###################\n\n"%setname
	
	setreport = db.select(imgdb, ['gogogo','treatme','setname'], [True, True, setname], fields, sortFields=[renormname], returnType='report')
	reporttxt += setreport
		

reportname = "report_renorm_" + renormname + ".txt"

reporttxtfile = open(os.path.join(workdir, reportname), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()


