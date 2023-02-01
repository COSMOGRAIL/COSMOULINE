from PyPDF2 import PdfWriter, PdfReader
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from variousfct import *
import glob

if os.path.isfile(plotdir + "Combined_pdf.pdf"):
	print("Removing existing stuff")
	print("rm "+plotdir+"Combined_pdf.pdf")
	os.system("rm "+plotdir+"Combined_pdf.pdf")
	

files = sorted(glob.glob(plotdir + "*.pdf"))
files =[file for file in files if 'sexphotom' in file or 'histo' in file]
print("I will create a single pdf file with all the plots")

# Creating a routine that appends files to the output file
def append_pdf(inp,out):
    [output.add_page(inp.pages[page_num]) for page_num in range(len(inp.pages))]

# Creating an object where pdf pages are appended to
output = PdfWriter()

# Appending two pdf-pages from two different files

for fil in files : 
	append_pdf(PdfReader(open(fil,"rb")),output)
	

# Writing all the collected pages to a file
output.write(open(plotdir + "Combined_pdf.pdf","wb"))
    
if computer == "regor4" :
		print("I can copy the result in your visudir if you want ?")
		proquest(askquestions)
		print("I'll copy the png to your visudir !")
		print("cp " +plotdir + "Combined_pdf.pdf " + visudir)
		os.system("cp " +plotdir + "Combined_pdf.pdf " + visudir)
