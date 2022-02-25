#	We look for the ds9 region files, read them, 
#   and mask corresponding regions in the sigma images.
import ds9reg
import numpy as np
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
                   psfkey
from modules.variousfct import proquest, fromfits, tofits
from modules.kirbybase import KirbyBase
from modules import star



update = settings['update']
askquestions = settings['askquestions']

psfstars = star.readmancat(psfstarcat)
# We read the region files

for i, s in enumerate(psfstars):
	print('---------------PSF STAR------------------')
	print(s.name)
	print('-----------------------------------------')

	
	s.filenumber = (i+1)
	possiblemaskfilepath = os.path.join(configdir, f"{psfkey}_mask_{s.name}.reg")
	print('mask file path is: ', possiblemaskfilepath)
	if os.path.exists(possiblemaskfilepath):
		# hardcoded for now 
        # (Warning, can cause a lot of trouble when dealing 
        #  with images other than ECAM)
		s.reg = ds9reg.regions(64, 64) 
		s.reg.readds9(possiblemaskfilepath, verbose=False)
		s.reg.buildmask(verbose = False)
		
		print("You masked %i pixels of star %s." % (np.sum(s.reg.mask), s.name))
	else:
		print("No mask file for star %s." % (s.name))

if not update:
	proquest(askquestions)
		

# Select images to treat
db = KirbyBase()


if settings['thisisatest'] :
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist', psfkeyflag], 
                              [True, True, True, True], 
                              returnType='dict', sortFields=['setname', 'mjd'])
elif settings['update']:
	print("This is an update.")
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating', psfkeyflag], 
                              [True, True, True, True], 
                              returnType='dict', sortFields=['setname', 'mjd'])
	askquestions = False
else :
	images = db.select(imgdb, ['gogogo', 'treatme',psfkeyflag], 
                              [True, True, True], 
                              returnType='dict', sortFields=['setname', 'mjd'])


print("Number of images to treat :", len(images))
proquest(askquestions)


for i, image in enumerate(images):
	
	print("%i : %s" % (i+1, image['imgname']))
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	os.chdir(os.path.join(imgpsfdir, "results"))
			
	for s in psfstars:
		
		if not hasattr(s, 'reg'): # If there is no mask for this star
			continue
		# We modify the sigma image
		sigfilename = "starsig_%03i.fits" % s.filenumber
		(sigarray, sigheader) = fromfits(sigfilename, verbose=False)

		sigarray[s.reg.mask] = 1.0e8
	
		tofits(sigfilename, sigarray, sigheader, verbose=False)
		print('saved !')

print("Done.")

