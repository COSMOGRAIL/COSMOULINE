execfile("../config.py")

from kirbybase import KirbyBase, KBError
from variousfct import *

db = KirbyBase()

images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['setname', 'mhjd'])

for image in images:
	print "%s\t%s" % (image["imgname"], image["setname"])
