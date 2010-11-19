#
#	to test the fancy functions
#
#


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from identcoordfct import *


n = 10	# number of sources to use for automatic alignement

	# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['recno'], ['*'], ['recno','imgname','rotator'], returnType='dict')
