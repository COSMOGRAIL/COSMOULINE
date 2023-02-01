import numpy as np
import os

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from variousfct import *

#This script is made to mask part of the background to avoid influencing the fit


filename = 'back0001'
outputname = 'back_m'
extension = ".fits"
back = os.path.join(decdir,filename+extension)
inverted = True



(backarray, backheader) = fromfits(back, verbose=False)

backarray[backarray<0.0] = 0.0

tofits(os.path.join(decdir,outputname + extension), backarray, backheader, verbose=False)




