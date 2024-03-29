#
#	Histogramm of the measured seeings, for each set.
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *

import matplotlib.pyplot as plt
import numpy as np

#imgdb = "/Users/mtewes/Desktop/vieuxdb.dat"

db = KirbyBase(imgdb)

# We read this only once.
images = db.select(imgdb, ['gogogo'], [True], returnType='dict')

times = [image['mhjd'] for image in images]
ellipticities = [image['ell'] for image in images]

plt.figure(figsize=(6, 3))
plt.scatter(times, ellipticities)
plt.title('')
plt.show()
	
