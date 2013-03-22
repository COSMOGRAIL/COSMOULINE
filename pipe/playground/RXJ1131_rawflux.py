


execfile("../config.py")
from kirbybase import KirbyBase, KBError
import variousfct
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.dates


db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['mjd'])

#refimage = [image for image in images if image["imgname"]==refimgname][0]


field = "out_dec_full_lens_medcoeff_pyMCSabcd1_D_flux"

values = np.array([image[field] for image in images])

#print values

plt.hist(np.sqrt(values), 30)
plt.show()

