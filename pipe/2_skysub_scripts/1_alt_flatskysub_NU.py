#
#	We subtract a flat value (skylevel from the database)	
#
import numpy as np
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import alidir, computer, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import fromfits, proquest, nicetimediff, notify, tofits
from datetime import datetime

askquestions = settings['askquestions']


db = KirbyBase(imgdb)
if settings['thisisatest']:
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo','treatme','testlist'], [True, True, True], returnType='dict')
else:
	images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')
	
	
nbrimages = len(images)
print("Number of images to treat :", nbrimages)
proquest(askquestions)

starttime = datetime.now()

for i,image in enumerate(images):
	
	print("+ " * 30)
	print("%5i/%i : %s" % (i+1, nbrimages, image["imgname"]))
	
	imagepath = os.path.join(alidir, image["imgname"] + ".fits")
	
	skylevel = image["skylevel"]
	print("Skylevel to be subtracted : %.3f" % skylevel)
	
	(imagea, imageh) = fromfits(os.path.join(alidir, image["imgname"] + ".fits"), verbose = False)
	skya = np.ones(imagea.shape) * skylevel
	
	skysubimagea = imagea - skya
	
	skysubimagepath = os.path.join(alidir, image["imgname"] + "_skysub.fits")
	if os.path.isfile(skysubimagepath):
		os.remove(skysubimagepath)
	
	
	skyimagepath = os.path.join(alidir,  image["imgname"] + "_sky.fits")
	if os.path.isfile(skyimagepath):
		os.remove(skyimagepath)
	
	
	tofits(skysubimagepath, skysubimagea, hdr = imageh, verbose = True)
	tofits(skyimagepath, skya, hdr = None, verbose = True)
	
	
timetaken = nicetimediff(datetime.now() - starttime)

notify(computer, settings['withsound'], "The sky is no longer the limit. I took %s" % timetaken)


