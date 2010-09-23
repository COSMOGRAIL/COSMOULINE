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
print "(among those, I will automatically skip incomplete psf constructions)"
proquest(askquestions)


for i, image in enumerate(images):
	
	print "- " * 30
	print i+1, image['imgname']
	
	imgpath = psfdir + image['imgname'] + "/"
	
	if not os.path.isfile(imgpath + "mofc.fits"):
		print "no mofc.fits"
		continue # psfm.exe has not worked here so we skip it
	
	pngname = "%04d" % (i+1)
	#pngname = image['imgname']
	
	pngpath = pngdir + pngname
	
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
		
		inputfitspath = imgpath + "psf%02i.fits"%(j+1)
		cosmicslist = readpickle(os.path.join(imgpath, "cosmicslist%02i.pkl" % (j+1)), verbose=False)
		
		
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
		
		inputfitspath = imgpath + "difc%02i.fits"%(j+1)
		
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
		
		inputfitspath = imgpath + "xixi%02i.fits"%(j+1)
		
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
	
	
	
	
	
	f2n.compose([psfstarimglist, difcimglist, xixiimglist, [f2nmofc, f2ns001, f2npsfr, f2nt]], pngpath + "_comp.png")	
	
	
	
	"""
	#cmd = f2n +" p lc " + imgpath + "g.fits" + " " + pngpath + "g.png" + " -30 200"
	#os.system(cmd)
	cmd = f2n +" p lc " + imgpath + "mofc.fits" + " " + pngpath + "mofc.png" + " 0 1e-0"
	os.system(cmd)
	cmd = f2n +" p lc " + imgpath + "psfr.fits" + " " + pngpath + "psfr.png"# + " -5e-2 5e-2"
	os.system(cmd)
	cmd = f2n +" p lc " + imgpath + "difc01.fits" + " " + pngpath + "difc01.png"# + " -5e-2 5e-2"
	os.system(cmd)
	cmd = "mogrify -sample 200% "+ pngpath + "difc01.png"
	os.system(cmd)
	cmd = f2n +" p f " + imgpath + "s001.fits" + " " + pngpath + "s001.png" + " 1e-8 1e-3"
	os.system(cmd)
	cmd = f2n +" p lc " + imgpath + "xixi01.fits" + " " + pngpath + "xixi01.png" + " -4 4"
	os.system(cmd)
	cmd = "mogrify -sample 200% "+ pngpath + "xixi01.png"
	os.system(cmd)
	
	cmd = "montage -background '#333333' " + pngpath + "mofc.png " + pngpath + "s001.png " + pngpath + "psfr.png " + pngpath + "difc01.png " + pngpath + "xixi01.png " + "-geometry +2+2 " + pngpath + "montage.png"
	os.system(cmd)
	
	cmd = "mogrify -sample 200% "+ pngpath + "montage.png"
	os.system(cmd)
	
	#date = image['date'].split('T')
	#date = date[0] + " " + date[1] + " UT"
	date = image['date']
	#scope = image['telescopename'] + " - " + image['setname']
	seeing = "Seeing : %4.2f [arcsec]" % image['seeing']
	ell = "Ellipticity : %4.2f" % image['ell']
	nbralistars = "nbralistars : " + "|"*image['nbralistars']
	imgname = image['imgname']
	geomaprms = "geomap rms : %4.2f [pixel]" % image['geomaprms']
	stddev = "sky stddev : %4.2f [ADU]" % image['stddev']
	rotator = "Rotator : %5.1f [deg]" % image['rotator']
	
	cmd = "convert " + pngpath + "montage.png -font Helvetica-Bold \
	-gravity SouthEast -fill '#DD3333' -annotate +14+14 '"\
	 + imgname + "\n" + date + "\n" + seeing + "\n" + ell + "\n" + geomaprms + "\n" + stddev +\
	  "\n" + nbralistars + "\n" + rotator + "' " + pngpath + "text.png"
	os.system(cmd)
	
	cmd = "convert " + pngpath + "text.png -font Helvetica-Bold \
	-fill '#FFFFFF' \
	-gravity Center -annotate +0+20 'xixi01.fits' \
	-gravity West -annotate +20+20 'difc01.fits' \
	-gravity NorthEast -annotate +20+20 'psfr.fits' \
	-gravity North -annotate +0+20 's001.fits' \
	-gravity NorthWest -annotate +20+20 'mofc.fits' \
	" + pngpath + "text.png"
	
	os.system(cmd)
	     
	os.remove(pngpath + "mofc.png")
	os.remove(pngpath + "psfr.png")
	os.remove(pngpath + "difc01.png")
	os.remove(pngpath + "s001.png")
	os.remove(pngpath + "xixi01.png")
	os.remove(pngpath + "montage.png")
	"""

"""
origdir = os.getcwd()
os.chdir(psfdir)
cmd = "tar cvf " + pngkey + ".tar " + pngkey + "/"
os.system(cmd)
cmd = "mv " + pngkey + ".tar ../."
os.system(cmd)
os.chdir(origdir)
"""

print "Remember : here is the psfkicklist :"
print psfkicklist
print "Look at the pngs and add problematic images."	
	
