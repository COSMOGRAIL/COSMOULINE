#
#	Read the produced out.txt
#	And write it into the database, using nice custom field names (using deckey and the source names)
#	*proud*
#	Final victory over this lovely deconv.exe output file ...
#
# For each source we insert x, y, int = the intensity as written in out.txt, flux = the acutal flux, calculated with a bizarre formula from this intensity.
# Plus there is z1, z2, delta1 and delta2


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
from star import *
import progressbar



db = KirbyBase()
# We select only the images that are deconvolved (and thus have a deckeyfilenum)
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True) # the sorting is not  important
nbimg = len(images)
print "Number of images :", nbimg

	# read params of point sources
ptsrcs = readmancatasstars(ptsrccat)
nbptsrcs = len(ptsrcs)
print "Number of point sources :", nbptsrcs
print "Names of sources : "
for src in ptsrcs: print src.name

# The readout itself is fast :
intpostable, zdeltatable = readouttxt(os.path.join(decdir, "out.txt"), nbimg)

print "Ok, I've read the deconvolution output.\n"




# We now prepare a list of dictionnaries to be written into the database, as well as a list of fields to add to the db.

newfields = []
for src in ptsrcs:

	newfields.append({"fieldname": "out_" + deckey + "_" + src.name + "_flux", "type": "float"}) # This will contain the flux (as would be measured by aperture  photometry on the original raw image)
	#newfields.append({"fieldname": "out_" + deckey + "_" + src.name + "_int", "type": "float"}) # We keep this "intensity" only for retrocompatibility.
	# Let's remove this "int", it should not be used anymore.
	newfields.append({"fieldname": "out_" + deckey + "_" + src.name + "_x", "type": "float"})
	newfields.append({"fieldname": "out_" + deckey + "_" + src.name + "_y", "type": "float"})
newfields.append({"fieldname": "out_" + deckey + "_z1", "type":"float"})
newfields.append({"fieldname": "out_" + deckey + "_z2", "type":"float"})
newfields.append({"fieldname": "out_" + deckey + "_delta1", "type":"float"})
newfields.append({"fieldname": "out_" + deckey + "_delta2", "type":"float"})


print "Negative fluxes :"
for image in images:
	image["updatedict"] = {}
	#print image[deckeyfilenum]
	outputindex = int(image[deckeyfilenum]) - 1 # So this guy is starting at 0, even if the first image is 0001.
	
	image["updatedict"]["out_" + deckey + "_z1"] = zdeltatable[outputindex][0]
	image["updatedict"]["out_" + deckey + "_z2"] = zdeltatable[outputindex][1]
	image["updatedict"]["out_" + deckey + "_delta1"] = zdeltatable[outputindex][2]
	image["updatedict"]["out_" + deckey + "_delta2"] = zdeltatable[outputindex][3]
	
	for i, src in enumerate(ptsrcs):

		# image["updatedict"]["out_" + deckey + "_" + src.name + "_int"] = intpostable[i][outputindex][0]
		image["updatedict"]["out_" + deckey + "_" + src.name + "_x"] = intpostable[i][outputindex][1]
		image["updatedict"]["out_" + deckey + "_" + src.name + "_y"] = intpostable[i][outputindex][2]
		
		# We calculate the flux :
		
		fwhm = 2.0 # this is the width of the "output gaussian", that we choose to be of 2 small pixels
		pi = 3.141592653589793
		ln2 = 0.693147180559945
		
		mcsint = intpostable[i][outputindex][0]
		flux = mcsint * ( fwhm**2 / 4.0 ) * pi / (4.0 * ln2)
		
		image["updatedict"]["out_" + deckey + "_" + src.name + "_flux"] = flux
		
		# We check if the int is positive :
		if mcsint < 0.0:
			print "%s, %s, %s : %f " % (image["imgname"], image["datet"], src.name, flux)

	
print "\nI would now update the database."
proquest(askquestions)
backupfile(imgdb, dbbudir, "readout_"+deckey)


for field in newfields:
	if field["fieldname"] not in db.getFieldNames(imgdb):
		db.addFields(imgdb, ["%s:%s" % (field["fieldname"], field["type"])])

print "New fields added."


# The writing itself :

widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(), ' ', progressbar.ReverseBar('<')]
pbar = progressbar.ProgressBar(widgets=widgets, maxval=nbimg+2).start()

for i, image in enumerate(images):
	pbar.update(i)	
	db.update(imgdb, [deckeyfilenum], [image[deckeyfilenum]], image["updatedict"])
	
pbar.finish()

# As usual, we pack the db :
db.pack(imgdb)
# Note that it seems to be better to pack the database before "changing a changed" entry !

notify(computer, withsound, "The results of %s are now in the database." % deckey)


