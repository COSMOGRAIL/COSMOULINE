#
#	write a report about the fishy things discovered in the analysis
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *


fields = ['imgname', 'datet','calctime', 'mhjd', 'airmass', 'moonpercent', 'moondist', 'moonalt', 'sunalt', 'sundist']


db = KirbyBase()
reporttxt = ""

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])


for setname in usedsetnames:
	
	reporttxt += "\n\n" + 20*"=" +  "%10s "%setname + 20*"=" +"\n\n"
		
	nbr = len(db.select(imgdb, ['astrofishy','setname','gogogo'], [True, setname, 'True'], returnType='dict'))
	setreport = db.select(imgdb, ['astrofishy','setname','gogogo'], [True, setname, 'True'], fields + ['astrocomment'], sortFields=['mhjd'], returnType='report')
	reporttxt += "\n  Something fishy with %i images :\n\n"% nbr
	reporttxt += setreport
	print("Setname %10s : %3i fishy images." %(setname, nbr))
	
	nbr = len(db.select(imgdb, ['astrofishy','setname','gogogo'], [False, setname, 'True'], returnType='dict'))
	setreport = db.select(imgdb, ['astrofishy','setname','gogogo'], [False, setname, 'True'], fields, sortFields=['airmass'], returnType='report')
	reporttxt += "\n  But these %i images are fine :\n\n"% nbr
	reporttxt += setreport
	

reporttxtfile = open(os.path.join(workdir, "report_astrocalc.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()

print("If there are fishy images, you should to do something about it now.")

