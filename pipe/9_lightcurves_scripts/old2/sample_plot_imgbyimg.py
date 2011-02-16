execfile("../config.py")
from kirbybase import KirbyBase, KBError
import matplotlib.pyplot as plt
import numpy as np

fieldname_deckeyfilenum = "decfilenum_dec_full1_a_medcoeff_abce1"
fieldname_int = "out_dec_full1_a_medcoeff_abce1_a_int"

db = KirbyBase()
images = db.select(imgdb, [fieldname_deckeyfilenum], ['\d\d*'], returnType='dict', sortFields=['mjd'], useRegExp=True)
# So we have sorted the images by date (important !)

# We "extract" what we want to plot :
ints = np.array([float(image[fieldname_int]) for image in images])
mags = -2.5 * np.log(ints)

xcoords = np.arange(len(images))

# And the plot :
plt.plot(xcoords, mags, 'b.')

# Reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

plt.xlabel('Image number')
plt.ylabel('Magnitude')

plt.show()
