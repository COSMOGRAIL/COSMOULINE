import sys
import os
from glob import glob


filedir = "/Volumes/Saturn/J1001jan09/work/dec_1_lens_newac1/png/"
os.chdir(filedir)


inputfiles = sorted(glob("*.jpg"))

print inputfiles

for i, inputname in enumerate(inputfiles):
	outputname = "%04i.jpg" % (i+1)
	#print outputname
	os.rename(inputname, outputname)


