


toplot = (
('dec_fullrn_lens_ab1_ab1','A'),
('dec_fullrn_lens_ab1_ab1','B'),
('dec_fullrn_lens_ab1_ab1','C', -0.5),
('dec_fullrn_lens_ab1_ab1','D', -0.3),
('dec_full_a_medcoeff_ab1','a', 4.0)
)

# - - - - - - - - - - - - - - - - - - - - - - - 

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from combibynight_fct import *
from star import *

import numpy as np
import matplotlib.pyplot as plt

# we only read the database once, it is faster to analyse this in RAM... :
db = KirbyBase()

allimages = db.select(imgdb, ["recno"], ['*'], returnType='dict')
#allimages = db.select(imgdb, ["telescopename"], ["Mercator"], returnType='dict')
#allimages = db.select(imgdb, ["seeing", "telescopename"], ['<3.0', "Mercator"], returnType='dict')

plt.figure(figsize=(12,8))	# sets figure size

curvestoplot = []

for curve in toplot:
	
	deckey = curve[0]
	sourcename = curve[1]
	deckeyfilenum = "decfilenum_" + deckey
	intfieldname = "out_" + deckey + "_" + sourcename + "_flux"
	
	images = [image for image in allimages if image[deckeyfilenum] != None]
	groupedimages = groupbynights(images)
		
	
	groupedfluxes = np.asarray(values(groupedimages, intfieldname)['median'])
	groupedmhjds = np.asarray(values(groupedimages, 'mhjd')['median'])
	groupedseeings = np.asarray(values(groupedimages, 'seeing')['mean'])
	groupedfluxmins = np.asarray(values(groupedimages, intfieldname)['min'])
	groupedfluxmaxs = np.asarray(values(groupedimages, intfieldname)['max'])
	
	groupedseeings[9] = 1.4566
	groupedseeings[10] = 1.83512
	groupedseeings[11] = 1.7254
	
	shift = 0.0
	if len(curve) == 3:
		shift = curve[2]
		
	label = sourcename
	
	curvestoplot.append({"jds":groupedmhjds, "fluxes":groupedfluxes, "seeings":groupedseeings, "label":label, "mins":groupedfluxmins, "maxs":groupedfluxmaxs, "shift":shift})
	

# We group A and B

newcurves = curvestoplot[2:]


abjds = curvestoplot[0]["jds"]
abfluxes = curvestoplot[0]["fluxes"] + curvestoplot[1]["fluxes"]
abmins = curvestoplot[0]["mins"] + curvestoplot[1]["mins"]
abmaxs = curvestoplot[0]["maxs"] + curvestoplot[1]["maxs"]
abseeings = curvestoplot[0]["seeings"]
ablabel = curvestoplot[0]["label"] + "+" + curvestoplot[1]["label"]
abshift = 0.0

newcurves.insert(0, {"jds":abjds, "fluxes":abfluxes, "seeings":abseeings, "label":ablabel, "mins":abmins, "maxs":abmaxs, "shift":abshift})


for curve in newcurves:
	curve["jds"] = curve["jds"][1:]
	curve["fluxes"] = curve["fluxes"][1:]
	curve["mins"] = curve["mins"][1:]
	curve["maxs"] = curve["maxs"][1:]
	curve["seeings"] = curve["seeings"][1:]
	
	
	curve["mags"] = -2.5 * np.log10(curve["fluxes"])
	curve["mags"] += curve["shift"]
	
	curve["magerrs"] = 2.5 * np.log10(curve["fluxes"] + (curve["maxs"]-curve["mins"])/2.0  ) - 2.5 * np.log10(curve["fluxes"])
	
	#print curve["shift"]



# We divide all A+B errors by 2, and additionally by 5 if large
num = 0
for i in range(len(newcurves[num]["magerrs"])):
	#print newcurves[num]["magerrs"][i]
	if newcurves[num]["magerrs"][i] > 0.3:
		#pass
		#print newcurves[num]["magerrs"][i]
		newcurves[num]["magerrs"][i] = newcurves[num]["magerrs"][i]/5.0
	newcurves[num]["magerrs"][i] = newcurves[num]["magerrs"][i]/2.0
	

# We divide all C and D errors by 3.0 if large :
num = 1
for i in range(len(newcurves[num]["magerrs"])):
	#print newcurves[num]["magerrs"][i]
	if newcurves[num]["magerrs"][i] > 0.15:
		#pass
		print newcurves[num]["magerrs"][i]
		newcurves[num]["magerrs"][i] = newcurves[num]["magerrs"][i]/2.0
num = 2
for i in range(len(newcurves[num]["magerrs"])):
	#print newcurves[num]["magerrs"][i]
	if newcurves[num]["magerrs"][i] > 0.15:
		#pass
		print newcurves[num]["magerrs"][i]
		newcurves[num]["magerrs"][i] = newcurves[num]["magerrs"][i]/2.0

	

for curve in newcurves :

#plt.errorbar(renormgroupedmhjds, renormgroupedmagsarray, [renormgroupedmags["down"],renormgroupedmags["up"]], linestyle="None", marker=".", label = label)
#plt.plot(groupedmhjds, groupedmags, linestyle="None", marker=".", label = label)

	plt.errorbar(curve["jds"], curve["mags"], curve["magerrs"], linestyle="None", ecolor="black", marker=".", label = curve["label"])
	#plt.plot(curve["jds"], curve["mags"], linestyle="None", marker=".", label = curve["label"])
	plt.scatter(curve["jds"], curve["mags"], s=20, c=curve["seeings"], vmin=1.0,vmax=2.5, edgecolors='none', label=curve["label"], zorder=12)

# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

cbar = plt.colorbar(orientation='vertical')
cbar.set_label('Image FWHM [arcsec]') 


plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude (instrumental)')

plt.grid(True)
#plt.legend()
plt.show()
	


