#
#	A scatter plot encoding the seeings as colours
#	You can tweak the code very easily to plot other database columns...
#

# - - - - - - - - - - - - - - - - - - - - - - - 

# give a list of tuples : [("deckey", "sourcename"), ...]
# optionally, you can also give ("deckey", "sourcename", magshift)

toplot = [('dec_test1_lens_BM_new_BM1_new_BMPS1_new_BM2_new_BMPS2','A'), ('dec_test1_lens_BM_new_BM1_new_BMPS1_new_BM2_new_BMPS2','B')]
"""
toplot = [('dec_test2_lens_renorm_test2_HGE_new_HG1_new_HGE2_new_EG1_new_HG2_new_HEM1_new_HGE3','A'),
('dec_test2_lens_renorm_test2_HGE_new_HG1_new_HGE2_new_EG1_new_HG2_new_HEM1_new_HGE3','B', +0.0),
]
"""

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
#allimages = db.select(imgdb, ["telescopename"], ["Mercator"], returnType='dict')
#allimages = db.select(imgdb, ["seeing", "telescopename"], ['<3.0', "Mercator"], returnType='dict')

plt.figure(figsize=(12,8))	# sets figure size

for item in toplot:
	deckey = item[0]
	sourcename = item[1]
	deckeyfilenum = "decfilenum_" + deckey
	fluxfieldname = "out_" + deckey + "_" + sourcename + "_flux"
	
	#images = [image for image in allimages if image[deckeyfilenum] != None and image["setname"] == setname]
	images = [image for image in allimages if image[deckeyfilenum] != None]

	print "%20s %3s : %4i" %(deckey, sourcename, len(images))

	# We combine by nights.
		
	groupedimages = groupbynights(images)
		
	
	groupedmags = asarray(mags(groupedimages, fluxfieldname)['median'])
	
	groupedmhjds = asarray(values(groupedimages, 'mhjd')['median'])
	
	groupedseeings = asarray(values(groupedimages, 'seeing')['mean'])
		
	if len(item) == 3: # we modify the array
		groupedmags += item[2]
				
	label = sourcename + "/" + deckey
	
	#plt.errorbar(renormgroupedmhjds, renormgroupedmagsarray, [renormgroupedmags["down"],renormgroupedmags["up"]], linestyle="None", marker=".", label = label)
	#plt.plot(groupedmhjds, groupedmags, linestyle="None", marker=".", label = label)
	
	plt.scatter(groupedmhjds, groupedmags, s=12, c=groupedseeings, vmin=0.5,vmax=2.3, edgecolors='none')




# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

cbar = plt.colorbar(orientation='horizontal')
cbar.set_label('FWHM [arcsec]') 


plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude')

plt.grid(True)
#plt.legend()
plt.show()
	

	
