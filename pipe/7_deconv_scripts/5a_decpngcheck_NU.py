#
#	generates pngs related to the deconvolution
#
import sys
if len(sys.argv) == 2:
	execfile("../config.py")
	decobjname = sys.argv[1]
	deckey = "dec_" + decname + "_" + decobjname + "_" + decnormfieldname + "_" + "_".join(decpsfnames)
	ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
	decskiplist = os.path.join(configdir,deckey + "_skiplist.txt")
	deckeyfilenum = "decfilenum_" + deckey
	deckeypsfused = "decpsf_" + deckey
	deckeynormused = "decnorm_" + deckey
	decdir = os.path.join(workdir, deckey)
	print "You are running the deconvolution on all the stars at once."
	print "Current star : " + sys.argv[1]


else:
	execfile("../config.py")
import shutil
import f2n
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import star




deconvonly = False  # If set to True, I will make pngs only for the deconvolution stamp

if update:
	# override config settings...
	execfile(os.path.join(configdir, 'deconv_config_update.py'))
	askquestions=False
	#print "It takes too long, I skip this step..."
	#sys.exit()
	# nothing more. Let's run on the whole set of images now.

pngkey = deckey + "_png"
pngdir = os.path.join(workdir, pngkey)

if os.path.isdir(pngdir):
	print "Deleting existing stuff."
	proquest(askquestions)
	shutil.rmtree(pngdir)
	
	reflinkdestpath = os.path.join(workdir, deckey + "_ref.png")
	if os.path.exists(reflinkdestpath):
		os.remove(reflinkdestpath)
	
os.mkdir(pngdir)

# Read input positions of point sources, to draw a legend.
ptsrcs = star.readmancat(ptsrccat)
print "Number of point sources :", len(ptsrcs)



db = KirbyBase()
if sample_only :
	print "I will draw the png only for your test sample."
	images = db.select(imgdb, [deckeyfilenum,'testlist'], ['\d\d*',True], returnType='dict', useRegExp=True, sortFields=[deckeyfilenum])
else :
	images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=[deckeyfilenum])


# This time we do not include the duplicated reference !
print "Number of images (we disregard the duplicated reference) : %i" % (len(images))

# Now, just for these pngs, lets put the unique ref image into the first position :
# We select the reference image
refimage = [image for image in images if image['imgname'] == refimgname][0] # we take the first and only element.
# The "others" :
images = [image for image in images if image['imgname'] != refimgname]
# And put the ref into the first positon :
images.insert(0, refimage)





for i, image in enumerate(images):
	
	print "- " * 40
	code = image[deckeyfilenum]
	print i+1, "/", len(images), ":", image['imgname'], code
	
	# We want to look for cosmics. Not that obvious, as we have left all the cosmic detections into the objdirs...
	# We do this in a robust way, i.e. only if we find the required files...
	objkey = "obj_" + decobjname
	cosmicslistpath = os.path.join(workdir, objkey, image['imgname'], "cosmicslist.pkl")
	if os.path.exists(cosmicslistpath):
		cosmicslist = readpickle(cosmicslistpath, verbose=False)
	else:
		cosmicslist = []
		
	# To get the number of cosmics is easier ...
	objcosmicskey = objkey + "_cosmics" # objkey is redefined up there...
	ncosmics = image[objcosmicskey]
	
	pngpath = os.path.join(pngdir, image['imgname'] + ".png")




	if deconvonly:

		f2ndec = f2n.fromfits(os.path.join(decdir, "dec" +code+".fits"), verbose=False)
		f2ndec.setzscale(-20, "auto")
		f2ndec.makepilimage(scale = "exp", negative = False)
		f2ndec.upsample(8)
		#f2ndec.writeinfo(["Deconvolution"])

		decpngpath = os.path.join(pngdir, image['imgname'] + "_deconly.png")
		f2n.compose([[f2ndec]], pngpath)
		continue

	#else...
	f2ndec = f2n.fromfits(os.path.join(decdir, "dec" +code+".fits"), verbose=False)
	f2ndec.setzscale(-20, "auto")
	f2ndec.makepilimage(scale = "log", negative = False)
	f2ndec.upsample(2)
	f2ndec.writeinfo(["Deconvolution"])

	f2ng = f2n.fromfits(os.path.join(decdir, "g" +code+".fits"), verbose=False)
	f2ng.setzscale(-20, "auto")
	f2ng.makepilimage(scale = "log", negative = False)
	f2ng.upsample(4)
	f2ng.drawstarlist(cosmicslist, r=5)
	f2ng.writeinfo(["Input"])
	
	#f2ng.writeinfo(["","g001.fits"])
	
	f2ndec = f2n.fromfits(os.path.join(decdir, "dec" +code+".fits"), verbose=False)
	f2ndec.setzscale(-20, "auto")
	f2ndec.makepilimage(scale = "log", negative = False)
	f2ndec.upsample(2)
	f2ndec.writeinfo(["Deconvolution"])
	
	f2nresi = f2n.fromfits(os.path.join(decdir, "resi" +code+".fits"), verbose=False)
	f2nresi.setzscale(-10, 10)
	f2nresi.makepilimage(scale = "lin", negative = False)
	f2nresi.upsample(2)
	f2nresi.writeinfo(["Residual"])
	
	f2nresi_sm = f2n.fromfits(os.path.join(decdir, "resi_sm" +code+".fits"), verbose=False)
	f2nresi_sm.setzscale(-10, 10)
	f2nresi_sm.makepilimage(scale = "lin", negative = False)
	f2nresi_sm.upsample(2)
	f2nresi_sm.writeinfo(["SM Residual"])
	
	f2nback = f2n.fromfits(os.path.join(decdir, "back" +code+".fits"), verbose=False)
	f2nback.setzscale("ex", "ex")
	f2nback.makepilimage(scale = "lin", negative = False)
	f2nback.upsample(2)
	f2nback.writeinfo(["Background", "Ex : %g %g" % (f2nback.z1, f2nback.z2)])
	
	
	"""
	f2ns = f2n.fromfits(os.path.join(decdir, "s" +code+".fits"), verbose=False)
	f2ns.setzscale(1e-8, "ex")
	f2ns.makepilimage(scale = "log", negative = False)
	f2ns.upsample(2)
	f2ns.writeinfo(["PSF"])
	"""
	
	# let's try to put the PSF in the right shape
	badpsf, h = fromfits(os.path.join(decdir, "s" +code+".fits"), verbose=False)
	goodpsf = np.zeros(badpsf.shape)
	psfsize = 128
	h = psfsize/2
	goodpsf[:h,:h] = badpsf[h:,h:]
	goodpsf[:h,h:] = badpsf[h:,:h]
	goodpsf[h:,:h] = badpsf[:h,h:]
	goodpsf[h:,h:] = badpsf[:h,:h]
	
	f2ns = f2n.f2nimage(numpyarray = goodpsf, verbose=False)
	f2ns.setzscale(1.0e-8, "ex")
	f2ns.makepilimage(scale = "log", negative = False)
	f2ns.upsample(2)
	f2ns.writeinfo(["PSF"])
	
	#legend = f2n.f2nimage(shape = (256,256), fill = 0.0, verbose=False)
	#legend.setzscale(0.0, 1.0)
	#legend.makepilimage(scale = "lin", negative = False)
	
	legend = f2n.f2nimage(shape = (64,64), fill = 0.0, verbose=False)
	legend.setzscale(0.0, 1.0)
	legend.makepilimage(scale = "lin", negative = False)
	legend.upsample(4)
	for ptsrc in ptsrcs:
		print ptsrc.name
		#legend.drawcircle(ptsrc.x, ptsrc.y, r=0.5, colour=255, label=ptsrc.name)
		legend.drawcircle(ptsrc.x, ptsrc.y, r=0.5, colour=255, label=str(ptsrc.name))
	legend.writeinfo(["Legend"])
	
	
	txtendpiece = f2n.f2nimage(shape = (256,256), fill = 0.0, verbose=False)
	txtendpiece.setzscale(0.0, 1.0)
	txtendpiece.makepilimage(scale = "lin", negative = False)

	
	date = image['datet']
	telname = "Instrument : %s" % image["telescopename"]
	seeing = "Seeing : %4.2f [arcsec]" % image['seeing']
	ell = "Ellipticity : %4.2f" % image['ell']
	nbralistars = "Nb alistars : %i" % image['nbralistars']
	airmass = "Airmass : %4.2f" % image['airmass']
	az = "Azimuth : %6.2f [deg]" % image['az']
	# stddev = "Sky stddev : %4.2f [e-]" % image['stddev']
	dkfn = "Deconv file : %s" % code
	ncosmics = "Cosmics : %i" % ncosmics
	selectedpsf = "Selected PSF : %s" % image[deckeypsfused]
	normcoeff = "Norm. coeff : %.3f" % image[deckeynormused]
	
	# we write long image names on two lines ...
	if len(image['imgname']) > 25:
		infolist = [image['imgname'][0:25], image['imgname'][25:]]
	else:
		infolist = [image['imgname']]
	infolist.extend([telname, date, nbralistars, seeing, ell, airmass, dkfn, ncosmics, selectedpsf, normcoeff])
	
	if thisisatest:
		testcomment = 'Testcomment: %s' %image['testcomment']
		infolist.append(testcomment)
	
	
	
	txtendpiece.writeinfo(infolist)
	

	f2n.compose([[f2ng, f2ndec, f2nback, txtendpiece], [f2ns, f2nresi, f2nresi_sm, legend]], pngpath)	
	
	orderlink = os.path.join(pngdir, "%05i.png" % (i+1))
	# WARNING : for the links, we do not use the code !!! We want to start at 0001
	
	os.symlink(pngpath, orderlink)
	
	
	# Before going on with the next image, we build a special link for the ref image (i.e. the first one, in this case) :
	
	if image["imgname"] == refimgname:
		print "This was the reference image."
		sourcepath = pngpath
		destpath = os.path.join(workdir, deckey + "_ref.png")
		copyorlink(sourcepath, destpath, uselinks)
		print "For this special image I made a link into the workdir :"
		print destpath
		print "I would now continue for all the other images."
		
		# We do something similar with the background image as fits :
		copyorlink(os.path.join(decdir, "back0001.fits"), os.path.join(workdir, deckey + "_back.fits"), uselinks)
		# here we use the fact that code 0001 is the duplicated ref image.
		
		proquest(askquestions)
	
print "- " * 40


notify(computer, withsound, "Done.")

print "I've made deconvolution pngs for", deckey
print "Note : for these pngs, the filenames of the links"
print "refer to decfilenums, not to a chronological order ! "

if makejpgarchives :
	makejpgtgz(pngdir, workdir, askquestions = askquestions)



