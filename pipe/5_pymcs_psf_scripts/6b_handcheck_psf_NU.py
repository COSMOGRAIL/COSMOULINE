import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

from tkinter import Tk, Frame, Label, Button
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

from config import computer, settings, imgdb, psfkey, psfkicklist
from modules.kirbybase import KirbyBase
from modules.variousfct import notify

askquestions = settings['askquestions']
workdir = settings['workdir']
withsound = settings['withsound']


"""

     You are looking at the most important script of all the pipe.

Be sure to have written the right path for your config.py 
in the execfile and the right psfkey in it. 

There are 4 functions, one for each button. skip() writes
in the skiplist the name of the image you are looking 
at and then displays the next one. keep() and previous() 
simply show respectively the next or previous picture. 
Only skip() and keep() have the ability to resize the 
picture if they are asked to, previous() doesn't need that 
since the resize is permanent (So don't do the skiplist 
looking the picture backwards, or just decomment the 
resizing part in this function). quit() checks if all 
the pictures have the same size, prints the number of the 
last picture you saw and puts it in the skiplist, 
then it closes the window.

"""


db = KirbyBase(imgdb)


if settings['thisisatest']:
    print("This is a test run.")
    imagesdict = db.select(imgdb, ['gogogo','treatme','testlist'], 
                                  [True, True, True], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
if settings['update']:
    print("This is an update.")
    imagesdict = db.select(imgdb, ['gogogo','treatme','updating'], 
                                  [True, True, True], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
    plt.figure(figsize=(8,5))
    plt.scatter(0,0, label='COUCOU')
    plt.xlabel('COUCOU !', fontsize=15)
    plt.ylabel('COUCOU !', fontsize=15)
    plt.legend(loc=6, fontsize=50)
    plt.suptitle('COUCOU !!')
    plt.show()
    message = "Hey Ho ! I need your input here. Look at the PSF of your"
    message += "new images and add the ones you don't like to your skiplist !"
    notify(computer, withsound, message)

else:
    imagesdict = db.select(imgdb, ['gogogo','treatme'], 
                                  [True, True], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])

# As the map function didn't want to work, I made my ersatz. 
images = []
for i,image in enumerate(imagesdict):
    images.append(image['imgname'])
        
message1 = "Which image do you want to start from ? "
message1 += "(For the first image write 0 ...) "
nb = eval(input(message1))
i = int(nb)

message2 = "Do you want to resize ? (yes/no) This is useful if your PSF "
message2 += "uses over 6 stars otherwise it just slows the program."
resize = input(message2)

#Dimension of the window if you decide to resize
if resize == 'yes':
    message3 = "What dimension ?(1 for 1200/950, 2 for 1900/1150, "
    message3 += "3 for 1600/968, 4 to enter your dimension"
    dimension = eval(input(message3))
    
    if dimension == '1':
        width = 1200 
        height = 950
    elif dimension == '2':
        width = 1900
        height = 1150
    elif dimension == '3':
        width = 1600
        height = 968
    elif dimension == '4':
        width = int(eval(input("Width ?")))
        height = int(eval(input("Height ?")))
    
t = Tk() 


if os.path.isfile(psfkicklist):
    print("The psfkicklist already exists :")
else:
    cmd = "touch " + psfkicklist
    os.system(cmd)
    print("I have just touched the psfkicklist for you :")
print(psfkicklist)

# Functions to increase or decrease i
def incri():
    global i
    i += 1
    return i
    
def decri():
    global i
    i-= 1
    return i

# Useful to see wether or not the picture you want to put 
# in the skiplist is already there
skipl = open(psfkicklist, "r")
liste = skipl.read()
colonne = liste.split("\n")
skipl.close()
    

def skip():
    global t
    global image 
    global psfkicklist
    global skiplist
    global colonne
    if askyesno("Confirmation of order",
                   "Are you sure you want to put that image in the skiplist?"):
        if (images[i] in colonne): 
            showwarning("Could you think before clicking ?", 
                        "Already in the skiplist, I knew you had Alzheimer !")
        else :
            skiplist = open(psfkicklist, "a")
            skiplist.write("\n" + images[i])
            skiplist.close()
        
        
        incri()    
        if resize == "yes":
            im4= Image.open(workdir+'/'+psfkey+"_png/"+str(images[i])+".png")
            im4=im4.resize((width,height), Image.ANTIALIAS)
            im4.save(workdir+'/'+psfkey+"_png/"+str(images[i])+".png")
            myimg = workdir+'/'+psfkey+"_png/"+images[i]+".png"
        else:
            myimg = workdir+'/'+psfkey+"_png/"+images[i]+".png"
        new_photoimage = ImageTk.PhotoImage(file=myimg)
        image = myimg
        w.config(image = new_photoimage)
        decompte.config(text = str(i) + '/'+ str(len(images)-1))
        w.after(skip)

    else:
        showwarning("gaga","Stop bothering me ")
        
    
def keep():
    global t
    global image
    incri()
    
    if resize == "yes":
        im3= Image.open(workdir+'/'+psfkey+"_png/"+str(images[i])+".png")
        im3=im3.resize((width,height), Image.ANTIALIAS)
        im3.save(workdir+'/'+psfkey+"_png/"+str(images[i])+".png")
        myimg = workdir+'/'+psfkey+"_png/"+images[i]+".png"
    else:
        myimg = workdir+'/'+psfkey+"_png/"+images[i]+".png"
            
    
    new_photoimage = ImageTk.PhotoImage(file=myimg)
    image = myimg
    w.config(image = new_photoimage)
    decompte.config(text = str(i) + '/'+ str(len(images)-1))
    w.after(keep)

    

def previous():
    global t
    global image
    decri()

    myimg = workdir+'/'+psfkey+"_png/"+images[i]+".png"
    
        
    new_photoimage = ImageTk.PhotoImage(file=myimg)
    image = myimg
    w.config(image = new_photoimage)
    decompte.config(text = str(i) + '/'+ str(len(images)-1))
    w.after(previous)

liste2 = [] # List of the sizes of all the images
liste3 = [] # List of the images that don't have the same size

def quit():
    global t
    global i
    message = f"You stopped at the {i}th image, remember that if you want to "
    message += "come back ! (I wrote that in comment of your skiplist in "
    message += "case you have Alzheimer)"
    print(message)
    skiplist = open(psfkicklist, "a")
    skiplist.write("\n #" + str(i) )
    skiplist.close()
    
    for i,elem in enumerate(images):
        im=Image.open(workdir+'/'+psfkey+'_png/'+str(images[i])+'.png')
        liste2.append(im.size)
    for i in range(1,783):
        if liste2[i]!=liste2[0]:
            liste3.append(images[i])
    if liste3 == []:
        print(('All the images have the same size : ' + str(liste2[0])))
    else:
        message  = f"{len(liste3)} images do not have the same size "
        message += f"as the first image ({liste2[0]}), here is the list:"
        print(message)
        for i, elem in enumerate(liste3):
            print((str(elem)))
        
    t.destroy()
    
    
    
if resize == "yes":
    im1= Image.open(workdir+'/'+psfkey+"_png/"+str(images[i])+".png")
    im1=im1.resize((width,height), Image.ANTIALIAS)
    im1.save(workdir+'/'+psfkey+"_png/"+str(images[i])+".png")
    image = workdir+'/'+psfkey+"_png/"+str(images[i])+".png"
else:
    image = workdir+'/'+psfkey+"_png/"+str(images[i])+".png"



frame = Frame(t)
frame.focus_force()

frame.bind("l", lambda event: keep())

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
frame.pack()
t.mainloop()
