execfile("../config.py")
import os,sys
import astropy.io.fits as pyfits
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
os.system('python 5_facult_rm_nonalifits_NU.py')