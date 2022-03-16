"""
A generic script to use if you want to manually tweak a field in the database
"""


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
import sys

proquest(askquestions)

#backupfile(imgdb, dbbudir, "modiffield")
db = KirbyBase()
images = db.select(imgdb, ['treatme'], [True], returnType='dict')

print(len(images))
sys.exit()
# Adapt here depending on what you want to chantge/update

# Adapt here depending on what you want to chantge/update
for image in images :
    db.update(imgdb, ['recno'], [image['recno']], [True], ['flag_psf_abcdip'])

# Changing the raw path to the images (after an HDD loss...)
db.pack(imgdb)

#myimgs = [image of images]