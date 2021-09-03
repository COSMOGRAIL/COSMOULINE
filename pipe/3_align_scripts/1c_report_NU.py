#
#	write a report about this identification of coordinates
#	This report is written for ALL imagesets, independent of current "treatme" flag.
#	But results are present one imageset after the other.

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
from star import *

db = KirbyBase()

fields = ['imgname', 'seeing', 'goodstars', 'nbralistars', 'maxalistars', 'flagali', 'angle', 'alicomment']

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])

reporttxt = ""

for setname in sorted(list(usedsetnames)):
	
	reporttxt += "\n\n\n###################### %10s     ###################\n\n"%setname
	
	noali = db.select(imgdb, ['flagali','setname'], ['!= 1', setname], fields, sortFields=['seeing'], returnType='report')
	nbr = len(db.select(imgdb, ['flagali','setname'], ['!= 1', setname], returnType='dict'))
	reporttxt += "\n\n  Images with shift determination problems, by seeing (%4i images):\n\n"%nbr
	reporttxt += noali
	
	yesali = db.select(imgdb, ['flagali', 'setname'], ['== 1', setname], fields, sortFields=['nbralistars', 'seeing'], returnType='report')
	nbr = len(db.select(imgdb, ['flagali','setname'], ['== 1', setname], returnType='dict'))
	reporttxt += "\n  Images that could be aligned, sorted by  nbralistars and seeing (%4i images):\n\n"%nbr
	reporttxt += yesali

reporttxtfile = open(os.path.join(workdir, "report_prealiident.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()

#
# the old way, before image sets
#


#db = KirbyBase()

#refmanstars = readmancatasstars(alistarscat)
#nbrmanstars = len(refmanstars)

#noshifts = db.select(imgdb, ['flagali'], ['== 0'], fields, sortFields=['seeingpixels'], returnType='report')
#reporttxt += "\n\nImages with shift determination problems :\n"
#reporttxt += noshifts

#noidentali = db.select(imgdb, ['flagali', 'nbralistars'], ['== 1', '< %d' % nbrmanstars], fields, sortFields=['nbralistars', 'seeingpixels'], returnType='report')
#reporttxt += "\n\nImages for which the alignement stars could not all be identified :\n"
#reporttxt += noidentali

#fine = db.select(imgdb, ['nbralistars'], ['== %d' % nbrmanstars], fields, sortFields=['seeingpixels'], returnType='report')
#reporttxt += "\n\nGood images :\n"
#reporttxt += fine


