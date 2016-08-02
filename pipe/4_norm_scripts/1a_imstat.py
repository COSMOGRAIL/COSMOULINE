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

execfile("../config.py")
from pyraf import iraf
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta

# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, "imstat")

db = KirbyBase()

if update:
	print "This is an update."
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], [True, True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')
	askquestions=False
else:
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')


print "OK, we have", len(images), "images to treat."
proquest(askquestions)

if "stddev" not in db.getFieldNames(imgdb) or "emptymean" not in db.getFieldNames(imgdb):
	print "I will add some fields to the database."
	proquest(askquestions)
	#db.addFields(imgdb, ['stddev:float', 'maxlens:float', 'sumlens:float'])
	db.addFields(imgdb, ['stddev:float', 'emptymean:float'])

iraf.imutil()

starttime = datetime.now()

for i, image in enumerate(images):
	
	print i+1, "/", len(images), ":", image['imgname']
	
	# iraf examples that were used :
	#imstatistics images="@list-qso.txt" fields="npix,mean,stddev" nclip=0 format=no >> stat.qso
	#imstatistics images="@list-sigma.txt" fields="stddev" lower=INDEF upper=INDEF nclip="3" lsigma="3.0" usigma="3.0" binwidth="0.1" format=no >> stat.sigma
	#imstatistics images="@list-sigma.txt" fields="image, stddev" lower=INDEF upper=INDEF nclip="3" lsigma="3.0" usigma="3.0" binwidth="0.1" format=no >> statEtImage.sigma
	#
	
	filename = alidir + image['imgname'] + "_ali.fits"
##################### empty region ########################

	iraf.unlearn(iraf.imutil.imstat)	
	iraf.imutil.imstat.fields = "image,npix,mean,midpt,stddev,min,max" # Fields to be printed
	iraf.imutil.imstat.lower = "INDEF" # Lower limit for pixel values
	iraf.imutil.imstat.upper = "INDEF" # Upper limit for pixel values
	iraf.imutil.imstat.nclip = 2 # nbr of clipping iterations
	iraf.imutil.imstat.lsigma = 3. # Lower side clipping factor in sigma
	iraf.imutil.imstat.usigma = 3. # Upper side clipping factor in sigma
	iraf.imutil.imstat.binwidt = 0.1 # Bin width of histogram in sigma
	iraf.imutil.imstat.format = "yes" # Format output and print column labels ?
	iraf.imutil.imstat.cache = "no" # Cache image in memory ?
	
	imstatblabla = iraf.imutil.imstat(images = filename + emptyregion, Stdout=1)
	
	#for line in imstatblabla:
	#	print line
	
	elements = imstatblabla[-1].split()
	npix = int(elements[1])
	mean = float(elements[2])
	midpt = float(elements[3])
	stddev = float(elements[4])
	minval = float(elements[5])
	maxval = float(elements[6])
	
	#print image['imgname'], npix, mean, midpt, stddev, minval, maxval
	print "Empty region stddev : %8.2f, median %8.2f, mean %8.2f" % (stddev, midpt, mean)
	db.update(imgdb, ['recno'], [image['recno']], {'stddev': stddev, 'emptymean': mean})

##################### qso region ########################

# 	
# 	iraf.unlearn(iraf.imutil.imstat)	
# 	iraf.imutil.imstat.fields = "image,npix,mean,midpt,stddev,min,max" # Fields to be printed
# 	iraf.imutil.imstat.lower = "INDEF" # Lower limit for pixel values
# 	iraf.imutil.imstat.upper = "INDEF" # Upper limit for pixel values
# 	iraf.imutil.imstat.nclip = 3 # nbr of clipping iterations
# 	iraf.imutil.imstat.lsigma = 6. # Lower side clipping factor in sigma
# 	iraf.imutil.imstat.usigma = 6. # Upper side clipping factor in sigma
# 	iraf.imutil.imstat.binwidt = 0.1 # Bin width of histogram in sigma
# 	iraf.imutil.imstat.format = "yes" # Format output and print column labels ?
# 	iraf.imutil.imstat.cache = "no" # Cache image in memory ?
# 
# 	imstatblabla = iraf.imutil.imstat(images = filename + lensregion, Stdout=1)
# 
# 	elements = imstatblabla[-1].split()
# 	npix = int(elements[1])
# 	mean = float(elements[2])
# 	midpt = float(elements[3])
# 	stddev = float(elements[4])
# 	minval = float(elements[5])
# 	maxval = float(elements[6])
# 	
# 	sumlens = float(mean * npix)
# 	
# 	print image['imgname'], npix, mean, midpt, stddev, minval, maxval
# 	db.update(imgdb, ['recno'], [image['recno']], {'maxlens': maxval, 'sumlens': sumlens})
# 

db.pack(imgdb) # to erase the blank lines

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "I computed some statistics for %i images. It took %s" %(len(images), timetaken))




