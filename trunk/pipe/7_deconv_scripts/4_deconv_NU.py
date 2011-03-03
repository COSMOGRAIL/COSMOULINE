#	
#	Do the deconvolution
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime
from variousfct import *

print "Starting deconvolution %s" % (deckey)

db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=[deckeyfilenum])
nbimg = len(images) + 1
print "%i images (ref image is duplicated)" % nbimg

proquest(askquestions)

print "Of course I do not update the database here,"
print "so you can go on with something else in the meantime."


starttime = datetime.now()
db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=[deckeyfilenum]) # WARNING the sorting is important !!!!!!!

origdir = os.getcwd()

os.chdir(decdir)
os.system(deconvexe)
os.chdir(origdir)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "I've deconvolved %s in %s ." % (deckey, timetaken))


