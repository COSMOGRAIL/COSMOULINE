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



askquestions = settings['askquestions']
fields = ['imgname', 'skylevel', 'prealistddev', 'seeing', 'goodstars', \
          'moonpercent', 'moondist', 'moonalt', 'sunalt']


db = KirbyBase()
reporttxt = ""

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], 
                                                   ['*'], 
                                                   ['setname'])])

for setname in usedsetnames:
    
    reporttxt += f"\n\n      ########### {setname:10}    ########\n\n"
    setreport = db.select(imgdb, ['gogogo','setname'], ['True', setname], 
                          fields, sortFields=['skylevel'], returnType='report')
    reporttxt += setreport

with open(os.path.join(settings['workdir'], "report_skylevel.txt"), "w") as f:
    f.write(reporttxt)
