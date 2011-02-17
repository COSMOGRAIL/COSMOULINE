execfile("../config.py")

###########################################################################################

#deconvname = "dec_full3_lens_medcoeff_abgde1"

toaddsourcenames = ["A1", "A2"]

sumsourcename = "A"

# error is taken as the mean error of the toaddsources

###########################################################################################

toaddfluxfields = ["out_%s_%s_flux" % (deconvname, sourcename) for sourcename in toaddsourcenames]
toadderrfields = ["out_%s_%s_randerror" % (deconvname, sourcename) for sourcename in toaddsourcenames]

sumfluxfield = "out_%s_%s_flux" % (deconvname, sumsourcename)
sumerrfield = "out_%s_%s_randerror" % (deconvname, sumsourcename)

print "Adding \n%s" % ("\n".join(toaddfluxfields))
print "= %s" % (sumfluxfield)

images = variousfct.readpickle(pkldbpath, verbose=True)


for image in images:
	image[sumfluxfield] = None
	image[sumerrfield] = None
	
	fluxestoadd = [image[fieldname] for fieldname in toaddfluxfields]
	errorstomean = [image[fieldname] for fieldname in toadderrfields]
	
	if not (None in fluxestoadd) :
		image[sumfluxfield] = sum(fluxestoadd)
		image[sumerrfield] = sum(errorstomean)/float(len(toaddsourcenames))

	print image[sumfluxfield], "+/-", image[sumerrfield]
	
	
	
variousfct.backupfile(pkldbpath, "../pkldb_backups", "Adding%s" % ("".join(toaddsourcenames)))
variousfct.writepickle(images, pkldbpath, verbose=True)
