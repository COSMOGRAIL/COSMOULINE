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
import forkmap


# We will tweak the db only at the end of this script.

db = KirbyBase()
images = db.select(imgdb, ['flagali','gogogo','treatme'], ['==1',True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')


print "I will run the actual alignment (on several cpus), and wait until this is done to update the database."
nbrofimages = len(images)
print "Number of images to treat :", nbrofimages

ncorestouse = forkmap.nprocessors()
if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print "maxcores = %i" % maxcores
print "For this I will run on %i cores." % ncorestouse
proquest(askquestions)


for i, img in enumerate(images):
	img["execi"] = (i+1) # We will not write this into the db, it's just for this particular run.

def aliimage(image):

	print "Image %i : %s" % (image["execi"], image["imgname"])
	
	imgtorotate = os.path.join(alidir, image['imgname'] + "_skysub.fits")
	geomapin = os.path.join(alidir, image['imgname'] + ".geomap")
	
	aliimg = os.path.join(alidir, image['imgname'] + "_ali.fits")
	
	if os.path.isfile(aliimg):
		os.remove(aliimg)
	
	databasename = os.path.join(alidir, image["imgname"] + ".geodatabase")
	if os.path.isfile(databasename):
		os.remove(databasename)

	# The default params of immatch.geomap :
	#input   =                       The input coordinate files
	#database=                       The output database file
	#xmin    =                INDEF  Minimum x reference coordinate value
	#xmax    =                INDEF  Maximum x reference coordinate value
	#ymin    =                INDEF  Minimum y reference coordinate value
	#ymax    =                INDEF  Maximum y reference coordinate value
	#(transfo=                     ) The output transform records names
	#(results=                     ) The optional results summary files
	#(fitgeom=              general) Fitting geometry
	#(functio=           polynomial) Surface type
	#(xxorder=                    2) Order of x fit in x
	#(xyorder=                    2) Order of x fit in y
	#(xxterms=                 half) X fit cross terms type
	#(yxorder=                    2) Order of y fit in x
	#(yyorder=                    2) Order of y fit in y
	#(yxterms=                 half) Y fit cross terms type
	#(maxiter=                    0) Maximum number of rejection iterations
	#(reject =                   3.) Rejection limit in sigma units
	#(calctyp=                 real) Computation type
	#(verbose=                  yes) Print messages about progress of task ?
	#(interac=                  yes) Fit transformation interactively ?
	#(graphic=             stdgraph) Default graphics device
	#(cursor =                     ) Graphics cursor
	#(mode   =                   ql)

	iraf.unlearn(iraf.immatch.geomap)
	iraf.immatch.geomap.fitgeom = "rscale"		# shift, xyscale, rotate, rscale
	iraf.immatch.geomap.function = "polynomial"
	iraf.immatch.geomap.transfo = "broccoli"
	iraf.immatch.geomap.interac = "no"
	

	mapblabla = iraf.immatch.geomap(input = geomapin, database = databasename, xmin = 1, xmax = dimx, ymin = 1, ymax = dimy, Stdout=1)
	
	
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
	
	print "%i Scale : %f" % (image["execi"], geomapscale)
	print "%i Angle : %f" % (image["execi"], geomapangle)
	print "%i RMS   : %f" % (image["execi"], geomaprms)
	
	image["geomapscale"] = geomapscale
	image["geomapangle"] = geomapangle
	image["geomaprms"] = geomaprms
	
	print "%i geomap done" % (image["execi"])




	#input   =                       Input data
	#output  =                       Output data
	#database=                       Name of GEOMAP database file
	#transfor=                       Names of coordinate transforms in database file
	#(geometr=            geometric) Geometry (linear,distortion,geometric)
	#(xmin   =                INDEF) Minimum reference x value of output picture
	#(xmax   =                INDEF) Maximum reference x value of output picture
	#(ymin   =                INDEF) Minimum reference y value of output picture
	#(ymax   =                INDEF) Maximum reference y value of output picture
	#(xscale =                   1.) X scale of output picture in reference units per pixel
	#(yscale =                   1.) Y scale of output picture in reference units per pixel
	#(ncols  =                INDEF) Number of columns in the output picture
	#(nlines =                INDEF) Number of lines in the output picture
	#(xsample=                   1.) Coordinate surface sampling area in x
	#(ysample=                   1.) Coordinate surface sampling area in y
	#(interpo=               linear) Interpolant (nearest,linear,poly3,poly5,spline3)
	#(boundar=              nearest) Boundary extension (nearest,constant,reflect,wrap)
	#(constan=                   0.) Constant for constant boundary extension 
	#(fluxcon=                  yes) Preserve image flux ?
	#(nxblock=                  512) X dimension of working block size in pixels
	#(nyblock=                  512) Y dimension of working block size in pixels
	#(verbose=                  yes) Print messages about the progress of the task ?
	#(mode   =                   ql)



	

	iraf.unlearn(iraf.immatch.gregister)
	iraf.immatch.gregister.geometry = "geometric"	# linear, distortion, geometric
	iraf.immatch.gregister.interpo = "spline3"	# linear, spline3
	iraf.immatch.gregister.boundary = "constant"	# padding with zero
	iraf.immatch.gregister.constant = 0.0
	iraf.immatch.gregister.fluxconserve = "yes"

	regblabla = iraf.immatch.gregister(input = imgtorotate, output = aliimg, database = databasename, transform = "broccoli", xmin = 1, xmax = dimx, ymin = 1, ymax = dimy, Stdout=1)
	
	if os.path.isfile(databasename):
		os.remove(databasename)

	print "%i gregister done" % (image["execi"])


starttime = datetime.now()
forkmap.map(aliimage, images, n = ncorestouse)
endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "Dear user, I'm done with the alignment. I did it in %s." % timetaken)
print ("Now updating the database...")

backupfile(imgdb, dbbudir, "alignimages")

if "geomapangle" not in db.getFieldNames(imgdb) :
	db.addFields(imgdb, ['geomapangle:float', 'geomaprms:float', 'geomapscale:float'])

widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(), ' ', progressbar.ReverseBar('<')]
pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(images)).start()
for image in images:
	db.update(imgdb, ['recno'], [image['recno']], {'geomapangle': image["geomapangle"], 'geomaprms': image["geomaprms"], 'geomapscale': image["geomapscale"]})
	pbar.update(i)
pbar.finish()	

db.pack(imgdb)


notify(computer, withsound, "Done." % timetaken)

