#
#	generates pngs from the extracted stars to detect problems
#

execfile("../config.py")
import shutil
from variousfct import *
from kirbybase import KirbyBase, KBError
import f2n



#
#	In a first step we just list the PSFs that have cosmic ray hist
#	Then, if you go on, we make pngs of those images that have cosmic rays
#

execfile("../config.py")
import shutil
from variousfct import *
import f2n
import cosmics
from kirbybase import KirbyBase, KBError

db = KirbyBase()

	# First step : a simple report.
fields = ['imgname','setname', 'stddev', cosmicskey]

report = db.select(imgdb, ['gogogo','treatme',cosmicskey], [True,True,'>0'], fields, sortFields=[cosmicskey], returnType='report')

print "PSFs with cosmic ray hits (%s) :\n" % psfkey
print report

print "(I have also written this into a report file.)"
reporttxtfile = open(workdir + "cosmicsreport_%s.txt" % psfkey, "w")
reporttxtfile.write(report)
reporttxtfile.close()

	
	# Second step

print "\nIn a second step, I will now generate pngs from the above PSFs."
proquest(askquestions)

	# Find how many PSF stars we have
psfstars = readmancat(psfstarcat)
nbrpsf = len(psfstars)

pngkey = "png_" + cosmicskey
pngdir = psfdir + pngkey + "/"

	# Check for existing pngs creation :
if os.path.isdir(pngdir):
	print "I would delete existing stuff."
	proquest(askquestions)
	shutil.rmtree(pngdir)
os.mkdir(pngdir)

	# select images to treat
if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo','treatme',cosmicskey,'testlist'], [True,True,'>0',True], returnType='dict', sortFields=[cosmicskey, 'mjd'])
else :
	images = db.select(imgdb, ['gogogo','treatme',cosmicskey], [True,True,'>0'], returnType='dict', sortFields=[cosmicskey, 'mjd'])

print "I will work on only the %i images that have cosmics." % len(images)
proquest(askquestions)


for i, image in enumerate(images):
	print "- " * 40
	print i+1, "/", len(images), ":", image['imgname']
	
	imgpath = psfdir + image['imgname'] + "/"
	
	#pngname = "%04d.png" % (i+1)
	pngname = image['imgname'] + ".png"
	pngpath = pngdir + pngname
	
	psfimglist=[]
	psfsigimglist=[]
	
	for j in range(nbrpsf):
		
		cosmicsdict = readpickle(os.path.join(imgpath, "cosmicslist%02i.pkl" % (j+1)), verbose=False)
		
		f2nimg = f2n.fromfits(imgpath + "psf%02i.fits" % (j+1), verbose=False)
		f2nimg.setzscale(0, 1)
		f2nimg.makepilimage(scale = "log", negative = False)
		f2nimg.upsample(4)
		f2nimg.drawstarlist(cosmicsdict, r=7.0)
		f2nimg.writeinfo(["psf%02i.fits (%s)" % (j+1, psfstars[j]["name"])])
			
		psfimglist.append(f2nimg)	
		
		
		f2nimg = f2n.fromfits(imgpath + "psfsig%02i.fits" % (j+1), verbose=False)
		f2nimg.setzscale(0, 0.02)
		f2nimg.makepilimage(scale = "log", negative = False)
		f2nimg.upsample(4)
		f2nimg.writeinfo(["psfsig%02i.fits (%s)" % (j+1, psfstars[j]["name"])])
			
		psfsigimglist.append(f2nimg)	
		
		
	
	f2n.compose([psfimglist, psfsigimglist], pngpath)	
	
print "- " * 40

