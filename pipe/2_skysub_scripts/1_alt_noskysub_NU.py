#
#	mimics the sky subtraction without doing anything to the images
#	we do a copy, as this is the first time we need the actual images.
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

from config import alidir, computer, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import copyorlink, proquest, nicetimediff, notify
from datetime import datetime

askquestions = settings['askquestions']
uselinks = settings['uselinks']

db = KirbyBase(imgdb)
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

nbrimages = len(images)

print("I will not change the images, just (link or) copy the files.")
print("uselinks : %s" % (uselinks))
proquest(askquestions)

print("Number of images to treat :", nbrimages)
proquest(askquestions)

starttime = datetime.now()


for i,image in enumerate(images):
	justname = image['imgname']
	print(i+1, "/", nbrimages, ":", justname)
	
	recno = image['recno']
	withskyfilepath = os.path.join(alidir, image['imgname'] + ".fits")
	
	noskyfilepath = os.path.join(alidir, image['imgname'] + "_skysub.fits")
	
	copyorlink(withskyfilepath, noskyfilepath, uselinks=uselinks)
	

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)
notify(computer, settings['withsound'], "Files copyorlinked. It took %s" % timetaken)


