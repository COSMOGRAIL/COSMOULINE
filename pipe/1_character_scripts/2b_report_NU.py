#
#	write a report about the fishy things discovered in the analysis
#

import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
    
from config import imgdb, settings
from modules.kirbybase import KirbyBase


workdir = settings['workdir']

fields = ['imgname', 'datet','calctime', 'mhjd', 'airmass', 'moonpercent', \
          'moondist', 'moonalt', 'sunalt', 'sundist']


db = KirbyBase()
reporttxt = ""

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])


for setname in usedsetnames:
	
	reporttxt += "\n\n" + 20*"=" +  "%10s "%setname + 20*"=" +"\n\n"
		
	nbr = len(db.select(imgdb, ['astrofishy','setname','gogogo'], 
                               [True, setname, 'True'], returnType='dict'))
	setreport = db.select(imgdb, ['astrofishy','setname','gogogo'], 
                                 [True, setname, 'True'], fields + ['astrocomment'], 
                                 sortFields=['mhjd'], returnType='report')
	reporttxt += "\n  Something fishy with %i images :\n\n"% nbr
	reporttxt += setreport
	print("setname %10s : %3i fishy images." %(setname, nbr))
	
	nbr = len(db.select(imgdb, ['astrofishy','setname','gogogo'], 
                               [False, setname, 'True'], returnType='dict'))
	setreport = db.select(imgdb, ['astrofishy','setname','gogogo'], 
                                 [False, setname, 'True'], fields, 
                                 sortFields=['airmass'], returnType='report')
	reporttxt += "\n  But these %i images are fine :\n\n"% nbr
	reporttxt += setreport
	

reporttxtfile = open(os.path.join(workdir, "report_astrocalc.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()

print("If there are fishy images, you should to do something about it now.")

