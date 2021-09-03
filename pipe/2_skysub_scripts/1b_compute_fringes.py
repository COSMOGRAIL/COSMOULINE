#
#	Create an image of the fringes
#


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
import shutil
import os
import numpy as np
from astropy.time import Time


db = KirbyBase()
if thisisatest:
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo','treatme','testlist'], [True, True, True], returnType='dict')
elif update:
	print("This is an update.")
	images = db.select(imgdb, ['gogogo','treatme','updating'], [True, True, True], returnType='dict')
	askquestions = False
else:
	images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')


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

