#
#	generates pngs related to the old psf construction
#

execfile("../config.py")
import f2n
import shutil
from kirbybase import KirbyBase, KBError
from variousfct import *

pngkey = "png_" + psfkey
pngdir = psfdir + pngkey + "/"

psfstars = readmancat(psfstarcat)
nbrpsf = len(psfstars)

if os.path.isdir(pngdir):
	print "Deleting existing stuff ?"
	proquest(askquestions)
	shutil.rmtree(pngdir)
os.mkdir(pngdir)

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['seeing'])
#images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['mjd'])

print "Number of images :", len(images)
proquest(askquestions)


for i, image in enumerate(images):
	
	print "- " * 30
	print i+1, image['imgname']
	
	imgpath = psfdir + image['imgname'] + "/"
	
	#pngname = "%04d" % (i+1)
	pngname = image['imgname']
	pngpath = os.path.join(pngdir, pngname)
	
	# We prepare a black 192 x 192 image to fill blanks :
	blank = f2n.f2nimage(shape = (192,192), fill = 0.0, verbose=False)
	blank.setzscale(0.0, 1.0)
	blank.makepilimage(scale = "lin", negative = False)
	
	endpiece = f2n.f2nimage(shape = (256,192), fill = 0.0, verbose=False)
	endpiece.setzscale(0.0, 1.0)
	endpiece.makepilimage(scale = "lin", negative = False)
	
	txtendpiece = f2n.f2nimage(shape = (256,192), fill = 0.0, verbose=False)
	txtendpiece.setzscale(0.0, 1.0)
	txtendpiece.makepilimage(scale = "lin", negative = False)
	
	date = image['date']
	seeing = "Seeing : %4.2f [arcsec]" % image['seeing']
	ell = "Ellipticity : %4.2f" % image['ell']
	nbralistars = "Nb alistars : %i" % image['nbralistars']
	airmass = "Airmass : %4.2f" % image['airmass']
	az = "Azimuth : %6.2f [deg]" % image['az']
	
	stddev = "Sky stddev : %4.2f [ADU]" % image['stddev']
	skylevel = "Sky level : %7.1f [ADU]" % image['skylevel']
	
	# we write long image names on two lines ...
	if len(image['imgname']) >= 20:
		infolist = [image['imgname'][0:20] + "...", "   " + image['imgname'][21:]]
	else:
		infolist = [image['imgname']]
	infolist.extend([date, seeing, ell, nbralistars, stddev, skylevel, airmass, az])
	
	txtendpiece.writeinfo(infolist)
	
	# The psf stars
	psfstarimglist = []
	for j in range(nbrpsf):
		
		inputfitspath = imgpath + "results/star%02i.fits"%(j+1)
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale("auto", "auto")
		f2nimg.makepilimage(scale = "log", negative = False)
		f2nimg.upsample(3)
		f2nimg.writetitle("star%02i (%s)" % (j+1, psfstars[j]["name"]))
		psfstarimglist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	psfstarimglist.extend([blank, blank, blank])
	psfstarimglist = psfstarimglist[:4]
	psfstarimglist.append(txtendpiece)
	
	# The difcm
	difmimglist = []
	for j in range(nbrpsf):
		
		inputfitspath = imgpath + "results/difm%02i.fits"%(j+1)
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale(-100, 100)
		f2nimg.makepilimage(scale = "lin", negative = False)
		f2nimg.upsample(3)
		#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
		#f2nimg.writeinfo(["","g001.fits"])
		f2nimg.writetitle("difm%02i (%s)" % (j+1, psfstars[j]["name"]))
		difmimglist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	difmimglist.extend([blank, blank, blank])
	difmimglist = difmimglist[:4]
	difmimglist.append(endpiece)
	
	# The difg
	difgimglist = []
	for j in range(nbrpsf):
		
		inputfitspath = imgpath + "results/difg%02i.fits"%(j+1)
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale(-100, 100)
		f2nimg.makepilimage(scale = "lin", negative = False)
		f2nimg.upsample(3)
		#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
		#f2nimg.writeinfo(["","g001.fits"])
		f2nimg.writetitle("difg%02i (%s)" % (j+1, psfstars[j]["name"]))
		difgimglist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	difgimglist.extend([blank, blank, blank])
	difgimglist = difgimglist[:4]
	difgimglist.append(endpiece)
	
	
	"""
	f2nmofc = f2n.fromfits(imgpath + "mofc.fits", verbose=False)
	f2nmofc.setzscale(0, 1)
	f2nmofc.makepilimage(scale = "log", negative = False)
	f2nmofc.upsample(2) # Now 256 x 256
	#f2nmofc.writeinfo([image['imgname']], (255, 0, 0))
	f2nmofc.writetitle("mofc")
	
	f2nmask = f2n.fromfits(imgpath + "mask.fits", verbose=False)
	f2nmask.setzscale(0.1, 1.1)
	f2nmask.makepilimage(scale = "lin", negative = True)
	f2nmask.upsample(2) # Now 256 x 256
	f2nmask.writetitle("mask")
	
	
	f2ns001 = f2n.fromfits(imgpath + "s001.fits", verbose=False)
	f2ns001.setzscale(1e-7, 0.004)
	f2ns001.makepilimage(scale = "log", negative = False)
	f2ns001.upsample(2) # Now 256 x 256
	f2ns001.writetitle("s")
	
	
	f2npsff = f2n.fromfits(imgpath + "psff.fits", verbose=False)
	f2npsff.setzscale(-0.1, 0.1)
	f2npsff.makepilimage(scale = "lin", negative = False)
	f2npsff.upsample(2) # Now 256 x 256
	f2npsff.writetitle("psff")
	
	f2npsfr = f2n.fromfits(imgpath + "psfr.fits", verbose=False)
	f2npsfr.setzscale(-0.1, 0.1)
	f2npsfr.makepilimage(scale = "lin", negative = False)
	f2npsfr.upsample(2) # Now 256 x 256
	f2npsfr.writetitle("psfr")
	
	f2nt = f2n.fromfits(imgpath + "t.fits", verbose=False)
	f2nt.setzscale(0, 1)
	f2nt.makepilimage(scale = "log", negative = False)
	f2nt.upsample(2) # Now 256 x 256
	f2nt.writetitle("t")
	"""
	
	
	
	
	f2n.compose([psfstarimglist, difmimglist,difgimglist], pngpath + ".png")	
	
	



print "Remember : here is the psfkicklist :"
print psfkicklist
print "Look at the pngs and add problematic images."	
	
