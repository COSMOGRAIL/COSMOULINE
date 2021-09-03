"""
Facultative
This script prealign the images
It avoids them to be stupidly aligned and cut when you align them
"""


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
import shutil
import os, sys
import numpy as np

db = KirbyBase()



images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

print("I will treat %i images." % len(images))
proquest(askquestions)

images = sorted(images, key=lambda image: image["imgname"])

xpattern = [0, 1, 2, 2, 2, 1, 1, 0, 0, -1, -2, -2, -1, -1, -2, -2, -2, -1, 0, 1, 2, 2, 1, 0, -1]
ypattern = [0, 0, 0, -1, -2, -2, -1, -1, -2, -2, -2, -1, -1, 0, 0, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1]
pixshift = 207

assert len(xpattern) == len(ypattern)
assert len(images) == len(xpattern)

for n, (image, x, y) in enumerate(zip(images, xpattern, ypattern)):
	print(n+1, "/", len(images), ":", image['imgname'])
	skysubimg = os.path.join(alidir, image["imgname"] + "_skysub.fits")

	(img, hdr) = fromfits(skysubimg, verbose=True)

	maxext = max(len(img), len(img[0]))/2
	newarray = np.zeros((2*maxext+len(img), 2*maxext+len(img[0])))


	for i in np.arange(len(img)):
		for j in np.arange(len(img[0])):
			newarray[i+maxext-x*pixshift][j+maxext-y*pixshift] = img[i][j]

	#tofits('test.fits', newarray, hdr=hdr)
	#sys.exit()
	tofits(skysubimg, newarray, hdr=hdr)

