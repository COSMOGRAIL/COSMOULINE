#
#	A little script to inspect the status quo of the testlist flag
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *

fields = ['setname', 'imgname','testcomment']

db = KirbyBase()
report = db.select(imgdb, ['testlist'], ['True'], fields, sortFields=['setname', 'imgname'], returnType='report')
images = db.select(imgdb, ['testlist'], ['True'], returnType='dict')

print report
print "There are %i images selected." % len(images)