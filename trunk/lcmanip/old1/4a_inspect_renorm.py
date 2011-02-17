#
#	This script is made to see how a renormalization went
#	We plot the some lightcurves in the "raw" and renormalized versions, combined by nights.	
#

# - - - - - - - - - - - - - - - - - - - - - - - 

# give a list of tuples : [("deckey", "sourcename"), ...]
# optionally, you can also give ("deckey", "sourcename", "magshift")

#tocompare = [('dec_1_lens_newac1','A'), ('dec_1_lens_newac1','B'), ('dec_1_a_newac1','a'), ('dec_1_b_newac1','b'), ('dec_1_c_newac1','c'), ('dec_1_g_newac1','g', -2.0)]

tocompare = [('dec_2_lens_newac1','A'), ('dec_2_lens_newac1','B')]

#tocompare = [('dec_1_a_newac1','a'), ('dec_1_g_newac1','g'), ('dec_1_c_newac1','c'), ('dec_1_b_newac1','b')]


renormfieldname = "renorm_ag_newac1"


# - - - - - - - - - - - - - - - - - - - - - - - 

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from combibynight_fct import *
from star import *

from numpy import *
import matplotlib.pyplot as plt

# we only read the database once, it is faster to analyse this in RAM... :
db = KirbyBase()
allimages = db.select(imgdb, ["recno"], ['*'], returnType='dict')
#allimages = db.select(imgdb, ["seeing", "telescopename"], ['<3.0', "Mercator"], returnType='dict')


# make a list of setnames
setnames = sorted(list(set([image["setname"] for image in allimages])))



plt.figure(figsize=(12,8))	# sets figure size

for item in tocompare:
	deckey = item[0]
	sourcename = item[1]
	deckeyfilenum = "decfilenum_" + deckey
	images = [image for image in allimages if image[deckeyfilenum] != None]
	
	print "%20s %3s : %4i" %(deckey, sourcename, len(images))

	# let's get the raw points :
	rawmhjds = asarray(map(lambda x: x['mhjd'], images))
	seeing = asarray(map(lambda x: x['seeing'], images))

	intfieldname = "out_" + deckey + "_" + sourcename + "_int"
	rawmags = -2.5 * log10(asarray(map(lambda x: x[intfieldname], images)))
	
	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	# For the renormalized version, we want to combine by nights.
	
	# Choose this if you want to allow combinations by night mixing all the different telescopes :
	#groupedimages = groupbynights(images)
	#print "Number of nights :", len(groupedimages)
	
	# Or this if you want to to separate by setnames (i.e. the telescopes)
	groupedimages = []
	for setname in setnames:
		thissetimages = [image for image in images if image["setname"] == setname]
		thissetgroupedimages = groupbynights(thissetimages)
		print "%20s : %4i images in %3i nights"%(setname, len(thissetimages), len(thissetgroupedimages))
		groupedimages.extend(thissetgroupedimages)
	
	
	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	
	renormgroupedmags = renormmags(groupedimages, intfieldname, renormfieldname)
	# just for testing purposes :
	#renormgroupedmags = mags(groupedimages, intfieldname)
	
	renormgroupedmagsarray = asarray(renormgroupedmags['median'])
	renormgroupedmhjds = asarray(values(groupedimages, 'mhjd')['median'])
	
	label = sourcename + "/" + deckey
	if len(item) == 3:
		rawmags += item[2]
		renormgroupedmagsarray += item[2]
		label += " (%+.2f)"%item[2]

	
	plt.plot(rawmhjds, rawmags, marker = ".", linestyle="None", color="#BBBBBB")
	plt.errorbar(renormgroupedmhjds, renormgroupedmagsarray, [renormgroupedmags["down"],renormgroupedmags["up"]], linestyle="None", marker=".", label = label)
	#plt.plot(renormgroupedmhjds, renormgroupedmagsarray, linestyle="None", marker=".", label = label)




# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude')

plt.grid(True)
plt.legend()
plt.show()
	

	
