import os
import glob


tarfiles = glob.glob("*.tar")


for tarfile in tarfiles:
	print tarfile
	os.system("tar xvf " + tarfile)
	

