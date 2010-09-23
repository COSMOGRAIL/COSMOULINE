#	
#	Do the deconvolution
#

execfile("../config.py")
#from kirbybase import KirbyBase, KBError
from variousfct import *
#from readandreplace_fct import *
#import shutil
from datetime import datetime

print "No time to loose, so starting right away ..."
print "Of course I do not update the database here,"
print "so you can go on with something else in the meantime."

starttime = datetime.now()

origdir = os.getcwd()

os.chdir(decdir)
os.system(deconvexe)
os.chdir(origdir)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "I've deconvolved %s in %s ." % (deckey, timetaken))


