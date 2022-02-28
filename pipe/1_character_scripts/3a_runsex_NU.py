#
#    Runs sextractor on the input images. 
#    Next script will measure seeing + ellipticity.
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

from config import alidir, computer, imgdb, settings, sex
from modules.kirbybase import KirbyBase
from modules.variousfct import proquest, nicetimediff, notify
from datetime import datetime


askquestions = settings['askquestions']

db = KirbyBase()
if settings['thisisatest']:
    print("This is a test run.")
    images = db.select(imgdb, ['gogogo','treatme','testlist'], 
                              [True, True, True], returnType='dict')
elif settings['update']:
    print("This is an update.")
    images = db.select(imgdb, ['gogogo','treatme','updating'], 
                              [True, True, True], returnType='dict')
    askquestions = False
else:
    images = db.select(imgdb, ['gogogo','treatme'], 
                              [True, True], returnType='dict')


nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)
proquest(askquestions)

starttime = datetime.now()


for i,image in enumerate(images):

    print("- " * 30)
    print(i+1, "/", nbrofimages, ":", image['imgname'])
    
    imagepath = os.path.join(alidir, image['imgname']+".fits")
    catfilename = os.path.join(alidir, image['imgname']+".cat")

    saturlevel = image["gain"] * image["saturlevel"] # to convert to electrons
    if image["telescopename"] in ["FORS2"]:
        print("FORS2 detected, switch to fors2 extraction parameters:")
        cmd = f"{sex} {imagepath} -c default_see_template_FORS.sex "
        cmd += f"-PIXEL_SCALE {image['pixsize']:.3f} "
        cmd += f"-SATUR_LEVEL {saturlevel:.3f} "
        cmd += f"-CATALOG_NAME {catfilename}"

    else:
        cmd = f"{sex} {imagepath} -c default_see_template.sex"
        cmd += f" -PIXEL_SCALE {image['pixsize']:.3f} "
        cmd += f"-SATUR_LEVEL {saturlevel:.3f} "
        cmd += f"-CATALOG_NAME {catfilename}"
    os.system(cmd)

timetaken = nicetimediff(datetime.now() - starttime)

notify(computer, settings['withsound'], f"I'm done. It took me {timetaken}")
