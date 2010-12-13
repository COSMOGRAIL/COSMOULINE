execfile("./config.py")

import skysim_sources
import skysim_images
import variousfct


# Matrix of PSF stars 
psfstars = skysim_sources.build_array_stars((900, 900), matrix_x = 6, matrix_y = 6, distance=120)

psfmags = [17, 17.5, 18, 18.5, 19, 19.5]
psfnames = ["a", "b", "c", "d", "e", "f"]

for i in range(6): # x = magnitudes
	for j in range(6):
		psfstars[6*i+j].mag = psfmags[i]
		psfstars[6*i+j].name = "%s%i" % (psfnames[i], j)


skysim_sources.jitter_sourcelist(psfstars)

# Separation 0.85 arcsec
lens1 = [skysim_sources.Star(1000, 750, 19, "L1A"), skysim_sources.Star(1003, 753, 19, "L1B")]
lens2 = [skysim_sources.Star(1200, 750, 18, "L2A"), skysim_sources.Star(1203, 753, 20, "L2B")]

# Separation sqrt(2) arcsec
lens3 = [skysim_sources.Star(1000, 630, 19, "L3A"), skysim_sources.Star(1005, 635, 19, "L3B")]
lens4 = [skysim_sources.Star(1200, 630, 18, "L4A"), skysim_sources.Star(1205, 635, 20, "L4B")]


sn1 = [skysim_sources.Galaxy(1100, 450, 17, "Galaxy1"), skysim_sources.Star(1110, 465, 18.5, "SN1")]

sn2 = [skysim_sources.Galaxy(1100, 250, 16, "Galaxy2"), skysim_sources.Star(1110, 265, 18.5, "SN2")]
sn2[0].bulgratio = 0.0

targets = lens1 + lens2 + lens3 + lens4 + sn1 + sn2


variousfct.writepickle(psfstars + targets, "Malte1_sourcelist.pkl")
