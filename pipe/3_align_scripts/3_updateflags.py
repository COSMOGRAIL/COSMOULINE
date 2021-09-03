
#
#	put gogogo to False for images that could not be aligned
#	this is not done in the script, so that you can rerun the alignement with another set of parameters
#	if you are not happy with it, without breaking your previoulsy set gogogo flags.
#
#
#
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *

backupfile(imgdb, dbbudir, "aliflagupdate")


db = KirbyBase()
nbdemotions = db.update(imgdb, ['flagali','treatme'], ['!=1','True'], [False, "Could not be aligned."], ['gogogo', 'whynot'])

print("I've kicked", nbdemotions, "images.")

db.pack(imgdb)
