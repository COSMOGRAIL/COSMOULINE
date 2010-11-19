#	obssf5
#
#	We read the "normstars.tab" file and identify the corresponding stars,
#	write the good stars with their measured fluxes (various techniques and fluxerrors) into one textfile for
#	each image.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from pylab import * # matplotlib and NumPy etc
#from numpy import *

print "coucou"

db = KirbyBase()
data = db.select(imgdb, ['gogogo'], [True], returnType='dict')

hold(False)

medcoeff = asarray(map(lambda x:float(x['medcoeff']), data))
hjd = asarray(map(lambda x:float(x['hjd']), data))


plot(hjd, medcoeff, 'bo')

title('Normalisation coefficients', fontsize=20)
xlabel('MJD [days]')
#ylabel()

savefig("normcoeff.png")



print "Done."
	
	
