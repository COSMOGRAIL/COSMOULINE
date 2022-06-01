#	We look for the ds9 region files, read them, 
#   and mask corresponding regions in the sigma images.
import numpy as np
import sys
import os
import glob 
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
from modules import ds9reg



update = settings['update']
askquestions = settings['askquestions']
refimgname = settings['refimgname']

psfstars = star.readmancat(psfstarcat)


# Select images to treat
db = KirbyBase(imgdb)


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



# Now we help the user with the mask creation.
if refimgname in [img["imgname"] for img in images]:
	
	imgpsfdir = os.path.join(psfdir, refimgname)
	starfiles = sorted(glob.glob(os.path.join(imgpsfdir, "results", "star_*.fits")))
	
	
	print("The stars extracted from the reference image are available here :")
	print("\n".join(starfiles))
	print("You can now open these files with DS9 to build your mask (optional).")
	print("Don't mask cosmics, only companion stars !")
	print("Save your region files respectively here :")
	
	#starfilenames = [os.path.splitext(os.path.basename(s))[0] for s in starfiles]
	
	maskfilepaths = [os.path.join(configdir, "%s_mask_%s.reg" % (psfkey, name)) 
                                        for name in [s.name for s in psfstars]]
	print("\n".join(maskfilepaths))
	
	print("If asked, use physical coordinates and DS9 (or REG) file format.")
else:
	if not update:
		print("By the way, the reference image was not among these images !")
		print("You should always have the reference image in your selection.")

#%%
############################ view each starfile in ds9
if not update:
    text = 5*"\n"
    text += "Now we need to mask our PSF star stamps from contaminant stars.\n"
    text += "Want me to open DS9 on each star so that you can build a mask?\n"
    text += "Btw for each star the path to where the mask needs to be saved\n"
    text += "will be copied to your clipboard.   So, open DS9? (yes/no) "
    if input(text) == 'yes':
        import pyperclip 
        from subprocess import call
        for starfile, maskfile in zip(starfiles, maskfilepaths):
            # copy the mask file to the clipboard:
            pyperclip.copy(maskfile)
            print(f'save your region file to \n{maskfile}')
            # open with ds9
            call(['ds9', starfile])
            # now mask the companion stars in ds9, and save the regions
            # to the file copied in the cilpboard.





############### now masking.
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

