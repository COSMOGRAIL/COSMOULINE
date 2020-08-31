execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import os
import pickle as pkl

file = os.path.join(configdir, "UM673_C2_db.pkl")
outputname  = os.path.join(workdir, "database_frompkl.dat")

database = pkl.load(file)
database.create(outputname)

database.pack(outputname) # to erase the blank lines