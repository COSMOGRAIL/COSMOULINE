
exec(compile(open("config.py", "rb").read(), "config.py", 'exec'))
import math
#import matplotlib.pyplot as plt
#import matplotlib.dates

toaddfluxfields = ["out_%s_%s_flux" % (deconvname, sourcename) for sourcename in toaddsourcenames]
toaddshotnoisefields = ["out_%s_%s_shotnoise" % (deconvname, sourcename) for sourcename in toaddsourcenames]

sumfluxfield = "out_%s_%s_flux" % (deconvname, sumsourcename)
sumshotnoisefield = "out_%s_%s_shotnoise" % (deconvname, sumsourcename)


addcode = sumsourcename  + "=" + "+".join(toaddsourcenames)
print("Operation : %s" % (addcode))

filenameels = os.path.splitext(dbfilepath)
newdbfilepath = filenameels[0] + "_" + addcode + filenameels[1]

if os.path.exists(newdbfilepath):
	raise RuntimeError("Output file exists, please remove it !")

shutil.copy(dbfilepath, newdbfilepath)

images = variousfct.readpickle(newdbfilepath, verbose=True)
print("%i images in db." % (len(images)))

for image in images:
	image[sumfluxfield] = None
	image[sumshotnoisefield] = None
	
	fluxes = [image[fieldname] for fieldname in toaddfluxfields]
	shotnoises = [image[fieldname] for fieldname in toaddshotnoisefields]
	
	if not (None in fluxes) :
		
		# We sum the fluxes, and take the geometric sum of the shotnoises (very plausible).
	
		image[sumfluxfield] = sum(fluxes)
		image[sumshotnoisefield] = math.sqrt(float(sum([s*s for s in shotnoises])))

	#print image[sumfluxfield], " +/- ", image[sumshotnoisefield]

variousfct.writepickle(images, newdbfilepath, verbose=True)
print("Ok done, this is the new dbfilename to use :")
print(os.path.basename(newdbfilepath))
