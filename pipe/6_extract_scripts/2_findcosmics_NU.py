#	We use cosmics.py to locate cosmics in the g001.fits images.
#	We do not clean them, but mask them in the sig001.fits.
#	The database is updated with the number of cosmic rays found.
#
#	It is ok to relauch this script : 
#		- I will reset the database entry
#		- Erase any previous files
#		- Apply my mask on the original sigma image.
#
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
from config import imgdb, settings, computer
from modules.variousfct import proquest, notify, writepickle
from modules.kirbybase import KirbyBase
from modules import cosmics

askquestions = settings['askquestions']
cosmicssigclip = settings['cosmicssigclip']
withsound = settings['withsound']

def maskCosmics(objkey, objkeyflag, objdir):

    # Select images to treat
    db = KirbyBase()
    images = db.select(imgdb, ['gogogo', 'treatme', objkeyflag], 
                              [True, True, True], 
                              returnType='dict', 
                              sortFields=['setname', 'mjd'])
    print("Number of images to analyse for cosmics: ", len(images))
    print("You have set cosmicssigclip to %f" % cosmicssigclip)
    proquest(askquestions)
    
    
    
    
    # Remember where we are
    origdir = os.getcwd()
    
    for i, image in enumerate(images):
    	print(i+1, "/", len(images), ":", image['imgname'])
    	imgobjdir = os.path.join(objdir, image['imgname'])
    	os.chdir(imgobjdir)
    	
    	
    	# We reset everyting :
    	if os.path.isfile("cosmicsmask.fits"):
    		os.remove("cosmicsmask.fits")
    	if os.path.isfile("cosmicslist.pkl"):
    		os.remove("cosmicslist.pkl")
    	if os.path.isfile("orig_sig.fits"):
    		# Then we reset the original sigma image :
    		if os.path.isfile("sig.fits"):
    			os.remove("sig.fits")
    		os.rename("orig_sig.fits", "sig.fits")
    		
    	# We read array and header of that fits file :
    	(a, h) = cosmics.fromfits("g.fits", verbose=False)
    	
    	# We gather some parameters :
    	
    	pssl = image['skylevel'] # The Previously Subtracted Sky Level
    	print("PSSL (TM): %.2f" % pssl)
    	gain = image['gain']
    	readnoise = image['readnoise']
    	
    	sigclip = cosmicssigclip
    	sigfrac = 0.3
    	objlim = 3.0
    	
    	# Creating the object :
    	c = cosmics.cosmicsimage(a, pssl=pssl, 
                                    gain=gain, 
                                    readnoise=readnoise, 
                                    sigclip=sigclip, 
                                    sigfrac=sigfrac, 
                                    objlim=objlim, 
                                    satlevel=-1.0, 
                                    verbose=False)
    	# negative satlevel : we do not look for saturated stars
    	
    	
    	
    	# Ok let's try a full run :
    	c.run(maxiter=3)
    	
    	ncosmics = np.sum(c.mask)
    	
    	if ncosmics != 0:
    		print(f"--- {ncosmics} pixels ---")
    	
    	# We do the rest anyway (easier): 
    	
    	# We write the mask :
    	cosmics.tofits("cosmicsmask.fits", c.getdilatedmask(size=5), 
                       verbose=False)
    		
    	# And the labels (for later png display) :
    	cosmicslist = c.labelmask()
    	writepickle(cosmicslist, "cosmicslist.pkl", verbose=False)
    		
    	# We modify the sigma image, but keep a copy of the original :
    	os.rename("sig.fits", "orig_sig.fits")
    	(sigarray, sigheader) = cosmics.fromfits("orig_sig.fits", 
                                                 verbose=False)
        # again, it's inverted, hence the minus: 
    	sigarray[c.getdilatedmask(size=5)] = 1.0e-8 
    	cosmics.tofits("sig.fits", sigarray, sigheader, verbose=False)
    	
    	# We write the number of cosmics in the database :
    	# No, this is too slow, not worth it.
    	#db.update(imgdb, ['recno'], [image['recno']], 
        #                 {objcosmicskey: int(ncosmics)})
    
    	os.chdir(origdir)
    
    # Not needed if we do not write the number of comsics
    #db.pack(imgdb) # To erase the blank lines
    
    notify(computer, withsound, f"Done with masking cosmics for {objkey}")
	
if __name__ == "__main__":
    from config import objkey, objkeyflag, objdir
    maskCosmics(objkey, objkeyflag, objdir)
