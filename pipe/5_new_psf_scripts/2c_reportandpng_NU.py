#
#	In a first step we just list the PSFs that have cosmic ray hist
#	Then, if you go on, we make pngs of those images that have cosmic rays
#

execfile("../config.py")
import shutil
from variousfct import *
import f2n
import cosmics
import ds9reg
from kirbybase import KirbyBase, KBError

db = KirbyBase()

	# First step : a simple report.
fields = ['imgname','setname', 'stddev', psfcosmicskey]

report = db.select(imgdb, ['gogogo','treatme',psfcosmicskey], [True,True,'>0'], fields, sortFields=[psfcosmicskey], returnType='report')

print "PSFs with cosmic ray hits (%s) :\n" % psfkey
print report

print "(I have also written this into a report file.)"
reporttxtfile = open(os.path.join(workdir, "report_cosmics_%s.txt" % psfkey), "w")
reporttxtfile.write(report)
reporttxtfile.close()

	
	# Second step

print "\nIn a second step, I will now generate pngs from the above PSFs."
proquest(askquestions)

pngkey = psfcosmicskey + "_png"
pngdir = os.path.join(workdir, pngkey)

	# Check for existing pngs creation :
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


	# select images to treat
if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo','treatme',psfcosmicskey,'testlist'], [True,True,'>0',True], returnType='dict', sortFields=[psfcosmicskey, 'mjd'])
else :
	images = db.select(imgdb, ['gogogo','treatme',psfcosmicskey], [True,True,'>0'], returnType='dict', sortFields=[psfcosmicskey, 'mjd'])

print "I will work on only the %i images that have cosmics." % len(images)
proquest(askquestions)


for i, image in enumerate(images):
	print "- " * 40
	print i+1, "/", len(images), ":", image['imgname']
	
	imgpath = os.path.join(psfdir, image['imgname'])
	
	#pngname = "%04d.png" % (i+1)
	pngname = image['imgname'] + ".png"
	pngpath = os.path.join(pngdir, pngname)
	
	# We read the pickle containing the cosmic positions :
	cosmicslist = readpickle(os.path.join(imgpath, "cosmicslist.pkl"), verbose=False)
	#(cosmicsmask, h) = cosmics.fromfits(os.path.join(imgpath, "cosmicsmask.fits"), verbose=False)
	
	
	txtendpiece = f2n.f2nimage(shape = (256,256), fill = 0.0, verbose=False)
	txtendpiece.setzscale(0.0, 1.0)
	txtendpiece.makepilimage(scale = "lin", negative = False)
	
	date = image['date']
	seeing = "Seeing : %4.2f [arcsec]" % image['seeing']
	stddev = "Sky stddev : %4.2f [ADU]" % image['stddev']
	skylevel = "Sky level : %4.2f [ADU]" % image['skylevel']
	nbcosmics = "Cosmics : %i pixels" % image[psfcosmicskey]
	
	# we write long image names on two lines ...
	if len(image['imgname']) > 25:
		infolist = [image['imgname'][0:25], image['imgname'][25:]]
	else:
		infolist = [image['imgname']]
	infolist.extend([date, seeing, stddev, skylevel, nbcosmics])
	
	txtendpiece.writeinfo(infolist)
	
	f2ng001 = f2n.fromfits(os.path.join(imgpath, "g001.fits"), verbose=False) # 128 x 128
	f2ng001.setzscale(-20, 2000)
	f2ng001.makepilimage(scale = "log", negative = False)
	f2ng001.upsample(2) # Now 256 x 256
	f2ng001.drawstarlist(cosmicslist, colour = (255, 0, 0))
	for circle in reg.circles:
		f2ng001.drawcircle(circle["x"], circle["y"], r = circle["r"], colour = (0, 255, 0))
	f2ng001.writeinfo(["g001.fits"])
	
	f2nsig001 = f2n.fromfits(os.path.join(imgpath, "sig001.fits"), verbose=False) # 128 x 128
	f2nsig001.setzscale(0.0, "ex")
	f2nsig001.makepilimage(scale = "lin", negative = False)
	#f2nsig001.drawmask(cosmicsmask > 0.5, colour = (255, 0, 0))
	f2nsig001.upsample(2) # Now 256 x 256
	f2nsig001.writeinfo(["sig001.fits"], colour=(0))
	
	f2n.compose([[f2ng001, f2nsig001, txtendpiece]], pngpath)	
	
	orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
	os.symlink(pngpath, orderlink)
	

print "- " * 40
notify(computer, withsound, "I'm done with pre-PSF pngs for %s." % psfkey)
	
if makejpgarchives :
	makejpgtgz(pngdir, workdir, askquestions = askquestions)

