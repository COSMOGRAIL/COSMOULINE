#
#	Simply generates pngs of the raw files that have gogogo set to False.
#	You can launch this whenever you like, it's made to check that rejected images 
#	are indeed useless.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import f2n

pngdir = os.path.join(workdir, "kick_png")

# We check for potential existing stuff :
if os.path.isdir(pngdir):
	print "I will delete existing stuff."
	proquest(askquestions)
	shutil.rmtree(pngdir)
os.mkdir(pngdir)

# We select the images to treat :
db = KirbyBase()
images = db.select(imgdb, ['gogogo'], [False], returnType='dict', sortFields=['setname','mjd'])

print "I will make pngs for %i rejected images." % len(images)
proquest(askquestions)

for i, image in enumerate(images):
	
	print "- " * 40
	print i+1, "/", len(images), ":", image['imgname']

	
	fitsfile = os.path.join(alidir, image['imgname'] + "_ali.fits")
	if not os.path.exists(fitsfile):
		print "You removed the non-aligned images..."
		continue
	
	f2nimg = f2n.fromfits(fitsfile)
	f2nimg.setzscale("auto", "auto", satlevel = 5000000)
	f2nimg.rebin(2)
	f2nimg.makepilimage(scale = "log", negative = False)
	f2nimg.writetitle(image['imgname'])
	
	
	infotextlist = [
	"%s UTC" % image['datet'],
	"Telescope : %s, setname : %s" % (image['telescopename'], image['setname']),
	"Rejection comment : %s" % image["whynot"]
	]
	
	f2nimg.writeinfo(infotextlist)

	pngname = image['imgname'] + ".png"
	pngpath = os.path.join(pngdir, pngname)
	f2nimg.tonet(pngpath)
	
	orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
	os.symlink(pngpath, orderlink)

print "- " * 40

print "The PNG files of the kicked images are written into"
print pngdir

if makejpgarchives :
	makejpgtgz(pngdir, workdir, askquestions = askquestions)

