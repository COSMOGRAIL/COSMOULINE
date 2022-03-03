
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
#from variousfct import *
#backupfile(imgdb, dbbudir)

db = KirbyBase(imgdb)

report = db.select(imgdb, ['recno'], ['*'], ['imgname', 'gogogo'], sortFields=['imgname'], returnType='report')

print(report)



