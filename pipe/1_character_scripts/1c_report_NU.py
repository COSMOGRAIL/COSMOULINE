exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *


fields = ['datet', 'mjd', 'imgname', 'telescopename', 'gain', 'gogogo']
db = KirbyBase()
reporttxt = db.select(imgdb, ['recno'], ['*'], fields, sortFields=['mjd'], returnType='report')

reporttxtfile = open(os.path.join(workdir, "report_chronocontent.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()

print("Done.")
