
execfile("../config.py")
import os,sys
import glob
from kirbybase import KirbyBase, KBError
from variousfct import *
from headerstuff import *


print "I will update the database with new images in set %s, telescope %s from %s" %(setname, telescopename, rawdir)
print ""
nimages = len(glob.glob(os.path.join(rawdir, "*.fits")))
db = KirbyBase()
images = db.select(imgdb, ['recno'], ['*'],['setname'], returnType='dict')
nimagesindb = len([image for image in images if image['setname'] == setname])
print "I have %i images in the database for set %s"%(nimagesindb, setname)
print "I have found %i images in the your raw folder"%(nimages)
if nimages > nimagesindb :
	nnewimages = nimages-nimagesindb
	print "This means %i new images added to this set" % nnewimages
else :
	nnewimages = nimages
	print "It seems that you have only the new images in the raw folder, I will add %i new images."%nimages

if nnewimages == 0:
	print "Nothing to do."
	#sys.exit()

proquest(True)

os.chdir('../1_character_scripts')
try:
	os.system('python 1a_addtodatabase.py')
except:
	print "Problem with script 1a"
	sys.exit()
try:
	os.system('python 1b_copyconvert_NU.py')
except:
	print "Problem with script 1b "
	sys.exit()
try:
	os.system('python 1c_report_NU.py')
except:
	print "Problem with script 1c"
	sys.exit()
try:
	os.system('python 2a_astrocalc.py')
except:
	print "Problem with script 2a"
	sys.exit()
try:
	os.system('python 2b_report_NU.py')
except:
	print "Problem with script 2b"
	sys.exit()
try:
	os.system('python 3a_runsex_NU.py')
except:
	print "Problem with script 3a"
	sys.exit()
try:
	os.system('python 3b_measureseeing.py')
except:
	print "Problem with script 3b"
	sys.exit()
try:
	os.system('python 3c_report_NU.py')
except:
	print "Problem with script 3c"
	sys.exit()
try:
	os.system('python 4a_skystats.py')
except:
	print "Problem with script 4a"
	sys.exit()
try:
	os.system('python 4b_report_NU.py')
except:
	print "Problem with script 4b"
	sys.exit()

print "Done with characterisation !"