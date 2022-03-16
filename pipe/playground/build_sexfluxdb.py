#
#	We group the Sextractor fluxes of the normstars into a single pickle for faster plotting.
#


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
#from calccoeff_fct import *
from variousfct import *
from star import *


# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')


# we read the handwritten star catalog
normstars = readmancatasstars(normstarscat)


lcdict = {}
for st in normstars:
	lcdict[st.name] = {"mjds":[], "fluxes":[], "seeings":[], "fwhms":[], "medcoeffs":[], "alts":[], "azs":[]}



for i, image in enumerate(images):
	
	# the catalog we will read
	sexcat = alidir + image['imgname'] + ".alicat"
	
	# read sextractor catalog
	catstars = readsexcatasstars(sexcat)
				
	# cross-identify the stars with the handwritten selection
	identstars = listidentify(normstars, catstars, 5.0)
	
	# Now we have a list of stars, for this image, and we fill the lcdict :
	for st in identstars:
		lcdict[st.name]["mjds"].append(image["mjd"])
		lcdict[st.name]["fluxes"].append(st.flux)
		lcdict[st.name]["seeings"].append(image["seeingpixels"])
		lcdict[st.name]["fwhms"].append(st.fwhm)
		lcdict[st.name]["medcoeffs"].append(image["medcoeff"])
		lcdict[st.name]["azs"].append(image["az"])
		lcdict[st.name]["alts"].append(image["alt"])


writepickle(lcdict, os.path.join(plotdir, "sexfluxdb.pkl"))


