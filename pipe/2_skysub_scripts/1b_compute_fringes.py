#
#	Create an image of the fringes
#
import numpy as np
from astropy.time import Time
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import alidir, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import fromfits, proquest, tofits
from datetime import datetime


askquestions = settings['askquestions']
workdir = settings['workdir']


db = KirbyBase()


def sigmaclipandreplace(data, sigmas=[0.5, 1.2], nit=2):

	print("="*30)
	for i in np.arange(nit):
		median = np.nanmedian(data)
		std = np.nanstd(data)
		print("Iteration %i: median=%.2f, std=%.2f" % (i+1, median, std))
		if len(sigmas) == 1:
			sigma=sigmas[0]
		else:
			sigma=sigmas[i]
		data[data > median+sigma*std] = median
		data[data < median-sigma*std] = median

	return data

def getobsnight(image):
	"""
	give me a datet object "YYYY-MM-DD HH:MM:SS"
	I return the night of the observation
	i.e if HH:MM:SS < ~15h UT, then it's the previous night (being on the safe side)

	A proper implementation would be to use the combibynight_fct module, but for now this will do the trick
	"""

	isodatet = ' '.join(image["datet"].split('T'))
	mjdobs = Time(isodatet, format='iso', scale='utc').mjd

	if mjdobs - int(mjdobs) < 0.63:
		mjdn = int(mjdobs)
	else:
		mjdn = int(mjdobs) + 1
	obsnight = Time(mjdn, format='mjd', scale='utc').iso.split(' ')[0]
	# we add the nightobs field, but only for this script
	image["obsnight"] = obsnight
	return obsnight


usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])

for setname in usedsetnames:

    if settings['thisisatest']:
    	print("This is a test run.")
    	images = db.select(imgdb, ['gogogo','treatme','testlist', 'setname'], 
                                  [True, True, True, setname], returnType='dict')
    elif settings['update']:
    	print("This is an update.")
    	images = db.select(imgdb, ['gogogo','treatme','updating', 'setname'], 
                                  [True, True, True, setname], returnType='dict')
    	askquestions = False
    else:
    	images = db.select(imgdb, ['gogogo','treatme', 'setname'], 
                                  [True, True, setname], returnType='dict')
    
    
    nbrimages = len(images)
    print("Number of images to treat :", nbrimages)
    proquest(False)
    
    starttime = datetime.now()
    obsnights = sorted(list(set([getobsnight(image) for image in images])))
    
    for obsnight in obsnights:
    
    	#if obsnight != '2016-11-10':
    		#continue
    	print("="*15, obsnight, "="*15)
    
    	nightimages = [image for image in images if image["obsnight"] == obsnight]
    
    	imageas = []
    	print("I'm working on %i images" % len(nightimages))
    	for image in nightimages:
    
    		imagepath = os.path.join(alidir, image["imgname"] + "_skysub.fits")
    		(imagea, imageh) = fromfits(imagepath, verbose=False)
    		print(imagea.shape)
    		clippeda = sigmaclipandreplace(imagea, sigmas=[0.5, 1.2], nit=2)
    		imageas.append(clippeda)
    		#tofits(os.path.join(alidir, image["imgname"] + "_clipped.fits"), clippeda)
    
    	fringes = np.median(imageas, axis=0)
    
    	if not os.path.isdir(os.path.join(workdir, 'fringes')):
    		os.mkdir(os.path.join(workdir, 'fringes'))
    
    	#fpath = os.path.join(workdir, 'fringes_%s.fits' % gender)
    	fpath = os.path.join(workdir, 'fringes', '%s.fits' % str(obsnight))
    	if os.path.isfile(fpath):
    		os.system('rm %s' % fpath)
    	tofits(fpath, fringes)
    
    
    	for image in nightimages:
    		imagepath = os.path.join(alidir, image["imgname"] + "_skysub.fits")
    		(imagea, imageh) = fromfits(imagepath, verbose=False)
    		imageadf = imagea - fringes + np.nanmedian(fringes)
    		#tofits("ftest/%s_withfringes.fits" % image["imgname"], imagea, imageh)
    		tofits(os.path.join(alidir, image["imgname"] + "_defringed.fits"), imageadf, imageh)

