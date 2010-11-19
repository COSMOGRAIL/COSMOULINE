execfile("../config.py")
import shutil
from variousfct import *
from combibynight_fct import *
import time
from numpy import *
from headerstuff import *
import pyfits


jdmed = values(images, "jd")['median']
pythondtmed = DateFromJulianDay(jdmed)
datenightobsmed = pythondtmed.strftime("%Y-%m-%d")


"""


'''
def values(listofimg, key):	# stats of the values within the given nights

	from numpy import array, median, std, min, max, mean
	medvals= 0
	stddevvals= 0
	minvals= 0
	maxvals= 0
	meanvals = 0
	
	values = array([float(image[key]) for image in listofimg])
	medvals = median(values)
	stddevvals = std(values)
	minvals = min(values)
	maxvals = max(values)
	meanvals = mean(values)
	
	return {'median': medvals, 'stddev': stddevvals, 'min': minvals, 'max': maxvals, 'mean':meanvals}
	



fielddict = {"alt":'int'}

imggroup = [{'alt': 1},{'alt':2},{'alt':3},{'alt':4},{'alt':5}]

listrecno = [str(image['alt']) for image in imggroup]

stringrecno = ''
	
for recno in listrecno:
	stringrecno = stringrecno + recno +'_'

stringrecno = stringrecno.strip('_')

print stringrecno
'''

pythondt = DateFromJulianDay(2453320.1494850004)

date = pythondt.strftime("%Y-%m-%d")
datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

print date
print datet
"""
