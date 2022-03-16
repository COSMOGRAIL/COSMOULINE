#	We look for the ds9 region files, read them, and mask corresponding regions in the original images !!.
#	Useful only with a small number of psf stars, very polluted (i.e. space images such HST images)


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
import cosmics # used to read and write the fits files
import ds9reg
import glob
import numpy as np
import star
import sys
psfstars = star.readmancat(psfstarcat)
# We read the region files


for i, s in enumerate(psfstars):
	
	s.filenumber = (i+1)
	possiblemaskfilepath = os.path.join(configdir, "%s_mask_%s.reg" % (psfkey, s.name))
	if os.path.exists(possiblemaskfilepath):
		
		s.reg = ds9reg.regions(128, 128) # hardcoded for now # THIS IS BAD MALTE, THIS IS BAD !!!!! 
		s.reg.readds9(possiblemaskfilepath, verbose=False)
		s.reg.buildmask(verbose = False)
		
		print("You masked %i pixels of star %s." % (np.sum(s.reg.mask), s.name))
	else:
		print("No mask file for star %s." % (s.name))

#proquest(askquestions)
		

# Select images to treat
db = KirbyBase()


if thisisatest :
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
else :
	images = db.select(imgdb, ['gogogo', 'treatme',psfkeyflag], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])


print("Number of images to treat :", len(images))
#proquest(askquestions)



# easy way, replace eveything masked by 0:
if 0:
	for i, image in enumerate(images):

		print("%i : %s" % (i+1, image['imgname']))
		imgpsfdir = os.path.join(psfdir, image['imgname'])
		os.chdir(os.path.join(imgpsfdir, "results"))

		for s in psfstars:

			if not hasattr(s, 'reg'): # If there is no mask for this star
				continue
			# We modify the original extracted stamps
			orifilename = "/home/epfl/vbonvin/DECONV/0435/pymcs/results/star_%03i.fits" % s.filenumber # alternative directory, for a specific case
			#orifilename = "star_%03i.fits" % s.filenumber # original directory 
			(oriarray, oriheader) = fromfits(orifilename, verbose=False)

			''' # tests
			oriarray2=oriarray
			oricopy=[]
			for l2,l3 in zip(oriarray,oriarray2):

				oricopy.append([np.median([l2e,l3e]) for l2e,l3e in zip(l2,l3)])	
			
			sys.exit()
			'''
			oriarray[s.reg.mask] = 0

			tofits(orifilename, oriarray, oriheader, verbose=False)
			print('saved !')

# hard (smarter) way, replace everythink masked by the median of the other stars (if any), or by 0 otherwise.

if 1:
	for i, image in enumerate(images):

		print("%i : %s" % (i+1, image['imgname']))
		imgpsfdir = os.path.join(psfdir, image['imgname'])
		os.chdir(os.path.join(imgpsfdir, "results"))
		
		orifilenames = []
		oriarrays = []
		oriheaders = []
		for s in psfstars:

			if not hasattr(s, 'reg'): # If there is no mask for this star
				continue
			# We read the original extracted stamps
			orifilenames.append("/home/epfl/vbonvin/DECONV/0435/pymcs/results/star_%03i.fits" % s.filenumber) # alternative directory, for a specific case
			#orifilenames.append("star_%03i.fits" % s.filenumber) # original directory 
			(oriarray, oriheader) = fromfits(orifilenames[-1], verbose=False)
			oriarrays.append(oriarray)
			oriheaders.append(oriheader)
			
			#print s.reg.mask[5][7]
			#print oriarrays[-1][5][7]
			#sys.exit()
		for ind,s in enumerate(psfstars):
			
			# WARNING !! Will not work (yet) if some stars don't have mask but others do !!!

			suboriarrays = []
			for ind2,o in enumerate(oriarrays):
				if ind2 != ind:
		
					suboriarrays.append([oriarrays[ind2],psfstars[ind2].reg.mask])

		
			# now, suboriarrays contains the pixeltables of each other psfstars
			# If a pixel has a mask, we want its value to be the median of other psfstars at the same position (if they do not have a mask)
			# Pixel by pixel, straightforward
			import copy
			neworiarray = []
			i=0
			j=0			
			for ind2,line in enumerate(oriarrays[ind]):
				toline = []
				for ind3,elt in enumerate(line):			
					if s.reg.mask[ind2][ind3]==False:
						
						toline.append(oriarrays[ind][ind2][ind3])
					else:
						
						otherpixvalues=[]	
						for suboriarray in zip(suboriarrays):
							subtop = suboriarray[0]
							sub=subtop[0]
							masksub=subtop[1]
							

							if masksub[ind2][ind3] == False:
								
								otherpixvalues.append(sub[ind2][ind3])
							
									
						if len(otherpixvalues) != 0:
							i+=1
							meanpixval = np.median(otherpixvalues)
						else:
							j+=1
							meanpixval = 0		
						toline.append(meanpixval)
						if min([abs(elt) for elt in toline]) ==0 :
							print('HOHOHO')
							#sys.exit()
				neworiarray.append(toline)
			
			
			
			#print 'i=',i
			#print 'j=',j
			#print 'i+j',i+j
			#sys.exit()
			#for l in np.arange(len(neworiarray)):
				#print l,max(neworiarray[l]-oriarrays[ind][l])
			#sys.exit()				
			
			orituple = copy.copy(oriarrays[ind])

			for nl in np.arange(len(orituple)):
				for ne in np.arange(len(orituple[0])):
					orituple[nl][ne] = neworiarray[nl][ne]
			


			#for l in np.arange(len(orituple)):
				#print l,max(orituple[l]-oriarrays[ind][l])
				
			#print oriarrays[ind][50]
			#sys.exit()	
			tofits(orifilenames[ind],orituple,oriheaders[ind],verbose=False)
			print('saved !')		
print("Done.")
	
	
