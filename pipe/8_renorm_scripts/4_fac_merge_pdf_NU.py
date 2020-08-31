from pyPdf import PdfFileWriter, PdfFileReader
import glob
execfile("../config.py")
from variousfct import *

files = sorted(glob.glob(plotdir + "renorm_" + renormname +"*.pdf"))
print "I will create a single pdf file with all the renormalisation plots" 

# Creating a routine that appends files to the output file
def append_pdf(inp,out):
    [output.addPage(inp.getPage(page_num)) for page_num in range(inp.numPages)]

# Creating an object where pdf pages are appended to
output = PdfFileWriter()

# Appending two pdf-pages from two different files

for fil in files : 
	append_pdf(PdfFileReader(open(fil,"rb")),output)
	

# Writing all the collected pages to a file
output.write(open(plotdir + "Combined_"+renormname+".pdf","wb"))

if computer == "regor4":
	print "I can copy it in your visudir if you want." 
	proquest(askquestions)
	
	if not os.path.exists(visudir + "/plots"): 
		os.makedirs(visudir + "/plots")

	os.system("cp "+plotdir+"Combined_"+renormname+".pdf " + visudir + "/plots")
