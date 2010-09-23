#
#	make some pngs out of some images in some dir
#
#

import os
import sys
from glob import glob

filepath = "/home/epfl/tewes/DECONV/J1001/prered/"


os.chdir(filepath)
filenames = sorted(glob("*.fits"))

for filename in filenames:
	print "-"*40
	print filename
	
	#if "flip" in filename:
	#	continue
	
	infile = filename
	pngfile = filename.split('.')[0]+".png"
	
	# normalized flats
	#os.system('f2n_linux p lc ' + infile + ' ' + pngfile + ' 0.9 1.1')
	
	# star images
	os.system('f2n_linux p f ' + infile + ' ' + pngfile + ' a a')
	
	# be careful please not to modify the fits file !
	os.system("mogrify -sample 50% "+ pngfile)

	os.system("convert " + pngfile + " -font Helvetica-Bold -pointsize 20 -fill '#FFFFFF' -gravity North -annotate +0+20 '" + filename + "' " + pngfile)

