"""
Plot the flux in various aperture photometry from sextractor catalogue
per star
per image
"""


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np

import matplotlib.pyplot as plt


db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

nbrofimages = len(images)
print "I respect treatme, and selected only %i images" % (nbrofimages)



# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)

#starslist = ["a", "b", "c", "d", "e", "f"]
#photomstars = [s for s in photomstars if s.name in starslist]

print "Photom stars :"
print "\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars])


# Read the list of aperture photometry
print "I will read the following fields :"
# Fields for the database :
#dbfields = [{"name":"%s_%s_%s" % (sexphotomname, s.name, f["dbname"]), "type":f["type"]} for s in photomstars for f in sexphotomfields]
#print "\n".join(["%30s : %5s" % (f["name"], f["type"]) for f in dbfields])



for i, image in enumerate(images[200:250]):

	if i < 5:
		print " -" * 20
		print i+1, "/", nbrofimages, ":", image['imgname']

		for s in photomstars:
				print "Star %s" %s.name
				dbfields = [{"name":"%s_%s_%s" % (sexphotomname, s.name, f["dbname"]), "type":f["type"]} for f in sexphotomfields]
				apertures = []
				fluxes = []
				try:
					for field in dbfields:
						if 'auto' not in field["name"]:
							print field["name"], image[field["name"]]
							fluxes.append(float(image[field["name"]]))
							apertures.append(int(field["name"].split('_')[2].split('ap')[1]))
						else:
							print field["name"], image[field["name"]]
							flux_auto = float(image[field["name"]])

					plt.figure()
					plt.plot(apertures, fluxes,'or-')
					plt.axhline(flux_auto)
					plt.suptitle("%s -- Star %s" %(image["imgname"], s.name))
					plt.show()
				except:
					print "No fluxes for star %s on image %s" %(s.name, image["imgname"])
		continue

	sys.exit()