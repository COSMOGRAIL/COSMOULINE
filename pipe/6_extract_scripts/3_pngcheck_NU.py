#
#	generates pngs of the extracted stuff.
#
import shutil
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings, objkey, objkeyflag, computer, objdir,\
                   objcosmicskey
from modules.variousfct import proquest, notify, readpickle, makejpgtgz
from modules.kirbybase import KirbyBase
from modules import f2n


askquestions = settings['askquestions']
workdir = settings['workdir']
makejpgarchives = settings['makejpgarchives']
withsound = settings['withsound']


# - - - CONFIGURATION - - -

z1 = -20
z2 =  10000

# - - - - - - - - - - - - -

print("You might want to configure the cuts in this script.")
proquest(askquestions)

pngkey = objkey + "_png"
pngdir = os.path.join(workdir, pngkey)

# Check for former png creation :
if os.path.isdir(pngdir):
	print("Deleting existing stuff.")
	proquest(askquestions)
	shutil.rmtree(pngdir)
os.mkdir(pngdir)


# Select images to treat
db = KirbyBase()
if settings['thisisatest'] :
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo', 'treatme', objkeyflag, 'testlist'], 
                              [True, True, True, True], 
                              returnType='dict', 
                              sortFields=['setname', 'mjd'])
else :
	images = db.select(imgdb, ['gogogo', 'treatme', objkeyflag], 
                              [True, True, True], 
                              returnType='dict', 
                              sortFields=['setname', 'mjd'])

print("I will treat %i images." % len(images))
proquest(askquestions)


for i, image in enumerate(images):

	print("- "*40)
	print(i+1, "/", len(images), ":", image['imgname'])
	
	
	# If cosmics are detected, we want to know where :
	cosmicslistpath = os.path.join(objdir, image['imgname'], "cosmicslist.pkl")
	if os.path.exists(cosmicslistpath):
		cosmicslist = readpickle(cosmicslistpath, verbose=False)
	else:
		cosmicslist = []
	# And there number :
	ncosmics = "Cosmics : %i" % image[objcosmicskey]
	
	
	gpath = os.path.join(objdir, image['imgname'], "g.fits")
	sigpath = os.path.join(objdir, image['imgname'], "sig.fits")
	
	# First we build the image for g :
	
	g = f2n.fromfits(gpath, verbose=False)
	g.setzscale(z1, z2)
	g.makepilimage(scale = "log", negative = False)
	g.upsample(4)
	g.drawstarlist(cosmicslist)
	g.writetitle("g.fits")
	
	
	# We write long image names on two lines ...
	if len(image['imgname']) > 25:
		infolist = [image['imgname'][0:25], image['imgname'][25:]]
	else:
		infolist = [image['imgname']]
	g.writeinfo(infolist)
	
	# And now for sig :
	
	sig = f2n.fromfits(sigpath, verbose=False)
	sig.setzscale("ex", "ex")
	sig.makepilimage(scale = "log", negative = False)
	sig.upsample(4)
	sig.writetitle("sig.fits", colour=(0))
	
	sig.writeinfo([ncosmics], colour=(0))
	
	
	pngname = image['imgname'] + ".png"
	pngpath = os.path.join(pngdir, pngname)
	f2n.compose([[g, sig]], pngpath)

    # a link to get the images sorted for the movies etc:
	orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) 
	os.symlink(pngpath, orderlink)


print("- "*40)
notify(computer, withsound, "I made PNGs for %s." % objkey)

if makejpgarchives :
	makejpgtgz(pngdir, workdir, askquestions=askquestions)


