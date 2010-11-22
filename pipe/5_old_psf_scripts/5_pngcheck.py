#
#	generates pngs related to the old psf construction
#

execfile("../config.py")
import f2n
import shutil
from kirbybase import KirbyBase, KBError
from variousfct import *


pngdir = psfdir + "_png"

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
print "(among those, I will automatically skip incomplete psf constructions)"
proquest(askquestions)


for i, image in enumerate(images):
	
	print "- " * 30
	print i+1, image['imgname']
	
	imgpath = os.path.join(psfdir, image['imgname'])
	
	if not os.path.isfile(os.path.join(imgpath,"mofc.fits")):
		print "no mofc.fits"
		continue # psfm.exe has not worked here so we skip it
	
	#pngname = "%05d.png" % (i+1)
	pngname = image['imgname'] + ".png"
	
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
	
	# we write long image names on two lines ...
	if len(image['imgname']) >= 20:
		infolist = [image['imgname'][0:20] + "...", "   " + image['imgname'][21:]]
	else:
		infolist = [image['imgname']]
	infolist.extend([date, seeing, ell, nbralistars, stddev, airmass, az])
	
	txtendpiece.writeinfo(infolist)
	
	# The psf stars
	psfstarimglist = []
	for j in range(nbrpsf):
		
		inputfitspath = os.path.join(imgpath, "psf%02i.fits"%(j+1))
		if os.path.isfile(os.path.join(imgpath, "cosmicslist%02i.pkl" % (j+1))):
			cosmicslist = readpickle(os.path.join(imgpath, "cosmicslist%02i.pkl" % (j+1)), verbose=False)
		else :
			cosmicslist = []
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale(0, 1)
		f2nimg.makepilimage(scale = "log", negative = False)
		f2nimg.upsample(3)
		f2nimg.drawstarslist(cosmicslist)
		#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
		#f2nimg.writeinfo(["","g001.fits"])
		f2nimg.writetitle("psf%02i (%s)" % (j+1, psfstars[j]["name"]))
		psfstarimglist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	psfstarimglist.extend([blank, blank, blank])
	psfstarimglist = psfstarimglist[:4]
	psfstarimglist.append(txtendpiece)
	
	# The difcs
	difcimglist = []
	for j in range(nbrpsf):
		
		inputfitspath = os.path.join(imgpath, "difc%02i.fits"%(j+1))
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale(-0.1, 0.1)
		f2nimg.makepilimage(scale = "lin", negative = False)
		f2nimg.upsample(3)
		#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
		#f2nimg.writeinfo(["","g001.fits"])
		f2nimg.writetitle("difc%02i (%s)" % (j+1, psfstars[j]["name"]))
		difcimglist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	difcimglist.extend([blank, blank, blank])
	difcimglist = difcimglist[:4]
	difcimglist.append(endpiece)
	
	# The xixis
	xixiimglist = []
	for j in range(nbrpsf):
		
		inputfitspath = os.path.join(imgpath, "xixi%02i.fits"%(j+1))
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale(-6.0, 6.0)
		f2nimg.makepilimage(scale = "lin", negative = False)
		f2nimg.upsample(3)
		#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
		#f2nimg.writeinfo(["","g001.fits"])
		f2nimg.writetitle("xixi%02i (%s)" % (j+1, psfstars[j]["name"]))
		xixiimglist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	xixiimglist.extend([blank, blank, blank])
	xixiimglist = xixiimglist[:4]
	xixiimglist.append(endpiece)
	
	
	
	f2nmofc = f2n.fromfits(os.path.join(imgpath, "mofc.fits"), verbose=False)
	f2nmofc.setzscale(0, 1)
	f2nmofc.makepilimage(scale = "log", negative = False)
	f2nmofc.upsample(2) # Now 256 x 256
	#f2nmofc.writeinfo([image['imgname']], (255, 0, 0))
	f2nmofc.writetitle("mofc")
	
	f2nmask = f2n.fromfits(os.path.join(imgpath, "mask.fits"), verbose=False)
	f2nmask.setzscale(0.1, 1.1)
	f2nmask.makepilimage(scale = "lin", negative = True)
	f2nmask.upsample(2) # Now 256 x 256
	f2nmask.writetitle("mask")
	
	
	f2ns001 = f2n.fromfits(os.path.join(imgpath, "s001.fits"), verbose=False)
	f2ns001.setzscale(1e-7, 0.004)
	f2ns001.makepilimage(scale = "log", negative = False)
	f2ns001.upsample(2) # Now 256 x 256
	f2ns001.writetitle("s")
	
	
	f2npsff = f2n.fromfits(os.path.join(imgpath, "psff.fits"), verbose=False)
	f2npsff.setzscale(-0.1, 0.1)
	f2npsff.makepilimage(scale = "lin", negative = False)
	f2npsff.upsample(2) # Now 256 x 256
	f2npsff.writetitle("psff")
	
	f2npsfr = f2n.fromfits(os.path.join(imgpath, "psfr.fits"), verbose=False)
	f2npsfr.setzscale(-0.1, 0.1)
	f2npsfr.makepilimage(scale = "lin", negative = False)
	f2npsfr.upsample(2) # Now 256 x 256
	f2npsfr.writetitle("psfr")
	
	f2nt = f2n.fromfits(os.path.join(imgpath, "t.fits"), verbose=False)
	f2nt.setzscale(0, 1)
	f2nt.makepilimage(scale = "log", negative = False)
	f2nt.upsample(2) # Now 256 x 256
	f2nt.writetitle("t")
	
	
	f2n.compose([psfstarimglist, difcimglist, xixiimglist, [f2nmofc, f2ns001, f2npsfr, f2nt]], pngpath)	
	
	

print "Remember : here is the psfkicklist :"
print psfkicklist
print "Look at the pngs and add problematic images."	
	
