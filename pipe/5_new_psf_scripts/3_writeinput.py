#
#	We write the input file of the new F77 MCS psf,
#	psfmofsour8.txt
#	one file for each image directory.
#
#	Here would be the place to set some parameters automatically according to seeing etc.
#
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *

# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['setname', 'mjd'])


print "I will treat %i images." % len(images)
proquest(askquestions)

# How many PSFs do we have and what are their fluxes ?
psfstars = readmancat(psfstarcat) # So at this point, if a flux was specified in the file, the stars have these fluxes.
					# if not, fluxes are set to -1.0 and the loop will stop.
nbrpsf = len(psfstars)
if nbrpsf > 4:

	print "You have given more than 4 PSFs."
	print "Not sure if I can handle this... we'll see."
	#raise mterror("I can't handle more than 4 PSFs !")
	proquest(askquestions)


# Read the template file
psf_template = justread(psf_template_filename)



for n, image in enumerate(images):
	print "- " * 40
	print n+1, "/", len(images), ":", image['imgname']

	imgpsfdir = os.path.join(psfdir, image['imgname'])

	# === Calculation of input parameters ===
		
	print "seeingpixels :", image["seeingpixels"]
	
	resolpix = 1.2 * image["seeingpixels"]	# 1.2
	print "resolpix :", resolpix
	
	# Preparation of the last lines of the input file = the "sources"
	
	paramsrc = ""
	for i, psfstar in enumerate(psfstars):
		if psfstar["flux"] < 0.0:
			raise mterror("Star has a negative flux... add flux as 4th col into the psfstarcat !")
		
		# Else, we calculate the intensity-that-nobody-knows-how-to-calculate-it for the F77 MCS.
		# It seems that a good value is 1.45 * the flux of the star as measured for instance with IRAF.
		# By flux I mean the sum of the pixels, or integral below the star, and not the peak value.
		# I add a 0.9 factor, to keep some "movement" in the optimization.
		
		#stupint = 1.45*0.9*(psfstar['flux'] / image['medcoeff'])
		stupint = 1.5*(psfstar['flux'] / image['medcoeff'])
		
		# Indeed coeff is defined by "coeff = reference / star"
		# So star = ref / coeff
		
		paramsrc = paramsrc + " %f\n" % stupint
		print "stupint :", stupint
		#paramsrc = paramsrc + "%7.2f %7.2f\n" % (psfstar[1], psfstar[2])
		
		if i == 0:
			paramsrc = paramsrc + " %4.1f\t%4.1f\n" % (33.5, 33.5)
		if i == 1:
			paramsrc = paramsrc + " %4.1f\t%4.1f\n" % (97.5, 33.5)
		if i == 2:
			paramsrc = paramsrc + " %4.1f\t%4.1f\n" % (33.5, 97.5)
		if i == 3:
			paramsrc = paramsrc + " %4.1f\t%4.1f\n" % (97.5, 97.5)
		
	paramsrc = paramsrc.rstrip("\n") # remove the last newline
	
	# A dictionnary of the info that will be written into the input file :
	psfdict = {"$nbrpsf$": str(nbrpsf), "$resolpix$": str(resolpix), "$paramsrc$": paramsrc}
	
	# We write the file :
	psfmofsour8txt = justreplace(psf_template, psfdict)
	psfmofsour8file = open(os.path.join(imgpsfdir,"psfmofsour8.txt"), "w")
	psfmofsour8file.write(psfmofsour8txt)
	psfmofsour8file.close()
	

print "I'm done, we are ready to launch the PSF construction."

