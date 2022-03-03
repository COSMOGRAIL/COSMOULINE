#
#	Gets the heliocentric julian date of the images
#	and writes it into the database, as hjd
#
#
#	mjd is provided by the header
#	jd and hjd will be calculated ...
#	We will update the field "epoch" in the header of the aligned image
#



exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from pyraf import iraf
from kirbybase import KirbyBase, KBError
#import operator # for the sorting
#import csv # just leave it there
from variousfct import *

print("bug")
sys.exit()


	# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, "hjd")

db = KirbyBase(imgdb)
images = db.select(imgdb, ['gogogo'], [True], ['recno','imgname','mjd','date'], sortFields=['imgname'], returnType='dict')

if db.getFieldNames(imgdb).count("hjd") == 0 :
	db.addFields(imgdb, ['hjd:str'])
if db.getFieldNames(imgdb).count("jd") == 0 :
	db.addFields(imgdb, ['jd:str'])

print("Number of images :", len(images))

iraf.astutil()
iraf.unlearn(iraf.astutil.setjd)
	
	# header keyworkds
iraf.astutil.setjd.observa = "lapalma"
iraf.astutil.setjd.date = "date"
iraf.astutil.setjd.time = "utstart"
iraf.astutil.setjd.exposure = "exptime"
iraf.astutil.setjd.ra = "ra"
iraf.astutil.setjd.dec = "dec"
iraf.astutil.setjd.epoch = "epoch"

iraf.astutil.setjd.jd = "jd"
iraf.astutil.setjd.hjd = "hjd"
iraf.astutil.setjd.ljd = "ljd"

iraf.astutil.setjd.utdate = "yes"
iraf.astutil.setjd.uttime = "yes"
iraf.astutil.setjd.listonl = "yes" 	# does not change the original file !

iraf.imutil()
iraf.unlearn(iraf.imutil.hedit)		# does change the original file ...

iraf.imutil.hedit.addonly = "yes"
iraf.imutil.hedit.verify = "no"
	
for image in images:
	
	filename = alidir + image['imgname'] + "_ali.fits"
	
	#	Liverpool Telescope : lat 28:45:44.63 lon -17:52:47.99 	= lat 28.762397, lon 17.979997 W
	#
	
	print(filename)
	heditblabla = iraf.imutil.hedit(image=filename, fields="EPOCH", value=2000, Stdout=1)
	#print heditblabla
	
	setjdblabla = iraf.astutil.setjd(image=filename, Stdout=1)
	#print len(setjdblabla)
	
	for line in setjdblabla:
		#print line
		if line[0] == "#":
			continue
		elements = line.split()
		jd = elements[1]
		hjd = elements[2]
		ljd = elements[3]
		
	print(image['imgname'], image['mjd'], hjd, jd)
		
		
	db.update(imgdb, ['recno'], [image['recno']], {'hjd': hjd})
	db.update(imgdb, ['recno'], [image['recno']], {'jd': jd})
	

db.pack(imgdb) # to erase the blank lines

print("Done.")
