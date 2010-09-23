#
#	
#	This time, you can specify which deconvolutions you want to compare.
#	We do not take into account the deconvolution settings of settings.py
#	

# - - - - - - - - - - - - - - - - - - - - - - - 

# give a list of tuples : [("deckey", "sourcename"), ...]
# optionally, you can also give ("deckey", "sourcename", magshift)

#tocompare = [('dec_1_lens_newac1','A'), ('dec_1_lens_newac1','B'), ('dec_1_a_newac1','a'), ('dec_1_b_newac1','b'), ('dec_1_c_newac1','c'), ('dec_1_g_newac1','g', -2.0)]

#tocompare = [('dec_1_lens_newac1','A'), ('dec_1_lens_newac1','B',+0.5), ('dec_1_g_newac1','g')]

#tocompare = [('dec_2_lens_renorm_abc_abc','A'), ('dec_2_lens_renorm_abc_abc','B'), ('dec_2_g_renorm_abc_abc','g', +0.8)]
#tocompare = [('dec_3_lens_renorm_abc_abcSharp','A'), ('dec_3_lens_renorm_abc_abcSharp','B'), ('dec_3_g_renorm_abc_abcSharp','g', +0.8)]

#tocompare = [('dec_1_a_newac1','a'), ('dec_1_b_newac1','b',+0.5), ('dec_1_c_newac1','c'), ('dec_1_g_newac1','g')]

tocompare = [('dec_full_lens_defg1_fg1','A'), ('dec_full_lens_defg1_defg1','A')]

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

plt.figure(figsize=(12,8))	# sets figure size

for item in tocompare:
	deckey = item[0]
	sourcename = item[1]
	deckeyfilenum = "decfilenum_" + deckey
	images = [image for image in allimages if image[deckeyfilenum] != None]
	
	print "%20s %3s : %4i" %(deckey, sourcename, len(images))

	mhjds = asarray(map(lambda x: x['mhjd'], images))# - 54000
	seeing = asarray(map(lambda x: x['seeing'], images))

	intfieldname = "out_" + deckey + "_" + sourcename + "_int"
	mags = -2.5 * log10(asarray(map(lambda x: x[intfieldname], images)))
	
	label = sourcename + "/" + deckey
	#label = sourcename
	if len(item) == 3:
		mags += item[2]
		label += " (%+.2f)"%item[2]

	plt.plot(mhjds, mags, marker = ".", linestyle="None", label = label)


# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude')

plt.grid(True)
plt.legend()
plt.show()
	

	
