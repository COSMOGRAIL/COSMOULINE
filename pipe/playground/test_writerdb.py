

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))

#from kirbybase import KirbyBase, KBError
#from variousfct import *
#backupfile(imgdb, dbbudir)

from variousfct import *
from rdbexport import *

columns = [{"name":"testA", "data":[1,2,3,4]}, {"name":"gfdgd", "data":[1,4,9,16]}]


writerdb(columns, "test.txt")


