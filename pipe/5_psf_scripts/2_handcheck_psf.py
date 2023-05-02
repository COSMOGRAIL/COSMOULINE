import os
import sys
from tkinter import Tk, Frame, Label, Button
from tkinter.messagebox import askyesno, showwarning
from PIL import ImageTk, Image

sys.path.append('..')
from config import computer, settings, imgdb, psfkey, psfkicklist, psfsplotsdir
from modules.kirbybase import KirbyBase
from modules.variousfct import notify

def construct_image_path(img_name):
    return os.path.join(workdir, psfkey, 'plots',  f"{img_name}.png")
    #return os.path.join(workdir, f"{psfkey}_png",

def update_image_display(img_name):
    img_path = construct_image_path(img_name)

    if resize:
        img = Image.open(img_path)
        img = img.resize((width, height), Image.ANTIALIAS)
        img.save(img_path)

    new_photoimage = ImageTk.PhotoImage(file=img_path)
    w.config(image=new_photoimage)
    w.image = new_photoimage
    decompte.config(text=f"{i}/{len(images) - 1}")

def incri():
    global i
    i += 1
    return i

def decri():
    global i
    i -= 1
    return i

def skip():
    if askyesno("Confirmation of order", "Are you sure you want to put that image in the skiplist?"):
        if images[i] in skiplist_content:
            showwarning("Could you think before clicking ?", "Already in the skiplist, I knew you had Alzheimer!")
        else:
            with open(psfkicklist, "a") as skiplist:
                skiplist.write(f"\n{images[i]}")

        incri()
        update_image_display(images[i])

    else:
        showwarning("gaga", "Stop bothering me")

def keep():
    incri()
    update_image_display(images[i])

def previous():
    decri()
    update_image_display(images[i])

def quit_app():
    message = f"You stopped at the {i}th image, remember that if you want to "
    message += "come back ! (I wrote that in comment of your skiplist in "
    message += "case you have Alzheimer)"
    print(message)
    with open(psfkicklist, "a") as skiplist:
        skiplist.write(f"\n#{i}")

    image_sizes = [Image.open(construct_image_path(img_name)).size for img_name in images]
    unique_sizes = set(image_sizes)

    if len(unique_sizes) == 1:
        print(f"All the images have the same size: {unique_sizes.pop()}")
    else:
        diff_size_imgs = [img for idx, img in enumerate(images) if image_sizes[idx] != image_sizes[0]]
        print(f"{len(diff_size_imgs)} images do not have the same size as the first image ({image_sizes[0]}), here is the list:")
        for img in diff_size_imgs:
            print(img)

    t.destroy()

# Main code
askquestions = settings['askquestions']
workdir = settings['workdir']
withsound = settings['withsound']
db = KirbyBase(imgdb)

if settings['thisisatest']:
    print("This is a test run.")
    imagesdict = db.select(imgdb, ['gogogo', 'treatme', 'testlist'],
                           [True, True, True],
                           returnType='dict',
                           sortFields=['setname', 'mjd'])

elif settings['update']:
    print("This is an update.")
    imagesdict = db.select(imgdb, ['gogogo', 'treatme', 'updating'],
                           [True, True, True],
                           returnType='dict',
                           sortFields=['setname', 'mjd'])

else:
    imagesdict = db.select(imgdb, ['gogogo', 'treatme'],
                           [True, True],
                           returnType='dict',
                           sortFields=['setname', 'mjd'])

images = [image['imgname'] for image in imagesdict]

start_image_index = int(input("Which image do you want to start from? (For the first image write 0 ...) "))
i = start_image_index

resize = input("Do you want to resize? (yes/no) This is useful if your PSF uses over 6 stars otherwise it just slows the program.") == 'yes'

if resize:
    dimension = int(input("What dimension? (1 for 1200/950, 2 for 1900/1150, 3 for 1600/968, 4 to enter your dimension"))

    if dimension == 1:
        width, height = 1200, 950
    elif dimension == 2:
        width, height = 1900, 1150
    elif dimension == 3:
        width, height = 1600, 968
    elif dimension == 4:
        width, height = int(input("Width?")), int(input("Height?"))

t = Tk()

if os.path.isfile(psfkicklist):
    print("The psfkicklist already exists:")
else:
    os.system(f"touch {psfkicklist}")
    print("I have just touched the psfkicklist for you:")

with open(psfkicklist, "r") as skipl:
    skiplist_content = skipl.read().split("\n")

frame = Frame(t)
frame.pack()


photoimage = ImageTk.PhotoImage(file=construct_image_path(images[i]))
w = Label(t, image=photoimage)
w.pack()


bouton1 = Button(t, text='Skiplist and next', command=skip)
bouton2 = Button(t, text='Keep it and go next', command=keep)
bouton3 = Button(t, text='Previous', command=previous)
bouton4 = Button(t, text='Quit', command=quit_app)
decompte = Label(t, text=f"{i}/{len(images) - 1}")

for btn in [bouton1, bouton2, bouton3, bouton4, decompte]:
    btn.pack()

bouton1.place(relx=0.45, rely=0.01)
bouton2.place(relx=0.6, rely=0.01)
bouton3.place(relx=0.3, rely=0.01)
bouton4.place(relx=0.85, rely=0.01)
decompte.place(relx=0.1, rely=0.01)

update_image_display(images[i])
t.mainloop()

