from Tkinter import *
execfile("../config.py")
from tkMessageBox import * 
from PIL import ImageTk
from PIL import Image
import os
import glob
import f2n
from variousfct import *
import star
import astropy.io.fits as pyfits
from itertools import count, product, islice
from string import ascii_lowercase

import numpy as np
#~ import matplotlib.pyplot
#~ matplotlib.use('TkAgg')
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot


"""
Script that allow to pick the good stars by clicking on the image. Still work in progress
Written by Eric Paic, early 2017 version. Modified by Vivien Bonvin to fit smoothly (and with less bugs...) into the cosmouline pipeline.
"""

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
#from matplotlib.backend_bases import key_press_handler


from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

import sys

if os.path.isfile(os.path.join(alidir, refimgname + "_skysub.fits")):
	fitsfile = os.path.join(alidir, refimgname + "_skysub.fits") #path to the img_skysub.fits you will display
else :
	print "Apparently, you removed your non-ali images, I'll try to find your _ali image."
	fitsfile = os.path.join(alidir, refimgname + "_ali.fits")

image = os.path.join(workdir, "refimg_skysub.fits") #path to the png that will be created from the img_skysub.fits
alistars = alistarscat #path to the alistars catalogue

# Creation of the list of names for the stars [a, b , ... , z, aa, ab, ..., az]
def multiletters(seq):
	for n in count(1):
		for s in product(seq, repeat=n):
			yield ''.join(s)

alphabet = list(islice(multiletters(ascii_lowercase), 52))
alphabet.append('too')
alphabet.append('many')
alphabet.append('staaaaaaaaaaaaaaaaaaaaaaaaaaaaars')

compteurs= [1,0,0] # first term counts the number of stars selected the second one the number of clicks you did to select the lens region and the third the same number for the empty region

lenscoord = [] # at the end it will contain the coordinates of the botom left corner and the top right corner of the lense region in the following order [x_bl, y_bl, x_tr, y_tr] 

emptycoord = [] # at the end it will contain the coordinates of the botom left corner and the top right corner of the empty region in the following order [x_bl, y_bl, x_tr, y_tr]

#if os.path.isfile(alistars):
 #	ali_f = open(alistars, "r")
	#ali_l = ali_f.read()
	#ali_c = ali_l.split("\n")
	#ali_f.close()
	#last = ali_c[len(ali_c)-2].split('\t')[0]
	#compteurs[0] = alphabet.index(str(last)) + 1		
	#print "The last star you selected is" + last + " I am now gonna draw all the stars you have already selected"


#Parameters for conversion from fits to png

(imagea, imageh) = fromfits(fitsfile, verbose = False)
haut = float(imageh["NAXIS1"]) # Be careful with this if you're not on ECAM, you might have to look for another header ...
larg = float(imageh["NAXIS2"])

#Conversion from fits to png
if os.path.isfile(alistars):
	refmanstars = star.readmancat(alistars)


z1 = 0	
z2 = 1000
f2nimg = f2n.fromfits(fitsfile)
f2nimg.setzscale(z1, z2)
f2nimg.makepilimage(scale = "log", negative = False)
if os.path.isfile(alistars):
	f2nimg.drawstarlist(refmanstars, r = 5, colour = (255, 0, 0))
f2nimg.tonet(image)

#else:
	#print "let's go"


#Storing the value of each pixel of the image
pxlvalue = pyfits.getdata(fitsfile)


#The dimensions of the png 
im = Image.open(image)
width,height = im.size

#factWidth = width/larg
#factHeight = height/haut
#fact = [factWidth, factHeight]

#print height, haut
#

if os.path.isfile(alistars):
	print "The alistars catalogue already exists :"
else:
	cmd = "touch " + alistars
	os.system(cmd)
	print "I have just touched the alistars.cat for you :"
print alistars

class LoadImage:
	def __init__(self,root):
		global frame
		global top
		global ax
		global f
		frame = Frame(root)
		#Creation of the canvas
		self.canvas = Canvas(frame,width=1000,height=1000, relief = SUNKEN)

		frame.pack()

	#display of the image
		File = image
		self.orig_img = Image.open(File)
		self.img = ImageTk.PhotoImage(self.orig_img)
		self.canvas.create_image(0,0,image=self.img, anchor="nw")

		self.zoomcycle = 0
		self.zimg_id = None

		#Creation of the stat window
		top = Toplevel()
		top.title("Stats")
		canvastop = Canvas(top, bg="black", width=200, height=200)
		f = Figure(figsize=(5,5))
			#a = f.add_subplot(111)
		ax = Axes3D(f)
		ax.mouse_init()

		msg = Label(top, text="To plot the value of the pixels in a region, use the right button of your mouse")
		msg.pack()
		f = Figure(figsize=(5,5))
		a = f.add_subplot(111)
		a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
		a.set_title ("Estimation Grid", fontsize=16)
		a.set_ylabel("Y", fontsize=14)
		a.set_xlabel("X", fontsize=14)


			#canvastop = FigureCanvasTkAgg(f, master=top)
			#canvastop.get_tk_widget().pack()
			#canvastop.draw()


		# Creation of scrollbars and shortcuts
		sbarV = Scrollbar(frame, orient=VERTICAL)
		sbarH = Scrollbar(frame, orient=HORIZONTAL)

		sbarV.config(command=self.canvas.yview)
		sbarH.config(command=self.canvas.xview)
		self.canvas.config(yscrollcommand=sbarV.set)
		self.canvas.config(xscrollcommand=sbarH.set)


		sbarV.pack(side=LEFT, fill=Y)
		sbarH.pack(side=BOTTOM, fill=X)
		if computer == "martin":
			#for MAC computer !!!!
			root.bind("<Button-2>", self.select)
			root.bind("space",self.select)
			root.bind("i",self.zoomer_mac_in)
			root.bind("o",self.zoomer_mac_out)
		else :
			root.bind("<Button-3>",self.select)
		root.bind("<Button-4>",self.zoomer)
		root.bind("<Button-5>",self.zoomer)
		#root.bind("<Button-1>",self.stat)
		self.canvas.bind("<Motion>",self.crop)
		self.canvas.pack(side =RIGHT, expand=True, fill=BOTH)
		self.canvas.config(scrollregion=(0,0,width,height))
		self.canvas.config(highlightthickness=0)

	# if you are on windows, Button-4 and Button-5 are united under MouseWheel and instead of event.num = 5 or 4 you have event.delta = -120 ou 120 
	def zoomer(self,event):
		if (event.num ==4):
			if self.zoomcycle != 5: self.zoomcycle += 1
		elif (event.num==5):
			if self.zoomcycle != 0: self.zoomcycle -= 1
		self.crop(event)

	def zoomer_mac_in(self,event):
		if self.zoomcycle != 5: self.zoomcycle += 1
		print "zoom : ", self.zoomcycle
		self.crop(event)

	def zoomer_mac_out(self,event):
		if self.zoomcycle != 0: self.zoomcycle -= 1
		print "zoom : ", self.zoomcycle
		self.crop(event)

	def crop(self,event):
		if self.zimg_id: self.canvas.delete(self.zimg_id)
		if (self.zoomcycle) != 0:
			x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y) #to get the real coordinate of the star even after scrolling
			if self.zoomcycle == 1:
				tmp = self.orig_img.crop((x-45,y-30,x+45,y+30))
			elif self.zoomcycle == 2:
				tmp = self.orig_img.crop((x-30,y-20,x+30,y+20))
			elif self.zoomcycle == 3:
				tmp = self.orig_img.crop((x-32,y-32,x+32,y+32))
			elif self.zoomcycle == 4:
				tmp = self.orig_img.crop((x-15,y-10,x+15,y+10))
			elif self.zoomcycle == 5:
				tmp = self.orig_img.crop((x-6,y-4,x+6,y+4))
		if self.zoomcycle == 3:
				size = 300,300
		else:
			size = 300,200
			#tmp = self.orig_img
			self.zimg = ImageTk.PhotoImage(tmp.resize(size))
			self.zimg_id = self.canvas.create_image(x,y,image=self.zimg)

	def select(self,event):
		global compteurs
		global choice
		global fact
		global height
		global lenscoord
		global emptycoord
		global bl_corner
		global bl_text
		global carre

		if choice == "star":
			x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y) #to get the real coordinate of the star even after scrolling
			ali = open(alistars, "a")
			ali.write("\n" + str(alphabet[compteurs[0]-1]) + "\t"+str((float(x))) + "\t" + str((float(height-y))) + "	10000")
			ali.close()

			self.canvas.create_oval(x+15, y-15, x-15,y+15,outline = "red")
			self.canvas.create_text(x+6,y+6,text=str(alphabet[compteurs[0]-1]),fill="green")
			compteurs[0] += 1
		elif choice == "lense":
			x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y) #to get the real coordinate of the star even after scrolling

			compteurs[1] +=1
			if compteurs[1]%3 ==1:
				bl_corner = self.canvas.create_oval(x+1,y-1, x-1,y+1,outline = "red")
				bl_text = self.canvas.create_text(x+6,y+6,text="Bottom left corner",fill="green")
				lenscoord.append(x)
				lenscoord.append(y)
			elif compteurs[1]%3 ==2:
				if x> lenscoord[0] and y<lenscoord[1]:
					self.canvas.delete(bl_corner)
					self.canvas.delete(bl_text)
					lenscoord.append(x)
					lenscoord.append(y)

					carre=self.canvas.create_rectangle(lenscoord[0],lenscoord[3], lenscoord[2], lenscoord[1],outline="blue")
					if askyesno("Satisfied ?", "I can write the coordinates of the lensregion in settings.py if you wish"):
						settings = os.path.join(configdir, "settings.py")
						set = open(settings,"r")
						set_c = set.read()
						set_line = set_c.split("\n")
						set.close()
						for i,elem in enumerate(set_line):
							if "lensregion" in set_line[i]:
								new_set = 'lensregion = "['+ str(lenscoord[0]).split('.')[0] + ':' +str(lenscoord[2]).split('.')[0]+' , '+ str(height-lenscoord[1]).split('.')[0]+':'+   str(height-lenscoord[3]).split('.')[0]+']"'
								set_line[i]=new_set

						set = open(settings,"w")
						set.write("\n".join(set_line))
						set.close()

				else:
					showwarning("You had only one job ..." , "Please select the the top right corner of your region")
					compteurs[1]-=1
			elif compteurs[1]%3 ==0:
				self.canvas.delete(carre)
				lenscoord = []

		elif choice == "empty":
			x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)#to get the real coordinate of the star even after scrolling
			print "selection of the empty region"
			compteurs[2] +=1
			if compteurs[2]%3 ==1:
				bl_corner = self.canvas.create_oval(x+1, y-1, x-1,y+1,outline = "red")
				bl_text = self.canvas.create_text(x+6,y+6,text="Bottom left corner",fill="green")
				emptycoord.append(x)
				emptycoord.append(y)



			elif compteurs[2]%3 ==2:
				self.canvas.delete(bl_corner)
				self.canvas.delete(bl_text)
				emptycoord.append(x)
				emptycoord.append(y)
				carre=self.canvas.create_rectangle(emptycoord[0],emptycoord[3], emptycoord[2], emptycoord[1],outline="green")
				if askyesno("Satisfied ?", "I can write the coordinates of the lensregion in settings.py if you wish"):
					#settings = "/home/epfl/paic/Desktop/alistar_maker/"+dir+"/settings.py"
					settings = os.path.join(configdir, "settings.py")
					set = open(settings,"r")
					set_c = set.read()
					set_line = set_c.split("\n")
					set.close()
					for i,elem in enumerate(set_line):
						if "emptyregion" in set_line[i]:
							new_set = 'emptyregion = "['+ str(emptycoord[0]).split('.')[0] + ':' +str(emptycoord[2]).split('.')[0]+' , '+ str(height-emptycoord[1]).split('.')[0]+':'+   str(height-emptycoord[3]).split('.')[0]+']"'
							set_line[i]=new_set

					set = open(settings,"w")
					set.write("\n".join(set_line))
					set.close()
			elif compteurs[2]%3 ==0:
				self.canvas.delete(carre)
				emptycoord = []

def Stars():
	global choice
	choice = "star"
	print "star"
	
def Lense():
	global choice
	choice = "lense"
	print "lense"

def Empty():
	global choice
	choice = "empty"
	print "empty"

def Nothing():
	global choice
	choice = "nothing"
	print "nothing"

def openali():
	global alistars
	cmd = "nedit " + alistars + " &"
	os.system(cmd)


if __name__ == '__main__':
	root = Tk()
	menu = Menu(root)
	root.config(menu=menu)
	filemenu = Menu(menu)
	Catalogue = Menu(menu)
	menu.add_cascade(label="Selection", menu=filemenu)
	filemenu.add_command(label="Stars", command=Stars)
	filemenu.add_command(label="Lense", command=Lense)
	filemenu.add_command(label="Empty", command=Empty)
	filemenu.add_command(label="Nothing", command=Nothing)
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=root.quit)
	menu.add_cascade(label="Catalogue", menu=Catalogue)
	Catalogue.add_command(label="Open alistars.cat", command=openali)

	root.title("Select stars")
	App = LoadImage(root)

	root.mainloop()
