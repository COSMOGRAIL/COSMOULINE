execfile("../config.py")
import os,sys
from kirbybase import KirbyBase, KBError
from variousfct import *
from headerstuff import *


print "I will update the database with new images in set %s, telescope %s from %s" %(setname, telescopename, rawdir)
print ""
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme','updating'], [True, True, True], returnType='dict')
nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)

os.chdir('../2_skysub_scripts')

try:
	os.system('python 3_facult_rm_electrons_NU.py')
except:
	print "Problem with script 3"
	sys.exit()

print "Remove electrons images done !"
