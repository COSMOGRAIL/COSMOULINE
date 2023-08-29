from PyPDF2 import PdfWriter, PdfReader
import glob
import sys
import os
from pathlib import Path
# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')
from config import plotdir, settings

normname = settings['normname']
setnames = settings['setnames']

for setname in setnames:
    pattern = os.path.join(plotdir, f"norm_{setname}_{normname}*.pdf")
    files = sorted(glob.glob(pattern))
    print("I will create a single pdf file with all the normalisation plots") 

    # Creating a routine that appends files to the output file
    def append_pdf(inp):
        [output.add_page(inp.pages[page_num]) for page_num in range(len(inp.pages))]

    # Creating an object where pdf pages are appended to
    output = PdfWriter()

    # Appending two pdf-pages from two different files

    for fil in files:
        append_pdf(PdfReader(open(fil, "rb")))

    # Writing all the collected pages to a file
    outpath = os.path.join(plotdir, f"Combined_{setname}_{normname}.pdf")
    output.write(open(outpath, "wb"))
    # ok, remove the originals
    for ff in files:
        Path(ff).unlink()

