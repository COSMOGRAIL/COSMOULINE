#
#	Histogramm of the measured seeings, for each set.
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
from pylab import * # matplotlib and NumPy etc


db = KirbyBase()

# We read this only once.
images = db.select(imgdb, ['gogogo'], [True], returnType='dict')


mhjds = array([image['mhjd'] for image in images])
mjds = array([image['mjd'] for image in images])

diffs = (mhjds - mjds) * 24.0 * 60.0

figure(1)
plot(mjds, diffs, "r.")
title('MHJD - MJD [minutes]', fontsize=18)
xlabel("MJD [days]")
#show()

moonpercents = array([image['moonpercent'] for image in images])

figure(2)
plot(mjds, moonpercents, "r.")
title('Moon illumination [%]', fontsize=18)
xlabel("MJD [days]")
show()
