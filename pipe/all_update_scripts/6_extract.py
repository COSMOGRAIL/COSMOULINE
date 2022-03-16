execfile("../config.py")
import os
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


os.chdir('../6_extract_scripts')
os.system('python 12_all_extrnancosm.py')