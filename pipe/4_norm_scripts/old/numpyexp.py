from numpy import *

a = asarray([1.0, 2.3, 4.0])

b = asarray([1.0, 2.3, 4.0])

c = a - b

print a
print b
print c


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from numpy import *


db = KirbyBase()
data = db.select(imgdb, ['gogogo'], [True], returnType='dict')


hjd = asarray(map(lambda x:float(x['hjd']), data))
jd = asarray(map(lambda x:float(x['jd']), data))
diff = jd - hjd


