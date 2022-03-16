execfile("../config.py")
from kirbybase import KirbyBase, KBError
db = KirbyBase()

import matplotlib.pyplot as plt
import numpy as np

images = db.select(imgdb, ['recno'], ['*'], returnType='dict')
#images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

jds = np.array([float(image['jd']) for image in images])
hjds = np.array([float(image['hjd']) for image in images])

moondist = np.array([float(image['moondist']) for image in images])


plt.plot(jds, hjds - jds, "b.")
plt.show()
