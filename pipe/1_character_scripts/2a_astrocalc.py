#
#	Performs some "astronomical" calculations (most important : hjd), using pyephem
#	Adds a lot of not-that-important entries to the database :-)
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *

import ephem # this is pyephem...
import math

# Something not included in pyephem : airmass estimation :
def airmass(radalt):
#	We calculate the airmass (radalt is altitude in radians)
#	Rozenberg's empirical relation :
#	X = 1 / [sin ho + 0.025 exp(-11 sin ho)]
#	where ho is the apparent altitude of the object. This formula can be used all down to the horizon (where it gives X = 40).

	if radalt < 0.0:
		return -1.0
	elif radalt > math.pi/2.0:
		return -2.0
	else :
		return 1.0 / (math.sin(radalt) + 0.025*math.exp(-11.0*math.sin(radalt)))

#	A plot to test :
#n = 100
#alts = [(float(i)/float(n)) *math.pi/2.0 for i in range(n+1)]
#ams = [airmass(alt) for alt in alts]
#degs = [alt*180.0/math.pi for alt in alts]
#plt.plot(degs, ams)
#plt.show()



db = KirbyBase()
if update:
	images = db.select(imgdb, ['gogogo','treatme', 'updating'], [True, True, True], returnType='dict')
	askquestions = False
else:
	images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)


print "Doublecheck that this is true : ", xephemlens
proquest(askquestions)

# We make a backup copy of our database.
backupfile(imgdb, dbbudir, "astrocalc")

# We add some new fields into the holy database.
if "hjd" not in db.getFieldNames(imgdb) :
	db.addFields(imgdb, ['hjd:str', 'mhjd:float', 'calctime:str', "alt:float", "az:float", 'airmass:float', 'moonpercent:float', 'moondist:float', 'moonalt:float', 'sundist:float', 'sunalt:float', 'astrofishy:bool', 'astrocomment:str'])

for i,image in enumerate(images):

	print "- " * 30
	print i+1, "/", nbrofimages, ":", image['imgname']
	
	astrofishy = False # this is a flag we set if we find something fishy... like observation in daylight etc...
	astrocomment = ""
	
	telescope = ephem.Observer()
	telescope.long = image['telescopelongitude']
	telescope.lat = image['telescopelatitude']
	telescope.elevation = image['telescopeelevation']
	telescope.epoch = ephem.J2000

	# DJD = JD - 2415020 is the Dublin Julian Date used by pyephem.
	djd = float(image['jd']) - 2415020.0 # jd is a string !
	telescope.date = djd
	calctime = str(telescope.date)
	print "UTC datetime : %s" % calctime

	lens = ephem.readdb(xephemlens)
	lens.compute(telescope)
	airmassvalue = airmass(float(lens.alt))
	if (airmassvalue < 1.0) or (airmassvalue > 5.0):
		astrofishy = True
		astrocomment = astrocomment + "Altitude : %s (airmass %5.2f). " % (lens.alt, airmassvalue)	
	print "Altitude : %s (airmass %5.2f)." % (lens.alt, airmassvalue)
	
	lensalt = float(lens.alt) * 180.00 / math.pi
	lensaz = float(lens.az) * 180.00 / math.pi

	moon = ephem.Moon()
	moon.compute(telescope)

	moonsep = ephem.separation(moon, lens)
	moondist = math.degrees(float(moonsep))
	print "Separation to the Moon is %.2f degrees." % moondist
	moonpercent = float(moon.phase)
	print "Moon illumation : %5.2f %%" % moonpercent
	moonalt=math.degrees(float(moon.alt))
	print 'Moon altitude [degrees]: %.2f' % moonalt

	sun = ephem.Sun()
	sun.compute(telescope)
	
	sunalt = math.degrees(float(sun.alt))
	if sunalt > 0.0 :
		astrofishy = True
		astrocomment = astrocomment + "Sun altitude : %.2f " % sunalt
	print "Sun altitude : %.2f" % sunalt
	print "Sun position : RA %s / Dec %s" % (sun.ra, sun.dec)
	# http://en.wikipedia.org/wiki/Heliocentric_Julian_Day
	# If the Sun's celestial coordinates are (ra0,dec0) and the coordinates of the observed object or event are (ra,dec),
	# and if the distance between the Sun and Earth is d, then
	# HJD = JD - (d/c) [sin(dec) sin(dec0) + cos(dec) cos(dec0) cos(ra-ra0)]

	dc = (sun.earth_distance * ephem.meters_per_au / ephem.c)/(60.0*60.0*24.0) # the factor d/c, expressed in days

	rasun = float(sun.ra)
	decsun = float(sun.dec)
	ralens = float(lens.ra)
	declens = float(lens.dec)
	sundist = math.degrees(float(ephem.separation(sun, lens)))

	print "Separation to the Sun is %.2f degrees." % sundist

	hjd = float(image['jd']) - dc * (math.sin(declens)*math.sin(decsun) + math.cos(declens)*math.cos(decsun)*math.cos(ralens-rasun))
	# So we calculate hjd based on the julian date that we got somehow from the header.
	
	mhjd = hjd - 2400000.5
	hjd = "%.6f" % hjd

	# some sanity checks, while we are at it
	if math.fabs(float(image['jd']) - float(hjd)) > 0.0059 : # should be less then 8.5 minutes
		astrofishy = True
		astrocomment = astrocomment + "Sun seems to be a bit too far from Earth... %f days" % math.fabs(image['mjd'] - mhjd)
	
	# check the date from jd with the date from the FITS header
	# field already in database : date = 2006-03-07
	# output of ephem : 2008/12/20 15:31:58
	
	transfcalctimelist = calctime.split()[0].split("/")
	transfcalctime = transfcalctimelist[0] + "-" + transfcalctimelist[1] + "-" + transfcalctimelist[2]
	transfdatelist = image['date'].split()[0].split("-")
	
	if (int(transfcalctimelist[0]) != int(transfdatelist[0])) or (int(transfcalctimelist[1]) != int(transfdatelist[1])) or (int(transfcalctimelist[2]) != int(transfdatelist[2])) :
		astrofishy = True
		astrocomment = astrocomment + "FITS date is %s, but calctime is %s !?" %(image['date'], calctime)
		
	# We update the data
	db.update(imgdb, ['recno'], [image['recno']], {'hjd': hjd, 'mhjd':mhjd, 'calctime':calctime, 'alt':lensalt, 'az':lensaz, 'airmass':airmassvalue, 'moonpercent':moonpercent, 'moondist':moondist, 'moonalt':moonalt, 'sundist':sundist, 'sunalt':sunalt, 'astrofishy':astrofishy, 'astrocomment':astrocomment})
	
	
db.pack(imgdb) # to erase the blank lines


print "Ok, done."

print "By the way, did you know that %s is located in the constellation %s ?"%(lens.name, ephem.constellation(lens)[1])




