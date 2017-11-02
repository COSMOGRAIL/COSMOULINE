#
#	generates overview pngs related to the pyMCS psf construction
#	NEW : add a imgname to jpgnumber report, to help the construction of the skiplist
#

execfile("../config.py")
import f2n
import shutil
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import ds9reg


pngdir = os.path.join(workdir, psfkey + "_png")
psfstars = star.readmancat(psfstarcat)
nbrpsf = len(psfstars)



# We read the mask files :
for i, s in enumerate(psfstars):
	
	s.filenumber = (i+1)
	possiblemaskfilepath = os.path.join(configdir, "%s_mask_%s.reg" % (psfkey, s.name))
	if os.path.exists(possiblemaskfilepath):
		
		s.reg = ds9reg.regions(64, 64) # hardcoded for now ...
		s.reg.readds9(possiblemaskfilepath, verbose=False)
		s.reg.buildmask(verbose = False)
		
		# print "You masked %i pixels of star %s." % (np.sum(s.reg.mask), s.name)
	else:
		# print "No mask file for star %s." % (s.name)
		pass



db = KirbyBase()

if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
elif update:
	print "This is an update."
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	askquestions=False
else :
	images = db.select(imgdb, ['gogogo', 'treatme',psfkeyflag], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])


if update:
	print "I will complete the existing sky folder. Or recreate it if you deleted it to save space"
	if not os.path.isdir(pngdir):
		os.mkdir(pngdir)

else:
	if os.path.isdir(pngdir):
		print "I will delete existing stuff."
		proquest(askquestions)
		shutil.rmtree(pngdir)
	os.mkdir(pngdir)





print "Something very special here : I do already look at the psfskiplist, so that I don't crash even if some of your pyMCS PSFs are broken."
if os.path.exists(psfkicklist):
	psfskipimages = [image[0] for image in readimagelist(psfkicklist)] # image[1] would be the comment
	print "It contains %i images." % len(psfskipimages)

	images = [image for image in images if image["imgname"] not in psfskipimages]
else:
	print "No skiplist."


print "Number of images :", len(images)
proquest(askquestions)


reportpath = os.path.join(workdir, "report_" + psfkey)
report = open(reportpath,'w')

for i, image in enumerate(images):
	
	print "- " * 30
	print i+1, image['imgname']
	toreport = str(image['imgname'])+'\t' + str(i+1)
	report.write(toreport)
	
	
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	resultsdir = os.path.join(imgpsfdir, "results")
	
	pngpath = os.path.join(pngdir, image['imgname'] + ".png")
	
	
	blank256 = f2n.f2nimage(shape = (256,256), fill = 0.0, verbose=False)
	blank256.setzscale(0.0, 1.0)
	blank256.makepilimage(scale = "lin", negative = False)
	
	
	totpsfimg = f2n.fromfits(os.path.join(resultsdir, "psf_1.fits"), verbose=False)
	#totpsfimg.rebin(2)
	totpsfimg.setzscale(1.0e-7, 1.0e-3)
	totpsfimg.makepilimage(scale = "log", negative = False)
	totpsfimg.upsample(2)
	totpsfimg.writetitle("Total PSF")
	
	numpsfimg = f2n.fromfits(os.path.join(resultsdir, "psf_num_1.fits"), verbose=False)
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

	if thisisatest:
		testcomment = 'Testcomment: %s' %image['testcomment']
		infolist.append(testcomment)

	
	txtendpiece.writeinfo(infolist)
	
	
	# The psf stars
	psfstarimglist = []
	for j in range(nbrpsf):
		
		inputfitspath = os.path.join(resultsdir, "star_%03i.fits" % (j+1) )
		starcosmicspklfilepath = os.path.join(resultsdir, "starcosmics_%03i.pkl" % (j+1))
		
		if os.path.exists(starcosmicspklfilepath):
			cosmicslist = readpickle(starcosmicspklfilepath, verbose=False)
		else:
			cosmicslist = []
		
		
			
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale("auto", "auto")
		f2nimg.makepilimage(scale = "log", negative = False)
		f2nimg.upsample(4)
		f2nimg.drawstarlist(cosmicslist, r=3)
		if hasattr(psfstars[j], "reg"):
			for circle in psfstars[j].reg.circles:
				f2nimg.drawcircle(circle["x"], circle["y"], r = circle["r"], colour = (170))
		f2nimg.writetitle("%s" % (psfstars[j].name))
		psfstarimglist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	#psfstarimglist.extend([blank256, blank256, blank256])
	#psfstarimglist = psfstarimglist[:4]
	psfstarimglist.append(blank256)
	
	
	# The sigmas
	sigmaimglist = []
	for j in range(nbrpsf):
		
		inputfitspath = os.path.join(resultsdir, "starsig_%03i.fits" % (j+1) )
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale(0, 1.0e3)
		f2nimg.makepilimage(scale = "log", negative = False)
		f2nimg.upsample(4)
		#f2nimg.drawstarlist(cosmicslist, r=10)
		#f2nimg.writetitle("%s" % (psfstars[j].name))
		sigmaimglist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	#sigmaimglist.extend([blank256, blank256, blank256, blank256])
	#sigmaimglist = sigmaimglist[:5]
	#sigmaimglist.append(txtendpiece)
	sigmaimglist.append(txtendpiece)
	
	# The difcm
	difmlist = []
	for j in range(nbrpsf):
	
		starmaskfilepath =  os.path.join(resultsdir, "starmask_%03i.fits" % (j+1) )
		inputfitspath = os.path.join(resultsdir, "difmof01_%02i.fits" % (j+1) )
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		
		if os.path.exists(starmaskfilepath):
			(mask, h) = fromfits(starmaskfilepath, verbose = False)
			f2nimg.numpyarray[mask > 0.5] = 0.0
		
		f2nimg.setzscale(-0.1, 0.1)
		f2nimg.makepilimage(scale = "lin", negative = False)
		f2nimg.upsample(4)
		#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
		#f2nimg.writeinfo(["","g001.fits"])
		if hasattr(psfstars[j], "reg"):
			for circle in psfstars[j].reg.circles:
				f2nimg.drawcircle(circle["x"], circle["y"], r = circle["r"], colour = (255))
		
		f2nimg.writetitle("dif mof %02i" % (j+1))
		difmlist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	#difmlist.extend([blank256, blank256, blank256])
	#difmlist = difmlist[:4]
	difmlist.append(numpsfimg)
	
	# The difnums
	difnumlist = []
	for j in range(nbrpsf):
		
		inputfitspath = os.path.join(resultsdir, "difnum01_%02i.fits" % (j+1) )
		
		f2nimg = f2n.fromfits(inputfitspath, verbose=False)
		f2nimg.setzscale(- 0.0025, 0.0025)
		f2nimg.makepilimage(scale = "lin", negative = False)
		f2nimg.upsample(2)
		#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
		#f2nimg.writeinfo(["","g001.fits"])
		f2nimg.writetitle("dif num %02i" % (j+1))
		difnumlist.append(f2nimg)
	
	# We fill with blanks and cut at 4 images :
	#difnumlist.extend([blank256, blank256, blank256])
	#difnumlist = difnumlist[:4]
	difnumlist.append(totpsfimg)

	#for a in difnumlist:
	#	print a
		

	f2n.compose([psfstarimglist, sigmaimglist, difmlist, difnumlist], pngpath)	

	if not update:
		orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
		os.symlink(pngpath, orderlink)
	


if update:  # remove all the symlink and redo it again with the new images
	allimages = db.select(imgdb, ['gogogo', 'treatme',psfkeyflag], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	for i, image in enumerate(allimages):
		pngpath = os.path.join(pngdir, image['imgname'] + ".png")
		orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
		try:
			os.unlink(orderlink)
		except:
			pass
		os.symlink(pngpath, orderlink)

print "- " * 30
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

print pngdir

if makejpgarchives :
	makejpgtgz(pngdir, workdir, askquestions = askquestions)
