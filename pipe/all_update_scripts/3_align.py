execfile("../config.py")
import os
from kirbybase import KirbyBase, KBError
from variousfct import *
from headerstuff import *


print "I will update the database with new images in set %s, telescope %s from %s" %(setname, telescopename, rawdir)
print "Note that I will use the normal sky substraction"
print ""
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme','updating'], [True, True, True], returnType='dict')
nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)


os.chdir('../3_align_scripts')
os.system('python 1b_identcoord.py')
os.system('python 1c_report_NU.py')
os.system('python 2a_multicpu_alignimages.py')
os.system('python 2b_report_NU.py')
os.system('python 3_updateflags.py')
os.system('python 4_pngcheck_NU.py')

print "Alignment done!"