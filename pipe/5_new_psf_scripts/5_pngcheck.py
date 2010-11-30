#
#	generates pngs to check the psf construction
#	Each png file has the name of the image.
#	Aside of this, we make links to these png files that are numbered chronologically.
#

execfile("../config.py")
import shutil
from variousfct import *
import f2n
import cosmics
import ds9reg
from kirbybase import KirbyBase, KBError
from datetime import datetime



pngkey = psfkey + "_png"
pngdir = os.path.join(workdir, pngkey)

	# Check for former png creation :
if os.path.isdir(pngdir):
	print "I would delete existing stuff."
	proquest(askquestions)
	shutil.rmtree(pngdir)
os.mkdir(pngdir)

	# See if there is a DS9 region file (just to make the pngs even nicer :
	
ds9regfilepath = os.path.join(configdir, psfkey + "_mask.reg")
reg = ds9reg.regions(128, 128) # hardcoded for now ...
if os.path.isfile(ds9regfilepath):
	print "I have found a DS9 region file."
	reg.readds9(ds9regfilepath)
else:
	print "I haven't found a DS9 region file (no problem for me)."
# we do not need to build the mask, we just want to use the reg.circles for the pngs.

	# We read the psf stars
psfstars = readmancat(psfstarcat)

	# Select images to treat
db = KirbyBase()
if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo','treatme',psfkeyflag,'testlist'], [True,True,True,True], returnType='dict', sortFields=['setname', 'mjd'])
else :
	images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['setname', 'mjd'])

print "I will treat %i images." % len(images)
proquest(askquestions)


starttime = datetime.now()


for i, image in enumerate(images):
	print "- " * 40
	print i+1, "/", len(images), ":", image['imgname']
	
	imgpath = os.path.join(psfdir, image['imgname'])
	
	pngpath = os.path.join(pngdir, image['imgname'] + ".png")
	
	endpiece = f2n.f2nimage(shape = (128,128), fill = 0.0, verbose=False)
	endpiece.setzscale(0.0, 1.0)
	endpiece.makepilimage(scale = "lin", negative = False)
	endpiece.upsample(2)
	# We use this as a "legend" for the star names:
	starlocations = [[33.5, 33.5], [97.5, 33.5], [33.5, 97.5], [97.5, 97.5]]
	for j, star in enumerate(psfstars):
		loc = starlocations[j]
		endpiece.drawcircle(loc[0], loc[1], r=2, colour=(255), label = star["name"])
	endpiece.writeinfo(["Legend"])
	
	
	txtendpiece = f2n.f2nimage(shape = (256,256), fill = 0.0, verbose=False)
	txtendpiece.setzscale(0.0, 1.0)
	txtendpiece.makepilimage(scale = "lin", negative = False)
	
	date = image['date']
	seeing = "Seeing : %4.2f [arcsec]" % image['seeing']
	ell = "Ellipticity : %4.2f" % image['ell']
	nbralistars = "Nb alistars : %i" % image['nbralistars']
	airmass = "Airmass : %4.2f" % image['airmass']
	az = "Azimuth : %6.2f [deg]" % image['az']
	nbcosmics = "Cosmics : %i pixels" % image[psfcosmicskey]
	
	stddev = "Sky stddev : %4.2f [ADU]" % image['stddev']
	skylevel = "Sky level : %4.2f [ADU]" % image['skylevel']
	
	# we write long image names on two lines ...
	if len(image['imgname']) > 25:
		infolist = [image['imgname'][0:25], image['imgname'][25:]]
	else:
		infolist = [image['imgname']]
	infolist.extend([date, seeing, ell, nbralistars, stddev, airmass, az, nbcosmics])
	
	txtendpiece.writeinfo(infolist)
	
	
	# If cosmics are detected, we want to know where :
	cosmicslistpath = os.path.join(imgpath, "cosmicslist.pkl")
	if os.path.exists(cosmicslistpath):
		cosmicslist = readpickle(cosmicslistpath, verbose=False)
	else:
		cosmicslist = []
	
	
	f2ng001 = f2n.fromfits(os.path.join(imgpath, "g001.fits"), verbose=False) # 128 x 128
	f2ng001.setzscale(-20, 2000)
	f2ng001.makepilimage(scale = "log", negative = False)
	f2ng001.upsample(2) # Now 256 x 256
	for circle in reg.circles:
		f2ng001.drawcircle(circle["x"], circle["y"], r = circle["r"], colour = (120))
	f2ng001.drawstarslist(cosmicslist)
	#f2ng001.writeinfo([image['imgname']], (255, 0, 0))
	f2ng001.writeinfo(["g001.fits"])
	
	#f2ng001f = f2n.fromfits(imgpath + "g001.fits", verbose=False) # 128 x 128
	#f2ng001f.setzscale("ex", "ex")
	#f2ng001f.makepilimage(scale = "lin", negative = False)
	#f2ng001f.upsample(2) # Now 256 x 256
	#f2ng001f.writeinfo(["g001.fits", "(full scale)"])
	
	f2nsig001 = f2n.fromfits(os.path.join(imgpath, "sig001.fits"), verbose=False) # 128 x 128
	f2nsig001.setzscale(0.0, 0.3)
	f2nsig001.makepilimage(scale = "lin", negative = False)
	f2nsig001.upsample(2) # Now 256 x 256
	f2nsig001.writeinfo(["sig001.fits"])
	
	f2nmoffat001 = f2n.fromfits(os.path.join(imgpath, "moffat001.fits"), verbose=False) # 256 x 256
	f2nmoffat001.setzscale("ex", "ex")
	f2nmoffat001.makepilimage(scale = "log", negative = False)
	f2nmoffat001.writeinfo(["moffat001.fits"])
	#f2nmoffat001.writetitle(image['imgname'])
	
	f2nfond001 = f2n.fromfits(os.path.join(imgpath, "fond001.fits"), verbose=False) # 256 x 256
	f2nfond001.irafcrop("[65:192,65:192]") # Now 128 x 128
	#f2nfond001.setzscale(-0.1e-3, 0.1e-3)
	#f2nfond001.setzscale("ex", "ex")
	f2nfond001.setzscale(-1.0e-3, 1.0e-3)
	f2nfond001.makepilimage(scale = "lin", negative = False)
	f2nfond001.upsample(2) # Now 256 x 256
	f2nfond001.writeinfo(["fond001.fits", "(zoom on center)"])
	
	f2nresidu001 = f2n.fromfits(os.path.join(imgpath, "residu001.fits"), verbose=False) # 128 x 128
	f2nresidu001.setzscale(-3, 3)
	f2nresidu001.makepilimage(scale = "lin", negative = False)
	f2nresidu001.upsample(2) # Now 256 x 256
	f2nresidu001.writeinfo(["residu001.fits"])

	
	f2ns001 = f2n.fromfits(os.path.join(imgpath, "s001.fits"), verbose=False) # 128 x 128
	f2ns001.setzscale(1e-8, 1e-3)
	f2ns001.makepilimage(scale = "log", negative = False)
	f2ns001.upsample(2) # Now 256 x 256
	f2ns001.writeinfo(["s001.fits"])
	
	
	f2n.compose([[f2ng001, f2nsig001, f2nfond001, txtendpiece], [f2nresidu001, f2ns001, f2nmoffat001, endpiece]], pngpath)	

	orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
	os.symlink(pngpath, orderlink)
	


#origdir = os.getcwd()
#os.chdir(psfdir)
#cmd = "tar cvf " + pngkey + ".tar " + pngkey + "/"
#os.system(cmd)
#cmd = "mv " + pngkey + ".tar ../."
#os.system(cmd)
#os.chdir(origdir)

print "- " * 40
endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)
notify(computer, withsound, "I've generated the PNG files in %s ." % timetaken)


if os.path.isfile(psfkicklist):
	print "The psfkicklist already exists :"
else:
	cmd = "touch " + psfkicklist
	os.system(cmd)
	print "I have just touched the psfkicklist for you :"

print psfkicklist
print "Once you have checked the PSFs (for instance by looking at the pngs),"
print "you should append problematic psf constructions to that list."
print "(Same format as for testlist.txt etc)"
print ""

if makejpgarchives :
	makejpgtgz(pngdir, workdir, askquestions = askquestions)



