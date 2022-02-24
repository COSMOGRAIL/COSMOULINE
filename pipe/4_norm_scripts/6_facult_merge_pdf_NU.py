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
from config import settings, plotdir

askquestions = settings['askquestions']

if os.path.isfile(plotdir + "Combined_pdf.pdf"):
	print("Removing existing stuff")
	print("rm "+plotdir+"Combined_pdf.pdf")
	os.system("rm "+plotdir+"Combined_pdf.pdf")



files = sorted(glob.glob(plotdir + "*.pdf"))
print("I will create a single pdf file with all the plots") 

# Creating a routine that appends files to the output file
def append_pdf(inp,out):
    [output.addPage(inp.getPage(page_num)) for page_num in range(inp.numPages)]

# Creating an object where pdf pages are appended to
output = PdfFileWriter()

# Appending two pdf-pages from two different files

for fil in files : 
	append_pdf(PdfFileReader(open(fil,"rb")),output)
	

# Writing all the collected pages to a file
output.write(open(plotdir + "Combined_pdf.pdf","wb"))
    

