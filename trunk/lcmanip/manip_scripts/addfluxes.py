execfile("../config.py")

###########################################################################################


deconvname = "dec_full3_lens_medcoeff_abgde1"

toaddsourcenames = ["A1", "A2"]

sumsourcename = ["A"]



###########################################################################################

import matplotlib.pyplot as plt
import matplotlib.dates


variousfct.backupfile(pkldbpath, "../pkldb_backups", "Adding%s" % ("".join(toaddsourcenames)))

"""
print "Deconvolution : %s" % (deconvname)
print "Point sources : %s" % ", ".join(sourcenames)

images = variousfct.readpickle(pkldbpath, verbose=True)

images = [image for image in images if image["decfilenum_" + deconvname] != None] 
print "%i images" % len(images)

groupedimages = groupfct.groupbynights(images)
print "%i nights"% len(groupedimages)


plt.figure(figsize=(12,8))

mhjds = groupfct.values(groupedimages, 'mhjd', normkey=None)['mean']

medairmasses = groupfct.values(groupedimages, 'airmass', normkey=None)['median']
medseeings = groupfct.values(groupedimages, 'seeing', normkey=None)['median']
medskylevels = groupfct.values(groupedimages, 'skylevel', normkey=None)['median']
#meddeccoeffs = groupfct.values(groupedimages, normcoeffname, normkey=None)['median']


"""
