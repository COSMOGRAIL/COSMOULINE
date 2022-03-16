exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))

from kirbybase import KirbyBase, KBError
from variousfct import *

if not update:
	raise mterror("update keyword not set to True !")

print("I will update the database with new images in set %s, telescope %s from %s" %(setname, telescopename, rawdir))
print("")
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)

print("If you are sure that everything is all right, I can change the updating flag of the new images to False.")
proquest(True)
print("So be it. Shall your word be my credo, I will fully devote myself to this task and shall not stop until the skies fall upon me.")
print("As I want your FULL ATTENTION here, I'm asking a second time...")
proquest(True)
updateimages = db.select(imgdb, ['gogogo','treatme','updating'], [True, True, True], returnType='dict')
for image in updateimages:
	db.update(imgdb, ['recno'], [image['recno']], [False], ['updating'])
db.pack(imgdb) # always a good idea !
print("...aaaaand done !")
