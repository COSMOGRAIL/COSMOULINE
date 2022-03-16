"""
A generic script to use if you want to manually tweak a field in the database
"""


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import sys

proquest(askquestions)

#backupfile(imgdb, dbbudir, "modiffield")
db = KirbyBase()
images = db.select(imgdb, ['treatme'], [True], returnType='dict')

print len(images)
sys.exit()
# Adapt here depending on what you want to chantge/update


# Changing the raw path to the images (after an HDD loss...)

#myimgs = [image of images]