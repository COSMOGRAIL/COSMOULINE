#
#	Some plots, for the fun of it. Illustrates how nice the database is :-)
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from pylab import * # matplotlib and NumPy etc
#from numpy import *


db = KirbyBase(imgdb)
data = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

hold(False)

medcoeff = asarray([float(x['medcoeff']) for x in data])
medcoefferr = 10*asarray([10*float(x['spancoeff']) for x in data])
jd = asarray([float(x['jd']) for x in data])

#print medcoefferr

#y = [2, 2, 2, 2]
#yerr = [1, 1, 3, 1]
#x = [1, 2, 3, 4]

errorbar(jd, medcoeff, yerr=medcoefferr, fmt='b.')
#axis([0.8*min(jd), 1.2*max(jd), 0.8*min(medcoeff), 1.2*max(medcoeff)])
#axis([0.8*min(x), 1.2*max(x), 0.8*min(y), 1.2*max(y)])
title('Normalisation coefficients')
xlabel('MJD [days]')
#ylabel()

#show()
savefig(plotdir + "normcoeff.png")

# helio plot

#hjd = asarray(map(lambda x:float(x['hjd']), data))
#jd = asarray(map(lambda x:float(x['jd']), data))
#diff = jd - hjd

#for i in range(len(hjd)):
#	print hjd[i], jd[i], diff[i]

#plot(jd, diff, "b.")
#title('HJD')
#xlabel('MJD [days]')
#xlabel('diff')
#show()
#savefig(plotdir + "helio.png")


#histos

seeing = asarray([float(x['seeing']) for x in data])
hist(seeing, 25)
title('Seeing [arcsec]')
savefig(plotdir + "seeing.png")

medcoeff = asarray([float(x['medcoeff']) for x in data])
hist(medcoeff, 25)
title('medcoeff')
savefig(plotdir + "medcoeff.png")

spancoeff = asarray([float(x['spancoeff']) for x in data])
hist(spancoeff, 25)
title('spancoeff')
savefig(plotdir + "spancoeff.png")

geomaprms = asarray([float(x['geomaprms']) for x in data])
hist(geomaprms, 25)
title('geomaprms')
savefig(plotdir + "geomaprms.png")

print("Done.")
	
	
