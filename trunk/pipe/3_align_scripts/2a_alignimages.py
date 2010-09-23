#
#	here we do the actual geomap and gregister (pyraf)
#	we apply this inprinciple to all images gogogo, treatme, and flagali
#


execfile("../config.py")

from kirbybase import KirbyBase, KBError
import math
from pyraf import iraf
from variousfct import *
from datetime import datetime, timedelta


	# As we will tweak the database, let's do a backup
backupfile(imgdb, dbbudir, "alignimages")


db = KirbyBase()
images = db.select(imgdb, ['flagali','gogogo','treatme'], ['==1',True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')

# perhaps you want to tweak this to run the alignment only on a few images :

#images = db.select(imgdb, ['flagali','gogogo','treatme','maxalistars'], ['==1', True, True, '==7'], ['recno','imgname'], sortFields=['imgname'], returnType='dict')
#images = db.select(imgdb, ['flagali', 'geomaprms'], ['==1', '> 1.0'], ['recno','imgname','rotator'], returnType='dict')
#images = db.select(imgdb, ['flagali','imgname'], ['==1','c_e_20080526_35_1_1_1'], ['recno','imgname'], sortFields=['imgname'], returnType='dict')

#for image in images:
#	print image['imgname']

#recnos = [image['recno'] for image in images]
#sys.exit()


if "geomapangle" not in db.getFieldNames(imgdb) :
	print "I will add some fields to the database."
	proquest(askquestions)
	db.addFields(imgdb, ['geomapangle:float', 'geomaprms:float', 'geomapscale:float'])

nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)

starttime = datetime.now()

for i,image in enumerate(images):

	print "--------------------"
	print i+1, "/", nbrofimages, image['imgname']
	
	imgtorotate = alidir + image['imgname'] + "_skysub.fits"
	geomapin = alidir + image['imgname'] + ".geomap"
	
	aliimg = alidir + image['imgname'] + "_ali.fits"
	
	if os.path.isfile(aliimg):
		os.remove(aliimg)
	
	databasename = "geodatabase"
	if os.path.isfile(databasename):
		os.remove(databasename)

	iraf.unlearn(iraf.geomap)
	iraf.geomap.fitgeom = "rscale"		# shift, xyscale, rotate, rscale
	iraf.geomap.function = "polynomial"
	iraf.geomap.transfo = "broccoli"
	iraf.geomap.interac = "no"
	#iraf.geomap.verbose="no"

	mapblabla = iraf.geomap(input = geomapin, database = databasename, xmin = 1, xmax = dimx, ymin = 1, ymax = dimy, Stdout=1)
	
	
	for line in mapblabla:
		if "X and Y scale:" in line:
			mapscale = line.split()[4:6]
		if "Xin and Yin fit rms:" in line:
			maprmss = line.split()[-2:]
		if "X and Y axis rotation:" in line:
			mapangles = line.split()[-4:-2]
		if "X and Y shift:" in line:
			mapshifts = line.split()[-4:-2]
	
	geomaprms = math.sqrt(float(maprmss[0])*float(maprmss[0]) + float(maprmss[1])*float(maprmss[1]))
	geomapangle = float(mapangles[0])
	geomapscale = float(mapscale[0])
	
	if mapscale[0] != mapscale[1]:
		raise mterror("Error reading geomap scale")
	
	print "Scale :", geomapscale
	print "Angle :", geomapangle
	print "RMS   :", geomaprms
	
	db.update(imgdb, ['recno'], [image['recno']], {'geomapangle': geomapangle, 'geomaprms': geomaprms, 'geomapscale': geomapscale})

	print "geomap done"

	iraf.unlearn(iraf.gregister)
	iraf.gregister.geometry = "geometric"	# linear, distortion, geometric
	iraf.gregister.interpo = "spline3"	# linear, spline3
	iraf.gregister.boundary = "constant"	# padding with zero
	iraf.gregister.constant = 0.0
	iraf.gregister.fluxconserve = "yes"

	regblabla = iraf.gregister(input = imgtorotate, output = aliimg, database = databasename, transform = "broccoli", xmin = 1, xmax = dimx, ymin = 1, ymax = dimy, Stdout=1)

	print "gregister done"

if os.path.isfile(databasename):
	os.remove(databasename)

db.pack(imgdb)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)


notify(computer, withsound, "Dear user, I'm done with the alignment. I did it in %s." % timetaken)

