
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
from pylab import *

db = KirbyBase()
images = db.select(imgdb, ['gogogo'], [True], returnType='dict')




values = array([image['gain'] for image in images])
	
	
#n, bins, patches = hist(values, 1000, range=(0.0,10.0), histtype='stepfilled', facecolor='grey')
n, bins, patches = hist(values, 100, histtype='stepfilled', facecolor='grey')

	


title('A Nice Histogram', fontsize=18)
show()
	
