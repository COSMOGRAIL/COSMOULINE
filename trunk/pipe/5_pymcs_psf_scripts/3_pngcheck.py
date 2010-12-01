#
#	generates pngs related to the old psf construction
#

execfile("../config.py")
import f2n
import shutil
from kirbybase import KirbyBase, KBError
from variousfct import *
import star


pngdir = os.path.join(workdir, psfkey + "_png")
psfstars = star.readmancat(psfstarcat)
nbrpsf = len(psfstars)

if os.path.isdir(pngdir):
	print "I would delete existing pngs."
	proquest(askquestions)
	shutil.rmtree(pngdir)
os.mkdir(pngdir)

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['mjd'])

print "Number of images :", len(images)
proquest(askquestions)


for i, image in enumerate(images):
	
	print "- " * 30
	print i+1, image['imgname']
	
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	resultsdir = os.path.join(imgpsfdir, "results")
	
	pngpath = os.path.join(pngdir, image['imgname'] + ".png")
	
	
	blank256 = f2n.f2nimage(shape = (256,256), fill = 0.0, verbose=False)
	blank256.setzscale(0.0, 1.0)
	blank256.makepilimage(scale = "lin", negative = False)
	
	
	totpsfimg = f2n.fromfits(os.path.join(resultsdir, "psf_1.fits"), verbose=False)
	totpsfimg.setzscale(1.0e-7, 1.0e-3)
	totpsfimg.makepilimage(scale = "log", negative = False)
	totpsfimg.upsample(2)
	totpsfimg.writetitle("Total PSF")
	
	numpsfimg = f2n.fromfits(os.path.join(resultsdir, "psfnum.fits"), verbose=False)
	numpsfimg.setzscale(-0.02, 0.02)
	numpsfimg.makepilimage(scale = "lin", negative = False)
	numpsfimg.upsample(2)
	numpsfimg.writetitle("Numerical PSF")
	
	
	txtendpiece = f2n.f2nimage(shape = (256,256), fill = 0.0, verbose=False)
	txtendpiece.setzscale(0.0, 1.0)
	txtendpiece.makepilimage(scale = "lin", negative = False)
	
	date = image['datet']
	telname = "Telescope : %s" % image["telescopename"]
	medcoeff = "Medcoeff : %.2f" % image["medcoeff"]
	seeing = "Seeing : %4.2f [arcsec]" % image['seeing']
	ell = "Ellipticity : %4.2f" % image['ell']
	nbralistars = "Nb alistars : %i" % image['nbralistars']
	airmass = "Airmass : %4.2f" % image['airmass']
	az = "Azimuth : %6.2f [deg]" % image['az']
	
	stddev = "Sky stddev : %4.2f [ADU]" % image['stddev']
	skylevel = "Sky level : %7.1f [ADU]" % image['skylevel']
	
	# we write long image names on two lines ...
	if len(image['imgname']) >= 27:
		infolist = [image['imgname'][0:20] + "...", "   " + image['imgname'][20:]]
	else:
		infolist = [image['imgname']]
	infolist.extend([date, telname, medcoeff, seeing, ell, nbralistars, stddev, skylevel, airmass, az])
	
	txtendpiece.writeinfo(infolist)
	
	# The psf stars
	psfstarimglist = []
	for j in range(nbrpsf):
		
		inputfitspath = os.path.join(resultsdir, "star_%03i.fits" % (j+1) )
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale("auto", "auto")
		f2nimg.makepilimage(scale = "log", negative = False)
		f2nimg.upsample(4)
		f2nimg.writetitle("%s" % (psfstars[j].name))
		psfstarimglist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	psfstarimglist.extend([blank256, blank256, blank256])
	psfstarimglist = psfstarimglist[:4]
	psfstarimglist.append(txtendpiece)
	
	# The difcm
	difmlist = []
	for j in range(nbrpsf):
		
		inputfitspath = os.path.join(resultsdir, "difm01_%02i.fits" % (j+1) )
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale(-200, 200)
		f2nimg.makepilimage(scale = "lin", negative = False)
		f2nimg.upsample(4)
		#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
		#f2nimg.writeinfo(["","g001.fits"])
		f2nimg.writetitle("difm01_%02i.fits" % (j+1))
		difmlist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	difmlist.extend([blank256, blank256, blank256])
	difmlist = difmlist[:4]
	difmlist.append(numpsfimg)
	
	# The difg
	difnumlist = []
	for j in range(nbrpsf):
		
		inputfitspath = os.path.join(resultsdir, "difnum%02i.fits" % (j+1) )
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale(-3, 3)
		f2nimg.makepilimage(scale = "lin", negative = False)
		f2nimg.upsample(2)
		#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
		#f2nimg.writeinfo(["","g001.fits"])
		f2nimg.writetitle("difnum%02i.fits" % (j+1))
		difnumlist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	difnumlist.extend([blank256, blank256, blank256])
	difnumlist = difnumlist[:4]
	difnumlist.append(totpsfimg)

	f2n.compose([psfstarimglist, difmlist, difnumlist], pngpath)	
	
print "- " * 30

