
import sys, os
pipedir = "/Users/martin/Desktop/COSMO3b/pipe"
sys.path.append(os.path.join(pipedir, "modules"))#the place where you have the kirbybase module

from kirbybase import KirbyBase, KBError
import combibynight_fct
import numpy as np
import csv


workdir ='/Users/martin/Desktop/config4COSMOULINE/HE0435_ECAM'
imgdb = os.path.join(workdir, "2019-01-11_HE0435_ECAM_db.dat")	# This will be a nice KirbyBase.

ref_star = ['a','b','c','d','h','f','j']
star_deckey = ['dec_noback' for s in ref_star]
norm_field = ['medcoeff' for s in ref_star]
deckeyfilenum = "decfilenum_" + "dec_backfull_lens_renorm_abcdhij_abcdil"
decpsfnames = ["abcdil"]

db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum,'gogogo'], ['\d\d*', True], returnType='dict', useRegExp=True, sortFields=['mjd'])
key_list = ['mhjd']


print "%i images" % len(images)
groupedimages = combibynight_fct.groupbynights(images)
mhjds = combibynight_fct.values(groupedimages, 'mhjd', normkey=None)['mean']
print "%i nights" % len(groupedimages)
data = [mhjds]

for j, s in enumerate(ref_star):
    fluxfieldname = "out_%s_%s_%s_%s_%s_flux" % (star_deckey[j], s, norm_field[j], decpsfnames[0],s)
    randomerrorfieldname = "out_%s_%s_%s_%s_%s_shotnoise" % (star_deckey[j], s, norm_field[j], decpsfnames[0],s)
    key_star = "Star %s (N%i)"%(s,j+1)

    mags = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=norm_field[j], verbose=False)['median']
    mags = np.asarray([np.float(m) for m in mags])
    data.append(mags)
    key_list.append(key_star)

    print 'Star %s, mean mag : '%s, np.median(mags)

print(key_list)
data = np.asarray(data)
outfile = os.path.join(workdir, "star_photometry.txt")

np.savetxt(outfile,data.T, header='\t'.join(key_list))
