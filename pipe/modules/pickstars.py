# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use("TkAgg")
import astropy.io.fits as pyfits
from itertools import count, product, islice
from string import ascii_lowercase
from tkinter import Tk, Frame, Label, Canvas, SUNKEN, Toplevel, Scrollbar,\
                    VERTICAL, HORIZONTAL, BOTTOM, LEFT, RIGHT, BOTH, X, Y,\
                    Menu
from tkinter.messagebox import askyesno, showwarning
from PIL import ImageTk
from PIL import Image
try:
    import ImageTk
    import Image
except:
    from PIL import ImageTk
    from PIL import Image
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import alidir, computer, settings, configdir
from modules.variousfct import fromfits
from modules import f2n
from modules import star

askquestions = settings['askquestions']
refimgname = settings['refimgname']
workdir = settings['workdir']
stampsize = settings['stampsize']

#%%




"""
Script that allow to pick the good stars by clicking on the image. 
Still work in progress
Written by Eric Paic, early 2017 version. 
Modified by Vivien Bonvin to fit smoothly (and with less bugs...) 
into the cosmouline pipeline.

2022: tried to remove all the global variables 
"""

from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

import sys


class LoadImage:
    def __init__(self,root,image, regioncat, alphabet):
        global frame
        global top
        global ax
        global f
        global height, width
        frame = Frame(root)
        #Creation of the canvas
        self.canvas = Canvas(frame,width=1000,height=1000, relief=SUNKEN)

        frame.pack()

        #display of the image
        File = image
        self.orig_img = Image.open(File)
        self.img = ImageTk.PhotoImage(self.orig_img)
        self.canvas.create_image(0,0,image=self.img, anchor="nw")

        self.zoomcycle = 0
        self.zimg_id = None
        
        self.regioncat = regioncat
        self.alphabet = alphabet
        
        
        #The dimensions of the png 
        im = Image.open(image)
        width,height = im.size

        #Creation of the stat window
        top = Toplevel()
        top.title("Stats")
        canvastop = Canvas(top, bg="black", width=200, height=200)
        f = Figure(figsize=(5,5))
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

    # if you are on windows, Button-4 and Button-5 are united under
    # MouseWheel and instead of event.num = 5 or 4 you have event.delta = -120 ou 120 
    def zoomer(self,event):
        if (event.num ==4):
            if self.zoomcycle != 5: self.zoomcycle += 1
        elif (event.num==5):
            if self.zoomcycle != 0: self.zoomcycle -= 1
        self.crop(event)

    def zoomer_mac_in(self,event):
        if self.zoomcycle != 5: self.zoomcycle += 1
        print("zoom : ", self.zoomcycle)
        self.crop(event)

    def zoomer_mac_out(self,event):
        if self.zoomcycle != 0: self.zoomcycle -= 1
        print("zoom : ", self.zoomcycle)
        self.crop(event)

    def crop(self,event):
        if self.zimg_id: self.canvas.delete(self.zimg_id)
        if (self.zoomcycle) != 0:
            #to get the real coordinate of the star even after scrolling:
            x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y) 
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


    def writeRegion(self, event, name):
        x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y) #to get the real coordinate of the star even after scrolling
        reg = open(self.regioncat, "a")
        reg.write("\n" + name + "\t"+str((float(x))) + "\t" + str((float(height-y))) + "    10000")
        reg.close()
        self.canvas.create_rectangle(x - stampsize//2, 
                                     y - stampsize//2,
                                     x + stampsize//2,
                                     y + stampsize//2,
                                     outline='red')


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
            name = str(self.alphabet[compteurs[0]-1])
            self.writeRegion(event, name)
  
            compteurs[0] += 1
        else:
            name = choice
            self.writeRegion(event, name)

def Stars():
    global choice
    choice = "star"
    print("star")
    
def lens():
    global choice
    choice = "lens"
    print("lens")

def Empty():
    global choice
    choice = "empty"
    print("empty")

def Nothing():
    global choice
    choice = "nothing"
    print("nothing")

def opencat(starcatalogue):
    cmd = "nedit " + starcatalogue + " &"
    os.system(cmd)


def main(regioncat, workonali=False, z2=1000):
    
    global compteurs
    global choice
    global fact
    global height
    global lenscoord
    global emptycoord
    global bl_corner
    global bl_text
    global carre
    
    lenscoord = [] # at the end it will contain the coordinates of the bottom left corner and the top right corner of the lens region in the following order [x_bl, y_bl, x_tr, y_tr] 
    
    emptycoord = [] # at the end it will contain the coordinates of the bottom left corner and the top right corner of the empty region in the following order [x_bl, y_bl, x_tr, y_tr]
    
    if workonali:
        fitsfile = os.path.join(alidir, refimgname + "_ali.fits")
    else:
        if os.path.isfile(os.path.join(alidir, refimgname + "_skysub.fits")):
            fitsfile = os.path.join(alidir, refimgname + "_skysub.fits") #path to the img_skysub.fits you will display
        else :
            print("Apparently, you removed your non-ali images, I'll try to find your _ali image.")
            fitsfile = os.path.join(alidir, refimgname + "_ali.fits")
    
    image = os.path.join(workdir, "refimg_skysub.fits") #path to the png that will be created from the img_skysub.fits
    
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
    
    #Parameters for conversion from fits to png
    
    (imagea, imageh) = fromfits(fitsfile, verbose = False)
    haut = float(imageh["NAXIS1"]) # Be careful with this if you're not on ECAM, you might have to look for another header ...
    larg = float(imageh["NAXIS2"])    
    
    z1 = 0    
    f2nimg = f2n.fromfits(fitsfile)
    f2nimg.setzscale(z1, z2)
    f2nimg.makepilimage(scale="log", negative=False)
    f2nimg.tonet(image)
    

    
    
    #Storing the value of each pixel of the image
    pxlvalue = pyfits.getdata(fitsfile)
    

    
    if os.path.isfile(regioncat):
        print("The region catalogue already exists :", regioncat)
    else:
        cmd = "touch " + regioncat
        os.system(cmd)
        print("I have just touched the region catalogue for you :", regioncat)
        
    
    
    root = Tk()
    menu = Menu(root)
    root.config(menu=menu)
    filemenu = Menu(menu)
    Catalogue = Menu(menu)
    menu.add_cascade(label="Selection", menu=filemenu)
    filemenu.add_command(label="Stars", command=Stars)
    filemenu.add_command(label="lens", command=lens)
    filemenu.add_command(label="Empty", command=Empty)
    filemenu.add_command(label="Nothing", command=Nothing)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menu.add_cascade(label="Catalogue", menu=Catalogue)
    Catalogue.add_command(label="Open star catalogue", command=opencat)

    root.title("Select stars")
    App = LoadImage(root, image, regioncat, alphabet)

    root.mainloop()



if __name__ == "__main__":
    main('toast.cat')