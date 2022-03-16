


execfile("../config.py")
from kirbybase import KirbyBase, KBError
import variousfct
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.dates


db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['mjd'])

refimage = [image for image in images if image["imgname"]==refimgname][0]

stars = [
["out_dec_full_a_medcoeff_pyMCSabcd1_a_flux", 15.7],
["out_dec_full_b_medcoeff_pyMCSabcd1_b_flux", 15.8],
["out_dec_full_c_medcoeff_pyMCSabcd1_c_flux", 15.2],
["out_dec_full_d_medcoeff_pyMCSabcd1_d_flux", 16.4],
["out_dec_full_y_medcoeff_pyMCSabcd1_y_flux", 16.7],

]

#print refimage

instmags = -2.5*np.log10(np.array([refimage[star[0]] for star in stars]))

calibmags = np.array([star[1] for star in stars])


#print calibmags
#print instmags
zps = calibmags - instmags

print zps
print np.mean(zps), np.std(zps)

