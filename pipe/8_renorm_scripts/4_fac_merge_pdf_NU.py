from PyPDF2 import PdfFileWriter, PdfFileReader
import glob
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import plotdir, settings

renormname = settings['renormname']
setnames = settings['setnames']

for setname in setnames:
    pattern = os.path.join(plotdir, f"renorm_{setname}_{renormname}*.pdf")
    files = sorted(glob.glob(pattern))
    print("I will create a single pdf file with all the renormalisation plots") 

    # Creating a routine that appends files to the output file
    def append_pdf(inp,out):
        [output.addPage(inp.getPage(page_num)) for page_num in range(inp.numPages)]

    # Creating an object where pdf pages are appended to
    output = PdfFileWriter()

    # Appending two pdf-pages from two different files

    for fil in files : 
        append_pdf(PdfFileReader(open(fil,"rb")),output)
        

    # Writing all the collected pages to a file
    outpath = os.path.join(plotdir, f"Combined_{setname}_{renormname}.pdf")
    output.write(open(outpath, "wb"))

