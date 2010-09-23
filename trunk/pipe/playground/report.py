
execfile("../config.py")
from kirbybase import KirbyBase, KBError
#from variousfct import *
#backupfile(imgdb, dbbudir)

db = KirbyBase()

report = db.select(imgdb, ['recno'], ['*'], ['imgname', 'gogogo'], sortFields=['imgname'], returnType='report')

print report



