execfile("../config.py")
import os,sys
import glob
from kirbybase import KirbyBase, KBError
from variousfct import *
from headerstuff import *
from readandreplace_fct import *
import numpy as np
import star
import shutil

print "I now export the database"

proquest(askquestions)

os.chdir('../9_export_scripts')
os.system('python export_NU.py')

print "That was easy."
