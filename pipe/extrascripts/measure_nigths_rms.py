#
# measure night quasar image rms and star rms
#

execfile("../config.py")
import f2n
import shutil
import star
from kirbybase import KirbyBase, KBError
from variousfct import *
import combibynight_fct
import numpy as np
import sys, os

star_ref = 'b'
aperture = 'auto'
ptsources = star.readmancat(ptsrccat)
skip_night = []
write_in_file = True #to write the report, turn to false to print in the terminal

if write_in_file :
    sys.stdout = open(os.path.join(workdir, 'report_night_scatter.txt'), "w")

print xephemlens.split(',')[0]
print "Number of point sources : %i" % len(ptsources)
print "Names of sources : %s" % ", ".join([s.name for s in ptsources])

db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum,'gogogo'], ['\d\d*', True], returnType='dict', useRegExp=True, sortFields=['mjd'])
print 'I have %i deconvolved images'%len(images)
dic = []
rms_night = []

for j, s in enumerate(ptsources):
    fluxfieldname = "out_%s_%s_flux" % (deckey, s.name)
    fluxfieldname_ref_star = "%s_%s_%s_flux" % (sexphotomname, star_ref, aperture)
    randomerrorfieldname = "out_%s_%s_shotnoise" % (deckey, s.name)


    groupedimages = combibynight_fct.groupbynights(images)
    dic.append(combibynight_fct.mags(groupedimages, fluxfieldname, normkey=deckeynormused, verbose = False))

dic_ref_star = combibynight_fct.mags(groupedimages, fluxfieldname_ref_star, normkey='medcoeff', verbose = False)

#dic indices : [ptssource][keyword][nights]
average_night_rms = [[] for i in ptsources]
average_night_mag = [[] for i in ptsources]
average_night_rms_refstar = []
average_night_mag_refstar = []
good_night = []

for i,night in enumerate(groupedimages):
    print
    print "-"*20, "Night :", np.floor(night[0]['mjd']), "-"*20
    if str(np.floor(night[0]['mjd'])) in skip_night :
        print "skipping this night"
    else :
        good_night.append(night)
        print "Number of images : ", len(night)
        print "Night average seeing (arcsec) :", np.mean([ima['seeing'] for ima in night ])
        print "Night rms : "
        for j, s in enumerate(ptsources):
            print s.name, " : ", dic[j]['stddev'][i]
            average_night_rms[j].append(dic[j]['stddev'][i])
            average_night_mag[j].append(dic[j]['median'][i])

        print "star ", star_ref, " : ", dic_ref_star['stddev'][i]
        average_night_rms_refstar.append(dic_ref_star['stddev'][i])
        average_night_mag_refstar.append(dic_ref_star['median'][i])

print ""
print "#" * 30
print "Average night rms (mag):"
for j, s in enumerate(ptsources):
    print s.name, " : ", np.mean(average_night_rms[j])
print "star ", star_ref, " : ", np.mean(average_night_rms_refstar)

print ""
print "#" * 30
print "Night to Night scatter (of the combined exposures) : "
print "Average mag and scatter over the period ", good_night[0][0]['date'], "-", good_night[-1][0]['date'], '(%i nigths)'%(len(good_night))

for j, s in enumerate(ptsources):
    print s.name, "mean : ", np.mean(average_night_mag[j]), "+/-", np.std(average_night_mag[j])
print "star ", star_ref, " : ", np.mean(average_night_mag_refstar), "+/-", np.std(average_night_mag_refstar)

if write_in_file :
    sys.stdout.close()