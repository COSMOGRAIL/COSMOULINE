#
#	This is typically the last plot, to look at the data you will use in the curve shifting algorithms.	
#

# - - - - - - - - - - - - - - - - - - - - - - - 

# give a list of tuples : [("deckey", "sourcename"), ...]
# optionally, you can also give ("deckey", "sourcename", magshift)

# Give an errorname

tocompare = [('dec_full8_lens_1256_1234','A'),
('dec_full8_lens_1256_1234','B', -0.2),
('dec_full8_lens_1256_1234','C', +0.15),
('dec_full8_lens_1256_1234','D', +0.25)]

errorname = "magerror_1256"

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
#allimages = db.select(imgdb, ["seeing"], ['<1.5'], returnType='dict')

# make a list of telescopes
telescopenames = sorted(list(set([image["telescopename"] for image in allimages])))

plt.figure(figsize=(12,8))	# sets figure size

#for setname in setnames:
for telescopename in telescopenames:

	#print setname
	print telescopename
	magarraylist = []
	mhjdarraylist = []
	errorarraylist = []

	for item in tocompare:
		deckey = item[0]
		sourcename = item[1]
		deckeyfilenum = "decfilenum_" + deckey
		intfieldname = "out_" + deckey + "_" + sourcename + "_int"
		
		#images = [image for image in allimages if image[deckeyfilenum] != None and image["setname"] == setname]
		images = [image for image in allimages if image[deckeyfilenum] != None and image["telescopename"] == telescopename]
	
		# We combine by nights.	
		groupedimages = groupbynights(images)
		
		print "%20s %3s : %4i images in %3i nights" %(deckey, sourcename, len(images), len(groupedimages))

		groupedmags = asarray(mags(groupedimages, intfieldname)['median'])
		groupederrors = asarray(values(groupedimages, errorname)['mean'])
		lengths = array(map(len, groupedimages))
		groupederrors = 2.0*groupederrors / sqrt(lengths)
			
		groupedmhjds = asarray(values(groupedimages, 'mhjd')['median'])
		
		if len(item) == 3: # we modify the array
			groupedmags += item[2]
					
		magarraylist.append(groupedmags)
		mhjdarraylist.append(groupedmhjds)
		errorarraylist.append(groupederrors)
		
	
	groupedmagsarray = concatenate(magarraylist)
	groupedmhjdsarray = concatenate(mhjdarraylist)
	groupederrorsarray = concatenate(errorarraylist)

	#label = setname
	label = telescopename
	
	#plt.plot(groupedmhjdsarray, groupedmagsarray, markersize=15, linestyle="None", marker=".", label = label)
	#plt.plot(groupedmhjdsarray, groupedmagsarray, linestyle="None", marker=".", label = label)
	plt.errorbar(groupedmhjdsarray, groupedmagsarray, groupederrorsarray, linestyle="None", marker=".", label = label)
	


# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude')

plt.grid(True)
plt.legend()
plt.show()
	

	
