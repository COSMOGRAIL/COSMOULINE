#
#	here we do a pseudo alignement on the combined images (or on simulated images) (they are already aligned)
#	indeed, we simply make renamed copies but we also update the database with the fields expected.
#	Warning: we have to copy the skysubtracted images (_skysub.fits) otherwise sextractor will crash in the next scripts!!!
#
from datetime import datetime
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import alidir, dbbudir, computer, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import proquest, backupfile, copyorlink, nicetimediff,\
                               notify


askquestions = settings['askquestions']
uselinks = settings['uselinks']


# As we will tweak the database, let's do a backup
backupfile(imgdb, dbbudir, "alignimages")

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')


nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)

print("I will not change the images, just (link or) copy the files.")
print("You won't have to run the other scripts of this directory.")
print("uselinks : %s" % (uselinks))

proquest(askquestions)

starttime = datetime.now()

# Prepare database : add new fields
if "flagali" not in db.getFieldNames(imgdb) :
	print("I will add the fields flagali, nbralistars, maxalistars, angle, alicomment to the database.")
	proquest(askquestions)
	db.addFields(imgdb, ['flagali:int', 'nbralistars:int', 'maxalistars:int', 'angle:float', 'alicomment:str'])
	
if "geomapangle" not in db.getFieldNames(imgdb) :
	print("I will add the fields geomapangle, geomaprms, geomapscale  to the database.")
	proquest(askquestions)
	db.addFields(imgdb, ['geomapangle:float', 'geomaprms:float', 'geomapscale:float'])

for i,image in enumerate(images):

	recno = image['recno']
	justname = image['imgname']
	filepath = os.path.join(alidir, justname)
	
	print("+++++++++++++++++++++++++++++++++++++++++++++++")
	print(i+1, "/", nbrofimages, ":", justname)
	
	# I update the database with pseudo values for alignement so that we still have the same structure later.
	db.update(imgdb, ['recno'], [recno], {'flagali': 1, 'nbralistars': 0, 'maxalistars': 0, 'alicomment':'Pseudo alignenement', 'angle': 0.0, 'geomapangle': 0.0, 'geomaprms': 0.0, 'geomapscale': 0.0})
	
	# The normal way to go, saving the skysubtracted image :
	#shutil.copy(filepath + "_skysub.fits", filepath + "_ali.fits")
	copyorlink(filepath + "_skysub.fits", filepath + "_ali.fits", uselinks = uselinks)

db.pack(imgdb)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)


notify(computer, settings["withsound"], "Dear user, I'm done with the pseudoalignment. I did it in %s." % timetaken)

