
#
#	put gogogo to False for images that could not be aligned
#	this is not done in the script, so that you can rerun the alignement with another set of parameters
#	if you are not happy with it, without breaking your previoulsy set gogogo flags.
#
#
#
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
    
from config import dbbudir, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import backupfile


workdir = settings['workdir']
backupfile(imgdb, dbbudir, "aliflagupdate")


db = KirbyBase(imgdb)
nbdemotions = db.update(imgdb, ['flagali','treatme'], 
                               ['!=1','True'], 
                               [False, "Could not be aligned."],
                               ['gogogo', 'whynot'])

print("I've kicked", nbdemotions, "images.")

db.pack(imgdb)
