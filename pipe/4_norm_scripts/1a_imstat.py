#
#	Calculates some "imstatistics" on the image and the region around the lens
#	and writes them into the database. This will be usefull for various
#	things (find bad images automatically, deconvolution ...)
#
#	You need to specify the "lensregion" (as small as possible) and "emptyregion"
#	in the settings file.
#
#	stddev : sigma in an empty region, in ADU
#	maxlens : peak pixel in the small region around the lens
#	sumlens : sum of the pixels in the small region around the lens
#
from datetime import datetime
from astropy.io import fits
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
from config import alidir, computer, imgdb, imgkicklist, dbbudir, settings
from modules.kirbybase import KirbyBase
from variousfct import notify, backupfile, proquest, nicetimediff

askquestions = settings['askquestions']
emptyregion = settings['emptyregion']


# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, "imstat")

db = KirbyBase()

if settings['update']:
	print("This is an update.")
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], 
                              [ True,     True,      True], 
                              ['recno','imgname'], 
                              sortFields=['imgname'], returnType='dict')
	askquestions=False
else:
	images = db.select(imgdb, ['gogogo', 'treatme'], 
                              [ True,     True], 
                              ['recno','imgname'], 
                              sortFields=['imgname'], returnType='dict')


print("OK, we have", len(images), "images to treat.")
proquest(askquestions)

if "stddev" not in db.getFieldNames(imgdb) or "emptymean" not in db.getFieldNames(imgdb):
	print("I will add some fields to the database.")
	proquest(askquestions)
	#db.addFields(imgdb, ['stddev:float', 'maxlens:float', 'sumlens:float'])
	db.addFields(imgdb, ['stddev:float', 'emptymean:float'])


starttime = datetime.now()
tokicklist = []


### before we start, a utility function that clips data:
def clipData(image, nsigma=3):
    m = np.nanmean(image)
    s = np.nanstd(image)
    image[image>m+3*s] = np.nan 
    image[image<m-3*s] = np.nan
    
    
for i, image in enumerate(images):
	
	print(i+1, "/", len(images), ":", image['imgname'])
	

	filename = alidir + image['imgname'] + "_ali.fits"
	data = fits.getdata(filename)
    # unpack the coordinates of "emptyregion" found in the settings:
	coords = emptyregion.replace('[', '').replace(']', '').split(',')
	xrange = [int(e.strip()) for e in coords[0].split(':')]
	yrange = [int(e.strip()) for e in coords[1].split(':')]
    # single out the empty region:
	emptyregiondata = data[yrange[0]:yrange[1],xrange[0]:xrange[1]]
    
    # now we calculate. 
	clipData(emptyregiondata)
	mean = float(np.nanmean(emptyregiondata))
	midpt = float(np.nanmedian(emptyregiondata))
	stddev = float(np.nanstd(emptyregiondata))
    
	
	#print image['imgname'], npix, mean, midpt, stddev, minval, maxval
	print("Empty region stddev : %8.2f, median %8.2f, mean %8.2f" % (stddev, midpt, mean))
	db.update(imgdb, ['recno'], [image['recno']], {'stddev': stddev, 'emptymean': mean})



db.pack(imgdb) # to erase the blank lines

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, settings['withsound'], "I computed some statistics for %i images. It took %s" %(len(images), timetaken))

print(len(tokicklist), 'IRAF crashed on these guys:')
for imgname in tokicklist:
	print(imgname)

print("Copy the names above to your kicklist! (or investigate the problems if half of the images are rejected...)")
print("I can do it for you if you want")
proquest(askquestions)
kicklist = open(imgkicklist, "a")
for imgname in tokicklist:
	kicklist.write("\n" + imgname)
kicklist.close()
print('Ok, done.')
print("Do not forget to update your kicklist manually !")