execfile("../config.py")
from Tkinter import *
from tkMessageBox import * 
import ImageTk
import Image
import os
import pyfits
import f2n
from variousfct import *
import star
import shutil

'''
This script allows the user to select stars that will directly be written in a stars catalog for further use.
To help with that, the scipt open a second window that zooms on where you have pressed the left button of the mouse on the first picture.
You can either select stars by clicking on the main windows or on the zoom window. 
Moreover it makes it possible to select the lens and empty region and displays what you need to copy-paste into settings.py
'''

alphabet=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
doubleAlphabet=[i+j for i in alphabet for j in alphabet]#aa,ab,ac,....,az,ba,bb,...
catalogStars=alphabet+doubleAlphabet#list that contains the possible names for stars, in the right order
compteur=0#variable used to chose the name of the selected stars

#two flags to handle the first time a region is selected		
nolensregion=True
noemptyregion=True


firststarsincelaunch=True#this flag is used 

#Variables to handle the different steps of the selection of the lens and empty regions
compteur_lens=0
compteur_empty=0

#Some variables to store the lens and empty regions
coinlens1x=0
coinlens2x=0
coinlens1y=0
coinlens2y=0
coinempty1x=0
coinempty1x=0
coinempty1y=0
coinempty2y=0

#this is the size of the stars image, this is what you need to set depending on the screen you are using
haut=1000.0
larg=1000.0

#some parameters that will be necessary for the conversion from .fits to .png
z1 = -40
z2 =  2000

#path to your stars catalog
alistarscat=configdir+"/alistars.cat"

#two dictionaries to handle the unknown numer of graphic objects to help the user to know which star has already been selected
dictWpoints=dict()
dictWnames=dict()
dictWpointsZ=dict()
dictWnamesZ=dict()

#lists to store the information concerning the stars
starslist=list()
nameslist=list()
listcoordx=list()
listcoordy=list()

fitsfile=workdir+"/ali/"+refrefimgname+".fits"#IL FAUT METTRE L'IMAGE DE REFERENCE ICI
pngpath=workdir+"/ali/"+refrefimgname+".png"#ICI NOM DU PNG PROVISOIRE

#Here is the conversion from .fits to .png------------------
f2nimg = f2n.fromfits(fitsfile)


f2nimg.setzscale(z1, z2)
wi,he=f2nimg.numpyarray.shape

if f2nimg.numpyarray.shape[0] > 3000:
	f2nimg.rebin(4)
else:
	f2nimg.rebin(2)

f2nimg.makepilimage(scale = "log", negative = False)
f2nimg.tonet(pngpath)
#---------------------------------------------------------

zoomfactor=5.0#This variable makes it possible to chose how much bigger the image in the zoom window is

#Here the image is resized twice : once for the main windows and once for the zoom window------
im1=Image.open(pngpath)
imzoom=im1.resize((zoomfactor*haut,zoomfactor*larg),Image.ANTIALIAS)
im1=im1.resize((haut,larg),Image.ANTIALIAS)
im1.save(pngpath)
imzoom.save("zoom.png")
#------------------
image=pngpath

#variables useful to change the coordinates between the real and resized images
factWi=wi/larg
factHe=he/haut
factWiZ=wi/(larg*zoomfactor)
factHeZ=he/(haut*zoomfactor)

#Initialization of graphic stuffs---------------------------------------------------------
fenetre=Tk()#main window
fenetre.title(image.split(".")[0])
frame = Frame(fenetre)
frame.pack()
photoimage = ImageTk.PhotoImage(file=image)
photoimagezoom = ImageTk.PhotoImage(file="zoom.png")
canvas = Canvas(fenetre, bg="black", width=larg, height=haut)
w = canvas.create_image(larg/2,haut/2,image=photoimage)
carreE=canvas.create_polygon(0,0,outline="",fill="")
textelens=canvas.create_text(0,0,text="")
texteempty=canvas.create_text(0,0,text="")
var_choix = StringVar()

#So that the interface is easier to use (only two buttons to use), on must chose what he wants to do and always use the left button of the mouse
choix_stars = Radiobutton(fenetre, text="Select stars", variable=var_choix, value="stars")
choix_lens = Radiobutton(fenetre, text="Select lens region", variable=var_choix, value="lens")
champ_label = Label(fenetre, text="No region selected")
choix_empty = Radiobutton(fenetre, text="Select empty region", variable=var_choix, value="empty")
champ_labelE = Label(fenetre, text="No region selected")
choix_stars.pack()
choix_lens.pack()
champ_label.pack()
choix_empty.pack()
champ_labelE.pack()

#Zoom window and its image and instruction
top = Toplevel()
top.title("Zoom")
msg = Label(top, text="To zoom, use the right button of your mouse")
msg.pack()
canvastop = Canvas(top, bg="black", width=200, height=200)
wtop = canvastop.create_image(0,0,image=photoimagezoom)
#-----------------------------------------------------------------------------------------

#if the catalog of stars already exists, this part will read it and take the already selected stars into account----------------
if os.path.isfile(alistarscat):
	fichier = open(alistarscat,"r")
	contenuliste = fichier.read()
	fichier.close()
	if not contenuliste == "" :
		starslist = contenuliste.split("\n")
		starslist = [s.partition('#')[0] for s in starslist]#gestion of the comments
		starslist = [s.strip() for s in starslist]
		starslist = [s for s in starslist if s!=""]
		nameslist = [s.partition('\t')[0] for s in starslist]
		provlist = [s.partition('\t')[2] for s in starslist]
		listcoordx = [float(s.partition('\t')[0])/factWi for s in provlist]
		provlist = [s.partition('\t')[2] for s in provlist]
		listcoordy = [(he-float(s.partition('\t')[0]))/factHe for s in provlist]
		#listcoordzx=[s*factWi/factWiZ for s in listcoordx]
		#listcoordzy=[s*factHe/factHeZ for s in listcoordy]
		if not nameslist[0] == "":
			for i in range(len(nameslist)):
				dictWpoints[nameslist[i]]=canvas.create_oval(listcoordx[i]-1,listcoordy[i]-1,listcoordx[i]+2,listcoordy[i]+2,fill = "red")
				dictWnames[nameslist[i]]=canvas.create_text(listcoordx[i]+6,listcoordy[i]+6,text = nameslist[i],fill = "green")
			lastLetter=nameslist[len(nameslist)-1]
			compteur=catalogStars.index(lastLetter)+1
#-------------------------------------------------------------------------------------------------------------------------------

#Every existing stars can be deleted so a list is created to further use			
starstodelete=Listbox(fenetre,selectmode=MULTIPLE)
starstodelete.pack(side="right")
for i,elem in enumerate(nameslist):
	starstodelete.insert(END,elem)
	

def pointeur(event):
	''' This is the function called when the left button of the mouse is pressed in the main window. It acts differently according what the user wants to do (select stars or a region)'''
	global compteur
	global compteur_lens
	global compteur_empty
	global coinlens1x
	global coinlens2x
	global coinlens1y
	global coinlens2y
	global coinempty1x
	global coinempty2x
	global coinempty1y
	global coinempty2y
	global nolensregion
	global noemptyregion
	global carre
	global carreE
	global textelens
	global texteempty
	global firststarsincelaunch
	global haut
	if var_choix.get()=="stars":#the information concerning the selected stars are stored and its plotted on the main window
		starslist.append(catalogStars[compteur]+"\t"+str(float(event.x*factWi))+"\t"+str(float((haut-event.y)*factHe))+"\t"+str(100000))
		nameslist.append(catalogStars[compteur])
		listcoordx.append(float(event.x*factWi))
		listcoordy.append(float((haut-event.y)*factHe))
		dictWpoints[catalogStars[compteur]]=canvas.create_oval(event.x,event.y,event.x+3,event.y+3,fill="red")#the graphic widgets are stored in a dictionnary so they can easily be named and hence easily deleted
		dictWnames[catalogStars[compteur]]=canvas.create_text(event.x+6,event.y+6,text=catalogStars[compteur],fill="green")
		starstodelete.insert(END,catalogStars[compteur])
		compteur=compteur+1
		firststarsincelaunch=False
	elif var_choix.get()=="lens":#the information concerning the lens region are collected through three steps and then displayed
		if (compteur_lens%3)==0 and not nolensregion:
			champ_label.configure(text="Region has been deleted. Please, select the upper-left corner")
			canvas.delete(carre)
			canvas.delete(textelens)
		elif (compteur_lens%3)==0 and nolensregion:
			champ_label.configure(text="No region selected. Please, select the upper-left corner")
		elif (compteur_lens%3)==1:
			coinlens1x=event.x
			coinlens1y=event.y
			champ_label.configure(text="Upper-left corner : ("+str(coinlens1x*factWi)+","+str(coinlens1y*factHe)+"). Now, select the lower-right corner.")
		else:
			nolensregion=False
			coinlens2x=event.x
			coinlens2y=event.y
			champ_label.configure(text="If satisfied, copy this in settings.py : ["+str(coinlens1x*factWi)+":"+str(coinlens2x*factWi)+","+str(coinlens1y*factHe)+":"+str(coinlens2y*factHe)+"]")
			textelens=canvas.create_text(coinlens1x+30,coinlens1y-10,text="lens region",fill="blue")
			carre=canvas.create_polygon(coinlens1x,coinlens1y, coinlens2x, coinlens1y, coinlens2x, coinlens2y, coinlens1x, coinlens2y,outline="blue",fill="")
		compteur_lens=compteur_lens+1
	elif var_choix.get()=="empty":#same as for the lens region
		if (compteur_empty%3)==0 and not noemptyregion:
			champ_labelE.configure(text="Region has been deleted. Please, select the upper-left corner")
			canvas.delete(carreE)
			canvas.delete(texteempty)
		elif (compteur_empty%3)==0 and noemptyregion:
			champ_labelE.configure(text="No region selected. Please, select the upper-left corner")
		elif (compteur_empty%3)==1:
			coinempty1x=event.x
			coinempty1y=event.y
			champ_labelE.configure(text="Upper-left corner : ("+str(coinempty1x*factWi)+","+str(coinempty1y*factHe)+"). Now, select the lower-right corner.")
		else:
			noemptyregion=False
			coinempty2x=event.x
			coinempty2y=event.y
			champ_labelE.configure(text="If satisfied, copy this in settings.py : ["+str(coinempty1x*factWi)+":"+str(coinempty2x*factWi)+","+str(coinempty1y*factHe)+":"+str(coinempty2y*factHe)+"]")
			texteempty=canvas.create_text(coinempty1x+40,coinempty1y-10,text="empty region",fill="blue")
			carreE=canvas.create_polygon(coinempty1x,coinempty1y, coinempty2x, coinempty1y, coinempty2x, coinempty2y, coinempty1x, coinempty2y,outline="blue",fill="")
		compteur_empty=compteur_empty+1
	else:
		print "You need to chose an option!"
		
def pointeurZoom(event):
	''' This is the function that is called when the left button of the mouse is pressed on the zoom window. 
	It stores the information concerning the newly selected star and plot it on both window.
	For technical reason, the dislay of the stars on the zoom window is not handle so the star disappear of the zoom window as soon as another is selected.'''
	global compteur
	global nameslist
	global starslist
	global listcoordx
	global listcoordy
	global wtop
	global canvastop
	global zoomfactor
	global factWiZ
	global factHeZ
	global dictWnamesZ
	global dictWpointsZ
	global firststarsincelaunch
	if not (compteur==0 or firststarsincelaunch):#if existing, erase the last selected star on the zoom window before drawing the new one
		canvastop.delete(dictWpointsZ[catalogStars[compteur-1]])
		canvastop.delete(dictWnamesZ[catalogStars[compteur-1]])
	coordImagex,coordImagey=canvastop.coords(wtop)
	posx=larg*zoomfactor*0.5-coordImagex+event.x#change of coordinates between the two windows
	posy=haut*zoomfactor*0.5-coordImagey+event.y
	starslist.append(catalogStars[compteur]+"\t"+str(float(posx*factWiZ))+"\t"+str(float((zoomfactor*haut-posy)*factHeZ))+"\t"+str(100000))
	nameslist.append(catalogStars[compteur])
	listcoordx.append(float(posx*factWiZ/factWi))
	listcoordy.append(float((zoomfactor*haut-posy)*factHeZ/factHe))
	starstodelete.insert(END,catalogStars[compteur])
	dictWpointsZ[catalogStars[compteur]]=canvastop.create_oval(event.x,event.y,event.x+3,event.y+3,fill="blue")
	dictWnamesZ[catalogStars[compteur]]=canvastop.create_text(event.x+6,event.y+6,text=catalogStars[compteur],fill="green")
	dictWpoints[catalogStars[compteur]]=canvas.create_oval(listcoordx[-1]-1,listcoordy[-1]-1,listcoordx[-1]+2,listcoordy[-1]+2,fill = "red")
	dictWnames[catalogStars[compteur]]=canvas.create_text(listcoordx[-1]+6,listcoordy[-1]+6,text = nameslist[-1],fill = "green")
	compteur=compteur+1	
	firststarsincelaunch=False

		

def eraseStars():
	'''This function is called when the user press on "Delete selected stars". It erase the information concerning the selected stars and withdraw the graphic widget related'''
	global compteur
	liste=starstodelete.curselection()
	if askyesno("","Are you sure you want to delete the "+str(len(liste))+" stars selected?"):
		for i,elem in enumerate(reversed(liste)):
			a=nameslist[int(elem)]
			canvas.delete(dictWpoints[a])
			canvas.delete(dictWnames[a])
			del starslist[int(elem)]
			del nameslist[int(elem)]
			starstodelete.delete(int(elem))
			compteur=max([catalogStars.index(s) for s in nameslist])+1
			
		
def eraseLast():
	'''This function deletes all information about the last selected stars'''
	global compteur
	a=nameslist[-1]
	canvas.delete(dictWpoints[a])
	canvas.delete(dictWnames[a])
	del starslist[-1]
	del nameslist[-1]
	starstodelete.delete(END)
	compteur=max([catalogStars.index(s) for s in nameslist])+1
		
def eraseAll():
	'''This function deletes all information about stars. In case you want to start over'''
	global compteur
	if askyesno("","Are you sure you want to delete all the stars in the catalog?"):
		for i in reversed(range(len(nameslist))):
			a=nameslist[i]
			canvas.delete(dictWpoints[a])
			canvas.delete(dictWnames[a])
			del starslist[i]
			del nameslist[i]
			starstodelete.delete(i)
			compteur=0
		
def zoomImage(event):
	'''This function is called when the user presses the right button of the mouse on the main window.
	It simply changes the region showed in the zoom window'''
	global nameslist
	global compteur
	global dictWnamesZ
	global dictWpointsZ
	global firststarsincelaunch
	if not (compteur==0 or firststarsincelaunch):
		canvastop.delete(dictWpointsZ[catalogStars[compteur-1]])
		canvastop.delete(dictWnamesZ[catalogStars[compteur-1]])
	coordImagex,coordImagey=canvastop.coords(wtop)
	canvastop.coords(wtop,zoomfactor*(larg/2-event.x+20),zoomfactor*(haut/2-event.y+20))#approximative change of coordinates		

#Here the functions defined above are linked to the way to call them inside the mainloop-------------
bousel = Button(fenetre, text="Delete selec", width=10, command=eraseStars)
bousel.pack(side=RIGHT)		
bousel.place(relx = 0.87, rely = 0.65)

boulast = Button(fenetre, text="Delete last", width=10, command=eraseLast)
boulast.pack(side=RIGHT)		
boulast.place(relx = 0.87, rely = 0.70)

bouall = Button(fenetre, text="Delete all", width=10, command=eraseAll)
bouall.pack(side=RIGHT)		
bouall.place(relx = 0.87, rely = 0.75)
	
canvas.bind("<Button-1>", pointeur)
canvas.bind("<Button-3>",zoomImage)
canvastop.bind("<Button-1>", pointeurZoom)
#-----------------------------------------------------------------------------------------------------
	
canvas.pack()
canvastop.pack()


fenetre.mainloop()#open the windows and enable the use of all functions until the main window is closed

#the file is written here
fichier = open(alistarscat, "w")
for i,elem in enumerate(starslist):
	fichier.write(elem+"\n")
fichier.close()
