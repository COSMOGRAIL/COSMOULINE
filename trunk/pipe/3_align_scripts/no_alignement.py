#
#	here we do a pseudo alignement on the combined images (or on simulated images) (they are already aligned)
#	indeed, we simply make renamed copies but we also update the database with the fields expected.
#	Warning: we have to copy the skysubtracted images (_skysub.fits) otherwise sextractor will crash in the next scripts!!!
#


execfile("../config.py")

from kirbybase import KirbyBase, KBError
import math
from variousfct import *
from datetime import datetime, timedelta


# As we will tweak the database, let's do a backup
backupfile(imgdb, dbbudir, "alignimages")


db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')

# perhaps you want to tweak this to run the alignment only on a few images :

#images = db.select(imgdb, ['flagali','gogogo','treatme','maxalistars'], ['==1', True, True, '==7'], ['recno','imgname'], sortFields=['imgname'], returnType='dict')
#images = db.select(imgdb, ['flagali', 'geomaprms'], ['==1', '> 1.0'], ['recno','imgname','rotator'], returnType='dict')
#images = db.select(imgdb, ['flagali','imgname'], ['==1','c_e_20080526_35_1_1_1'], ['recno','imgname'], sortFields=['imgname'], returnType='dict')

#for image in images:
#	print image['imgname']

#recnos = [image['recno'] for image in images]
#sys.exit()


nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)

starttime = datetime.now()

# Prepare database : add new fields
if "flagali" not in db.getFieldNames(imgdb) :
	print "I will add some fields to the database."
	proquest(askquestions)
	db.addFields(imgdb, ['flagali:int', 'nbralistars:int', 'maxalistars:int', 'angle:float', 'alicomment:str'])
	
if "geomapangle" not in db.getFieldNames(imgdb) :
	print "I will add some fields to the database."
	proquest(askquestions)
	db.addFields(imgdb, ['geomapangle:float', 'geomaprms:float', 'geomapscale:float'])

for i,image in enumerate(images):

	recno = image['recno']
	justname = image['imgname']
	filepath = os.path.join(alidir, justname)
	
	print "+++++++++++++++++++++++++++++++++++++++++++++++"
	print i+1, "/", nbrofimages, ":", justname
	
	# I update the database with pseudo values for alignement so that we still have the same structure later.
	db.update(imgdb, ['recno'], [recno], {'flagali': 1, 'nbralistars': 0, 'maxalistars': 0, 'alicomment':'Pseudo alignenement', 'angle': 0.0, 'geomapangle': 0.0, 'geomaprms': 0.0, 'geomapscale': 0.0})
	
	# The normal way to go, saving the skysubtracted image :
	shutil.copy(filepath + "_skysub.fits", filepath + "_ali.fits")
	

	print "\npseudo alignement done"


db.pack(imgdb)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)


notify(computer, withsound, "Dear user, I'm done with the alignment. I did it in %s." % timetaken)

