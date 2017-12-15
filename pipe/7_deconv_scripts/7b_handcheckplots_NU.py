from Tkinter import *            
from tkMessageBox import *
try:
	import ImageTk
	import Image
except:
	from PIL import ImageTk
	from PIL import Image
execfile("../config.py")
from kirbybase import KirbyBase, KBError 
from variousfct import * 
from readandreplace_fct import *
import matplotlib.pyplot as plt
import star
import os
import shutil
import glob
import pyfits
import datetime


"""
Adaptation of 5/6b to the deconvolution pngs.

The goal here is to remove the deconvolution that have not been done properly, on the (hopefully) few images that were not kicked yet (i.e. unfocused ones)

The flagged images are written in a postdec_skiplist in the config directory that should be manually called in lcmanip.py (see imgskiplistfilename field)

No resize here, since the images are small anyway
"""


db = KirbyBase()

if thisisatest:
	print "This is a test run."
	imagesdict = db.select(imgdb, ['gogogo','treatme','testlist'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
if update:
	print "This is an update."
	imagesdict = db.select(imgdb, ['gogogo','treatme','updating'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	plt.figure(figsize=(8,5))
	plt.scatter(0,0, label='COUCOU')
	plt.xlabel('COUCOU !', fontsize=15)
	plt.ylabel('COUCOU !', fontsize=15)
	plt.legend(loc=6, fontsize=50)
	plt.suptitle('COUCOU !!')
	plt.show()
	notify(computer, withsound, "Hey Ho ! I need your input here. Look at the deconv of your new images and add the ones you don't like to your skiplist !")

else:
	imagesdict = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict', sortFields=['setname', 'mjd'])

# As the map function didn't want to work, I made my ersatz. 
images = []
for i,image in enumerate(imagesdict):
	images.append(image['imgname'])
		
		
nb= raw_input("Which image do you want to start from ? (For the first image write 0 ...) ")
i = int(nb)
t = Tk() 

if os.path.isfile(postdecskiplist):
	print "The postdecskiplist already exists :"
else:
	cmd = "touch " + postdecskiplist
	os.system(cmd)
	print "I have just touched the postdecskiplist for you :"
print postdecskiplist

# Functions to increase or decrease i
def incri():
	global i
	i += 1
	return i
	
def decri():
	global i
	i-= 1
	return i

#Useful to see wether or not the picture you want to put in the skiplist is already there
skipl = open(postdecskiplist, "r")
liste = skipl.read()
colonne = liste.split("\n")
skipl.close()
	

def skip():
	global t
	global image 
	global postdecskiplist
	global skiplist
	global colonne

	if askyesno("Confirmation of order", "Are you sure you want to put that image in the skiplist?"):
		if (images[i] in colonne): 
			showwarning("Better twice than none" , "Already in the skiplist !")
		else :
			skiplist = open(postdecskiplist, "a")
			skiplist.write("\n" + images[i])
			skiplist.close()
		
		
		incri()	
		myimg = decdir+"_png/"+images[i]+".png"
		new_photoimage = ImageTk.PhotoImage(file=myimg)
		image = myimg
		w.config(image = new_photoimage)
		decompte.config(text = str(i) + '/'+ str(len(images)-1))
		w.after(skip)

	else:
		showwarning("If not","Then why ?")
		
	
def keep():
	global t
	global image
	incri()

	myimg = decdir+"_png/"+images[i]+".png"
			
	
	new_photoimage = ImageTk.PhotoImage(file=myimg)
	image = myimg
	w.config(image = new_photoimage)
	decompte.config(text = str(i) + '/'+ str(len(images)-1))
	w.after(keep)

	

def previous():
	global t
	global image
	decri()

	myimg = decdir+"_png/"+images[i]+".png"
	
		
	new_photoimage = ImageTk.PhotoImage(file=myimg)
	image = myimg
	w.config(image = new_photoimage)
	decompte.config(text = str(i) + '/'+ str(len(images)-1))
	w.after(previous)

def quit():
	global t
	global i
	print "You stopped at the ", i, "th image, remember that if you want to come back ! (I wrote that in comment of your skiplist just in case)"
	skiplist = open(postdecskiplist, "a")
	skiplist.write("\n #" + str(i) )
	skiplist.close()

	t.destroy()

image = decdir+"_png/"+str(images[i])+".png"
frame = Frame(t)
frame.pack()


photoimage = ImageTk.PhotoImage(file=image)

w = Label(t, image = photoimage)
w.pack()
bouton1 = Button(t, text ='Skiplist and next', command=skip)
bouton2 = Button(t, text ='Keep it and go next', command=keep)
bouton3 = Button(t, text = 'Previous', command=previous)
bouton4 = Button(t, text = 'Quit ', command = quit)
decompte = Label(t, text = str(i) + '/' + str(len(images)-1))

bouton1.pack()
bouton2.pack()
bouton3.pack()
bouton4.pack()
decompte.pack()
bouton1.place(relx = 0.45, rely = 0.01)
bouton2.place(relx = 0.6, rely = 0.01)
bouton3.place(relx = 0.3, rely = 0.01)
bouton4.place(relx = 0.85, rely = 0.01)
decompte.place(relx = 0.1, rely = 0.01)
t.mainloop()
