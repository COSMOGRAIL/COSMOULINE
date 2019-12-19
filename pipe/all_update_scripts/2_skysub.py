execfile("../config.py")
import os,sys
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

os.chdir('../2_skysub_scripts')
try:
	os.system('python 1_skysub_NU.py')
except:
	print "Problem with script 1"
	sys.exit()

if defringed:
	os.system('python 1b_compute_fringes.py')

try:
	os.system('python 2_skypng_NU.py')
except:
	print "Problem with script 2"
	sys.exit()
# try:
# 	os.system('python 3_facult_rm_electrons_NU.py')
# except:
# 	print "Problem with script 3"
# 	sys.exit()

print "Sky substraction done !"
