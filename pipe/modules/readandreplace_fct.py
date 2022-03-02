def justreplace(inputstring, repdict):
    
    template = inputstring
    
    for key, value in list(repdict.items()):
        template = template.replace(key, value)
    
    return template

def justread(inputfilename):
    
    infile = open(inputfilename, 'r')
    content = infile.read()
    infile.close()
    return content




def readouttxt(outtxtfile, nbimg): # function to read the out.txt written by deconv.exe
 
    infile = open(outtxtfile, 'r',encoding="ISO-8859-1")
    content = infile.readlines()
    nblines = len(content)
    print(("Number of lines :", nblines))
    infile.close()
    
    i = 0
    intpostable = []
    while i < nblines:
        line = content[i]
        if line.find("Nombre d")>=0:
            nbiter = line.split()[-1]
            if nbiter[0] == ":":
                nbiter = nbiter[1:]
            nbiter = int(nbiter)
            print(("Number of iterations :", nbiter))
            
        if line.find("  - Num")>=0:
            table = []
            for j in range(i+1, i+1+nbimg):
                values = list(map(float, content[j].split()))
                table.append(values)
            intpostable.append(table)
            i = i+nbimg
        if line.find("* Valeurs finales de z1, z2, delta1 et delta2 :")>=0:
            zdeltatable = []
            for j in range(i+1, i+1+nbimg):
                values = list(map(float, content[j].split()))
                zdeltatable.append(values)
            i = i+nbimg
            
        i = i+1
    
    return intpostable, zdeltatable
    
