execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import star

"""
This script can be used anytime during the PSF
"""


db = KirbyBase()


print "psfkey =", psfkey

print "Reading psf star catalog ..."
psfstars = star.readmancat(psfstarcat)

for i, s in enumerate(psfstars):
	print '---------------PSF STAR------------------'
	print s.name
	print '-----------------------------------------'
	s.filenumber = (i+1)


if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
if update:
	print "This is an update."
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	askquestions=False
else :
	images = db.select(imgdb, ['gogogo', 'treatme',psfkeyflag], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])




print "Number of images to treat :", len(images)
proquest(askquestions)


kicklist = []

for i, image in enumerate(images):

	print "%i : %s" % (i+1, image['imgname'])
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	os.chdir(os.path.join(imgpsfdir, "results"))

	for s in psfstars:

		# We modify the sigma image
		starfilename = "star_%03i.fits" % s.filenumber
		(stararray, starheader) = fromfits(starfilename, verbose=False)

		if max([max(starline) for starline in stararray]) > image["saturlevel"]*image["gain"]*maxpixelvaluecoeff:
			print image["imgname"] , ' is saturated ! '
			kicklist.append(image["imgname"])
			break


print len(kicklist), ' PSF(s) are saturated:'
for imgname in kicklist:
	print imgname

print "Copy the names above to your psf skiplist!"
print "I can do it for you if you want"
proquest(askquestions)
skiplist = open(psfkicklist, "a")
for imgname in kicklist:
	skiplist.write("\n" + imgname)
skiplist.close()
print 'Ok, done.'