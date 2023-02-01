import os
import numpy as np
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
import combibynight_fct

ref_star = ['a']
star_deckey = ['dec_noback' for s in ref_star]
norm_field = ['medcoeff' for s in ref_star]

# panstarr_mag = np.asarray([16.62470054626465]) #rPSFmag 2M1134 star a
# panstarr_mag = np.asarray([17.158700942993164]) #rPSFmag HE0047 star b
# panstarr_mag = np.asarray([20.1326]) #rPSFmag DES2325 star a from DES
# panstarr_mag = np.asarray([18.1021]) #rPSFmag DES0407 star a from DES
# panstarr_mag = np.asarray([18.78380012512207]) #rPSFmag WG0214 star b
# panstarr_mag = np.asarray([17.769899368286133]) #rPSFmag PS1606 star a
panstarr_mag = np.asarray([17.6733894348]) #DES mag for DESJ0602

f = open(os.path.join(configdir, "zeropoint.txt"), "w")
f.write('Absolute Calibration using %i stars : \n'%len(ref_star))
f.write('\n')
zp_vect = []


db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum,'gogogo'], ['\d\d*', True], returnType='dict', useRegExp=True, sortFields=['mjd'])
print(f"{len(images)} images")
groupedimages = combibynight_fct.groupbynights(images)
print(f"{len(groupedimages)} nights")

for j, s in enumerate(ref_star):
    fluxfieldname = "out_%s_%s_%s_%s_%s_flux" % (star_deckey[j], s, norm_field[j], decpsfnames[0],s)
    randomerrorfieldname = "out_%s_%s_%s_%s_%s_shotnoise" % (star_deckey[j], s, norm_field[j], decpsfnames[0],s)

    mags = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=norm_field[j])['median']
    zp = panstarr_mag[j] - mags

    print('Star %s, mean mag : '%s, np.median(mags))
    print('Star %s, zeropoint : '%s, np.median(zp))

    f.write('Star %s, PanSTARRS Mag :%2.5f \n'%(s, panstarr_mag[j]))
    f.write('Star %s, median mag : %2.5f \n'%(s, np.median(mags)))
    f.write('Star %s, zeropoint : %2.5f \n'%(s, np.median(zp)))
    f.write('\n')

    zp_vect.append(np.median(zp))


f.write('\n ### OVERALL CALIBRATION ### \n')
f.write('Zero Point : %2.5f'%np.median(zp_vect))