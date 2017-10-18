execfile("../config.py")

import os

folder = workdir + '/ali_full_png/'
os.system("convert "+ folder+"0*.png " + folder+"animation.gif")

 
