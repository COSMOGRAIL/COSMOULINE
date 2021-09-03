#
#	We make a plot of (re)normalization coefficients (basically to cross check that everyhting went right)
#

# give a list of fieldnames : ["medcoeff", ...]

tocompare = ["medcoeff", "renormacg"]



exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *

from numpy import *
import matplotlib.pyplot as plt

db = KirbyBase()
allimages = db.select(imgdb, ["gogogo", "treatme"], [True, True], returnType='dict', sortFields=['setname', 'mhjd'])

plt.figure(figsize=(12,8))	# sets figure size

for fieldname in tocompare:

	coeffs = asarray([x[fieldname] for x in allimages])
		
	label = fieldname

	plt.plot(coeffs, marker = ".", linestyle="None", label = label)



plt.xlabel('Images')
plt.ylabel('Coefficient')

plt.grid(True)
plt.legend()
plt.show()
	

	
