import glob
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import configdir, settings, psfstarcat, psfkeyflag, imgdb, psfdir,\
                   computer, psfkey
from modules.variousfct import proquest, notify
from modules.kirbybase import KirbyBase
from modules import star, forkmap
from modules.MCS_interface import MCS_interface



maxcores = settings['maxcores']
withsound = settings['withsound']
psfname = settings['psfname']
refimgname = settings['refimgname']
update = settings['update']
askquestions = settings['askquestions']

psfstars = star.readmancat(psfstarcat)


# Select images to treat
db = KirbyBase(imgdb)


if settings['thisisatest'] :
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist' ,psfkeyflag], 
                              [True, True, True, True], 
                              returnType='dict', sortFields=['setname', 'mjd'])
elif settings['update']:
	print("This is an update")
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating', psfkeyflag], 
                              [True, True, True, True],
                              returnType='dict', sortFields=['setname', 'mjd'])
	askquestions = False
else :
	images = db.select(imgdb, ['gogogo', 'treatme', psfkeyflag], 
                              [True, True, True], 
                              returnType='dict', sortFields=['setname', 'mjd'])

print("I will extract the PSF of %i images." % len(images))

ncorestouse = forkmap.nprocessors()
if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print("maxcores = %i" % maxcores)
print("For this I will run on %i cores." % ncorestouse)
proquest(askquestions)


for i, img in enumerate(images):
    # We do not write this into the db, it's just for this particular run.
	img["execi"] = (i+1) 

def extractpsf(image):
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	print("Image %i : %s" % (image["execi"], imgpsfdir))
	
	os.chdir(imgpsfdir)
	mcs = MCS_interface("pyMCS_psf_config.py")
	mcs.set_up_workspace(extract=True, clear=False, backup=False)


for image in images :
    extractpsf(image)
# forkmap.map(extractpsf, images, n = 1)

notify(computer, withsound, "PSF extraction done for psfname %s." % (psfname))
#%%
