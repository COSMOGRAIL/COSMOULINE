import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import alidir, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import proquest


askquestions = settings['askquestions']




print('I will simply remove all the orignial images (converted to electrons and hence copied) from the alidir.')
print('This will save some disk space, now that images are skysubtracted...')
print("Soft links would not be removed.")

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

print("I will try to delete %i images." % len(images))
proquest(askquestions)
for i, image in enumerate(images):

	print("%i : %s" % (i+1, image["imgname"]))
	filepath = os.path.join(alidir, image["imgname"] + ".fits")
	if os.path.isfile(filepath):
		os.remove(filepath)
	else:
		print("Hmm, no such file.")
	
print("Done.")
	

