import sys
import os
# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')

from config import imgdb, settings

from modules.kirbybase import KirbyBase

db = KirbyBase(imgdb)
fields = ['datet', 'mjd', 'imgname', 'telescopename', 'gain', 'gogogo']
reporttxt = db.select(imgdb, ['recno'], 
                             ['*'], fields, 
                             sortFields=['mjd'], returnType='report')


reporttxtfile = open(os.path.join(settings['workdir'], 
                                  "report_chronocontent.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()

print("Done.")
