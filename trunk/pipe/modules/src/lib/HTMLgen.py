import utils
import get_sky
from HTags import *
import help 



class Website():
    def __init__(self):
        self.data = {}
        self.pages = {'start':StartP(self.data)}
        self.active = 'start'
        self.body = self.html = self.js = self.head = None
        self.menu = self.__get_menu()
        self.get_page('start')
    
    def get_page(self, pagename):
        #TODO: improve robustness (check pagename)
        self.active = pagename
        self.js = self.pages[self.active].js
        self.head = HEAD(TITLE('pyMCS')+
                         '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'+
                         LINK(rel="stylesheet",
                              media="all",
                              type="text/css",
                              href='/lib/css/menu_style.css')+
                         SCRIPT(type="text/javascript", src="/lib/css/scripts.js")+
                         self.js) 
        self.body = self.pages[self.active].content
        console = """<A HREF="#" onClick="window.open('/console','console', 'toolbar=0, location=0, directories=0, status=0, scrollbars=1, resizable=1, copyhistory=0, menuBar=0, width=600, height=300'); return(false)">console</A>"""
        self.html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        self.html += HTML(self.head+ DIV(\
                          BODY(DIV(DIV(self.menu, Class="menu bubplastic horizontal blue")+BR()+
                               DIV(self.body+BR()+BR()+HR()+ DIV("(c) EPFL - 2009"),
                                   Class='pagecont'), Class="page")+
                               DIV(console, Class='console'), id='body')))
        return str(self.html)
    
    def update(self, pagename, args):
        for arg in args:
            self.data[arg] = args[arg]
        self.pages[pagename].update(args)
        
    def update_all(self, args): 
        for arg in args:
            self.data[arg] = args[arg] 
        for p in self.pages:
            self.pages[p].update(args) 
            
    def add_page(self, pagename, page):
        self.pages[pagename] = page
        self.menu = self.__get_menu()
    
    def __get_menu(self):
        #TODO: change the color of the active page
        elements = ['start', 'config', 'prepare', 'moffat', 'gaussians']
        menu = UL()
        for e in elements:
            if e in self.pages:
                a = A(SPAN(e, Class="menu_ar"), href='/'+e)
                menu <= LI(SPAN(a, Class="menu_r"))
        menu += BR(Class="clearit")
        return menu
        
class Page():
    def __init__(self, data):
        self.data = data
        self.content = ''
        self.js = ''
            
    def update(self, args):
        for arg in args:
            self.data[arg] = args[arg]
        self._build()
    
    def _build(self):
        pass
        
        
class StartP(Page):
    def __init__(self, data):
        Page.__init__(self, data)
        self._build()
    
    def _build(self):
        utils.checkDic(['cfg_file'], self.data)
        title = H1('Welcome to the pyMCS page')
        form = FORM(action='/prepare', method='POST')
        form <= INPUT(type='radio', name='cfg', value='new', id='new')+'<label for="new">Start from scratch</label>'+BR()
        if self.data['cfg_file'] is None:
            form <= INPUT(type='radio', name='cfg', value='old', id='old')+'<label for="old">Use existing config file:</label>'+BR()
        else:
            form <= INPUT(type='radio', name='cfg', value='old', id='old', checked=True)+'<label for="old">Use existing config file</label> (currently: '+self.data['cfg_file']+')'+BR()
        form <= INPUT(type='file', name='cfg_file', size='40')+BR()
        form <= INPUT(type='submit', name='proceed_c', value='Next')
        self.content = title+FIELDSET(form)
        
        
class ConfP(Page):
    def __init__(self, data):
        Page.__init__(self, data)
        self._build(first = True)
        
    def _build(self, first=False):
        import string
        utils.checkDic(['cfg_file'], self.data)
        title = H1('Configuration')+BR()+help.section['config']+BR()+BR()
        form = FORM(action='/prepare', method='POST')
        file = open(self.data['cfg_file'], "r")
        while True:
            line = file.readline()
            if not line:
                break
            if len(line) > 2 and '=' in line:
                if line[-1] != '\n':
                    line += '\n'
                name, val = line.split("=")
                name, val = string.strip(name), string.strip(val)
                if first:
                    val = utils.string2val({name:val})[name]
                    self.data[name] = val
                else:
                    val = self.data[name]    
                if name == 'FILENAME':
                    if type(val) == type('') and val != '' and val != 'None':
                        form <= INPUT(type='file', Class='ok', name=name, size = '40')+name+BR()
                    else:
                        form <= INPUT(type='file', Class='bad', name=name, size = '40')+name+BR()
                else:
                    form <= INPUT(type='text', name=name, value=val)+name+BR()
            else:
                while line[0] == '#':
                    line = line[1:]
                if len(line)>1:
                    while line[-2] == '#':
                        line = line[:len(line)-2]+'\n'
                #TODO: add title
                form <= line + BR()
        form <= INPUT(type='submit', name='proceed', value='Next')
        self.content = title+FIELDSET(form)
        file.close()
        

class PrepP(Page):
    def __init__(self, data):
        Page.__init__(self, data)
        self._build()
    
    def __get_sky(self):
        img = utils.get_data('./img/'+self.data['FILENAME'])
        curval = 'Currently:'
        if 'SKY_BACKGROUND' in self.data and 'SIGMA_SKY' in self.data: 
            curval += UL(LI("Sky = "+str(self.data['SKY_BACKGROUND']))+\
                         LI("Sigma = "+str(self.data['SIGMA_SKY'])))
        tog = A("sky computation", href="javascript:toggleContent('sky');")+BR()+\
              P(help.section['sky'])+BR()+curval+BR()
        togcont = FORM(action='/prepare/run_sky', method='POST')
        skyrange, nbins = None, None
        if 'SKY_RANGE' in self.data:
            skyrange = self.data['SKY_RANGE']
        if 'NBINS' in self.data:
            nbins = self.data['NBINS']
        togcont <= BR()+SPAN(SPAN(help.entry['SKY_RANGE'])+INPUT(type='text', Class='ok', 
                    name='SKY_RANGE', value=str(skyrange))+'SKY_RANGE', Class='param')
        togcont <= BR()+SPAN(SPAN(help.entry['NBINS'])+INPUT(type='text', Class='ok', 
                    name='NBINS', value=nbins)+'NBINS', Class='param')
        togcont <= BR()+INPUT(type='submit', name='run', value='run')
        if 'skyfit' in self.data:
            togcont += BR()+A(IMG(src=self.data['skyfit'], width='600'),
                                href=self.data['skyfit'])
        skyB = LI(tog +BR() + DIV(togcont,ID="sky", style="display:block;")+BR())
        return skyB
    
    def __get_stars(self):
        img = utils.get_data('./img/'+self.data['FILENAME'])
        tog = A("star search", href="javascript:toggleContent('candidates');")+\
              BR()+P(help.section['ssearch'])
        togcont = FORM(action='/prepare/run_stars', method='POST')
        sky, sig = None, None
        needed = ['SKY_BACKGROUND', 'SIGMA_SKY', 'IMG_GAIN', 'NOBJ']
        allp = ['NOBJ', 'SKY_BACKGROUND', 'IMG_GAIN', 'SIGMA_SKY', 'VAL_BND']
        isbad = utils.isBad(needed, self.data)
        for e in allp:
            togcont <= BR()+SPAN(SPAN(help.entry[e])+INPUT(type='text', Class=isbad[e], 
                                       name=e, value=self.data[e])+e, Class='param')
        togcont <= BR()+INPUT(type='submit', name='run', value='run')+BR()
        togi = togimg = res = ''
        if 'candidates_pics' in self.data:
            res = DIV("Red: candidates, Green: accepted candidates"+BR()\
                      +A(IMG(src=self.data['candidates_pics'][6], width='600', 
                             onmouseover="TJPzoom(this,'"+self.data['candidates_pics'][5]+"');"),
                             href=self.data['candidates_pics'][5]) + BR())
            togi = BR()+A("Candidates details (toggle):", href="javascript:toggleContent('togimg');")+BR()
#            candmap = MAP(name='candmap')
#            for i, c in enumerate(self.data['clist']):
#                r = max(c.rad)
#                candmap <= AREA(shape='rect', coords='('+str(c.x-c)+','+str(c.y-c)+','+str(c.x+c)+','+str(c.x+c)+')',
#                                Class='candpic', name=cand+str(i)) 
            togimg = DIV(A(IMG(src=self.data['candidates_pics'][0], width='600'), href=self.data['candidates_pics'][0]) + BR())
#            togimg += SCRIPT("preload(sig1,'"+self.data['candidates_pics'][2]+"');\n"+
#                              "preload(sig2,'"+self.data['candidates_pics'][3]+"');\n"+
#                              "preload(sig3,'"+self.data['candidates_pics'][4]+"');\n")
            togimg += DIV('Gaussian residuals:'+BR()+IMG(id='sig',src=self.data['candidates_pics'][1], usemap='#sigmap', alt='', href=self.data['candidates_pics'][1], width='600') + BR())
            
            togimg += MAP(AREA(shape='rect', coords='(0,0,199,100%)', href=self.data['candidates_pics'][2], name='1sig', onMouseOver="flipsig('"+self.data['candidates_pics'][2]+"')", onMouseOut="flipsig('"+self.data['candidates_pics'][1]+"')", alt='one sigma')+
                           AREA(shape='rect', coords='(200,0,399,100%)', href=self.data['candidates_pics'][3], name='2sig', onMouseOver="flipsig('"+self.data['candidates_pics'][3]+"')", onMouseOut="flipsig('"+self.data['candidates_pics'][1]+"')", alt='two sigma')+
                           AREA(shape='rect', coords='(400,0,600,100%)', href=self.data['candidates_pics'][4], name='3sig', onMouseOver="flipsig('"+self.data['candidates_pics'][4]+"')", onMouseOut="flipsig('"+self.data['candidates_pics'][1]+"')", alt='three sigma'), 
                           name='sigmap')
        starB = LI(tog + res + DIV(togcont+togi+DIV(togimg, id="togimg", style="display:none;"),id="candidates", style="display:block;")+BR())
        return starB
    
    def __get_selection(self):
        needed = ['STARS']
        isbad = utils.isBad(needed, self.data)
        tog = A("star selection", href="javascript:toggleContent('select');")+\
              BR()+P(help.section['ssel'])+BR()
        togcont = FORM(action="/moffat", method='POST')#'/moffat')
        size = self.data['STARS']!=None and 10 + 10*len(self.data['STARS']) or 10
        togcont <= 'Candidates:'+BR()+INPUT(type='text', Class=isbad['STARS'], name='STARS', 
                         value=str(self.data['STARS']), size=size)+BR()
        togcont <= 'Or enter the candidates ids:'+BR()+INPUT(type='text', name='c_ids', value='[]', size=20)+BR()
        if isbad['STARS']=='ok':
            togcont <= BR()+'Which candidates would you like to keep?'+BR()
            if 'star_sel' not in self.data:
                l = []
                for e in self.data['STARS']:
                    l += [e]
                self.data['star_sel'] = l
            i = 0
            for s in self.data['STARS']:
                if s in self.data['star_sel']:
                    togcont <= INPUT(type='checkbox', name='star'+str(i), id='star'+str(i),value=i, checked='yes')+'<label for=star'+str(i)+'>Candidate '+str(i+1)+'</label>'+BR()
                else:
                    togcont <= INPUT(type='checkbox', name='star'+str(i), id='star'+str(i),value=i)+'<label for=star'+str(i)+'>Candidate '+str(i+1)+'</label>'+BR()
                i = i+1
        togcont <= INPUT(type='submit', name='gomof', value='proceed to fit')+BR()
        selB = LI(tog + DIV(togcont,id="select", style="display:block;")+BR())
        return selB
    
    def __get_console(self):
        cons =  A("console", href="javascript:toggleCons();")+BR()
        cons += IFRAME(src='/console', id='console', width='100%', height='100%', 
                       frameborder='1',crolling = "auto", style="display:block;")
        cons = DIV(cons, Class='console')
        return cons
        
    def _build(self):
        title = H1('Prepare MCS parameters')+BR()
        self.js = """
<script type="text/javascript">
    function preload(name, src) {
        name = new Image()
        name.src = src
    }
</script>
<script type="text/javascript">
    function toggleContent(id) {
        var contentId = document.getElementById(id);
        contentId.style.display == "block" ? contentId.style.display = "none" : 
        contentId.style.display = "block"; 
    }
</script>
<script type="text/javascript">
    function toggleCons() {
        var cons = document.getElementById('console');
        cons.style.display == "block" ? cons.style.display = "none" : 
        cons.style.display = "block"; 
    }
</script>
<script type="text/javascript">
    function flipsig(src) {
        document.getElementById('sig').src = src;
    }flipsig
</script>
<script type="text/javascript">
    function onConsResponse() {   
        var req = new XMLHttpRequest();
        req.open("GET", "/console", true); 
        req.onreadystatechange = function(){
            if (req.readyState != 4)  { return; }
            console = document.getElementById('console');
            var response = req.responseText;
            console.src = response;
        };    
        req.send(null);    
        setTimeout("refreshcons()",5000);
    }
</script>
<script type="text/javascript">
    function onConsResponse2() {   
        var req = new XMLHttpRequest();
        req.open("GET", "/console", false); 
        console = document.getElementById('console');
        var response = req.responseText;
        console.src = response;
        req.send(null);    
        setTimeout("refreshcons()",2000);
    }
</script>
<script type="text/javascript">
    function refreshcons() {
        onConsResponse();
        setTimeout("onConsResponse2()",2000);
    }
</script>
<script type="text/javascript">
    function sky() {   
        var req = new XMLHttpRequest();
        req.open("GET", "/prepare/run_sky", true); 
        req.onreadystatechange = function(){
            if (req.readyState != 4)  { return; }
                var response = req.responseText;
                document.src = response;
        };    
        req.send(null);    
        refreshcons();
    }
</script>""" 
        skyB = self.__get_sky()
        starB = self.__get_stars()
        selB = self.__get_selection()
        cons = ""#self.__get_console()
        #TODO: change to ul(li+li+li)
        self.content = title +help.section['prepare']+BR()+BR()+HR() + \
                       UL(skyB + HR()) + UL(starB + HR()) + UL(selB) + cons

                            
class ConsP(Page):
    def __init__(self):
        Page.__init__(self,{})
        self._build()
        
    def _build(self):
        cont = 'Application output:\n\n' + PRE(id='output')
        js = """
<script type="text/javascript">
    function check() {
        setTimeout("refresh()", 0);
    }
</script>
<script type="text/javascript">
    function refresh() {
        var req = new XMLHttpRequest();
        req.open("GET", "/console/check", true); 
        req.onreadystatechange = function(){
            if (req.readyState != 4)  { return; }
            document.getElementById('output').innerHTML= req.responseText;
        };    
        req.send(null);
        check();  
    }
</script>""" 
        self.content = HTML(HEAD((TITLE('console'))+js)+
                            BODY(cont, onload='check();'))
        
        
class MofP(Page):
    def __init__(self, data):
        Page.__init__(self, data)
        self._build()
    
    def _build(self):
        par = self.__get_params()
        res = self.__get_results()
        self.content = H1('Moffat fit')+P(help.section['moffit'])+\
                       UL(par) + HR() + res + BR()
        
        
    def __get_results(self):
        needed = ['MOF_PARAMS']
        isbad = utils.isBad(needed, self.data)
        ds9 = ''
        if 'mof_res' in self.data:
            self.js="""
<script type="text/javascript">
    function ds9() {
        var req = new XMLHttpRequest();
        req.open("GET", "/moffat/ds9", true); 
        req.onreadystatechange = function(){
            return;
        };    
        req.send(null);
    }
</script>""" 
            ds9 = A('[Display with DS9]', href="javascript:ds9();", Class='opt')
        res = 'Moffat fit output: '+ds9+BR()
        size = str(200)
        gal = TABLE()
        if 'mofpic' in self.data:
            gal <= TR(TD(DIV(A(IMG(src=self.data['mofpic'], width='250'),
                         href=self.data['mofpic'][5])+DIV('Fitted moffat'), Class='imggal')))
        if 'starpics' in self.data:
            for i, s in enumerate(self.data['starpics']):
                s = DIV(A(IMG(src=s, width=size, 
                              alt='star '+str(i+1)), href=s)+DIV('star '+str(i+1)), Class='imggal')
                m = ''
                if 'difmpics' in self.data:
                    m = DIV(A(IMG(src=self.data['difmpics'][i], width=size,
                                  alt='difm '+str(i+1)),href=self.data['difmpics'][i])+DIV('residuals'), Class='imggal')
                gal <= TR(TD(s) + TD(m)) 
        res += gal
        if 'moftrace' in self.data:
            res += 'Parameters trace:'+BR()+\
                    A(IMG(src=self.data['moftrace'], width='600'),
                      href=self.data['moftrace']) + BR()
        form = FORM(action='/gaussians', method='POST')
        form <= 'Moffat parameters:'+BR()+\
                INPUT(type='text', Class=isbad['MOF_PARAMS'], name='MOF_PARAMS', 
                      value=str(self.data['MOF_PARAMS']), size='40')+BR()
        form <= INPUT(type='submit', name='gogaus', value='go to gaussian fit')+BR()+BR()
        return H2('Results:')+BR() + form + res
        
        
    def __get_params(self):
        needed = ['star_sel', 'SKY_BACKGROUND', 'SIGMA_SKY', 
                  'IMG_GAIN', 'NPIX', 'S_FACT', 'G_RES']
        optp = ['CENTER', 'MOF_INIT', 'MAX_IT', 'MOF_PARAMS']
        isbad = utils.isBad(needed, self.data)
        utils.checkDic(optp, self.data)
        content = FORM(action='/moffat/run_mof', method='POST')
        size = self.data['star_sel']!=None and 10 + 10*len(self.data['star_sel']) or 10
        c1 = H3('Mandatory parameters:')
        c1 += BR()+SPAN(INPUT(type='text', Class=isbad['star_sel'], name='star_sel', 
                 value=self.data['star_sel'], size=size)+'Positions', Class='param')
        del needed[0]
        for e in needed:
            c1 += BR()+SPAN(SPAN(help.entry[e])+INPUT(type='text', Class=isbad[e], 
                       name=e, value=self.data[e])+e, Class='param')
        c2 = H3('Optional parameters:')+BR()
        for e in optp:
            c2 += BR()+SPAN(SPAN(help.entry[e])+INPUT(type='text', Class='ok', 
                   name=e, value=self.data[e])+e, Class='param')
        content <= LI(c1)
        content <= LI(c2)
        content <= INPUT(type='submit', name='run', value='run')+BR()+BR()
        return content
        
        
        
class GausP(Page):
    def __init__(self, data):
        Page.__init__(self, data)
        self._build()
    
    def _build(self):
        par = self.__get_params()
        res = self.__get_results()
        self.content = H1('Gaussians fit')+ BR()+P(help.section['gausfit'])+\
                       BR() + par + HR() + res + BR()
        
    def __get_params(self):
                               
        needed = ['star_sel', 'SKY_BACKGROUND', 'SIGMA_SKY', 'IMG_GAIN', 
                  'NPIX', 'S_FACT', 'G_RES', 'MOF_PARAMS', 'G_STRAT', 
                  'G_SETTINGS', 'NB_RUNS']
        isbad = utils.isBad(needed, self.data)
        content = FORM(action='/gaussians/run_gaus', method='POST')
        size = self.data['star_sel']!=None and 10 + 10*len(self.data['star_sel']) or 10
        c = H3('Parameters:')+BR()+ 'Positions:'+BR()+\
                   INPUT(type='text', Class=isbad['star_sel'], name='star_sel', 
                         value=self.data['star_sel'], size=size)+BR()
        del needed[0]
        for e in needed:
            c += BR()+SPAN(SPAN(help.entry[e])+INPUT(type='text', Class=isbad[e], 
                   name=e, value=self.data[e])+e, Class='param')
        content <= c
        content <= BR()+INPUT(type='submit', name='run', value='run')+BR()+BR()
        return content
         
    def __get_results(self):
        needed = ['G_PARAMS', 'G_POS', 'difgpics', 'difmpics']
        isbad = utils.isBad(needed, self.data)
        res = 'Gaussian fit output:' + BR()
        size = str(200)
        if 'difmpics' in self.data and 'difgpics' in self.data and 'gauspic' in self.data:
            res += A(IMG(src=self.data['gauspic'], width=size), href=self.data['gauspic'])
            i=0
            for s in self.data['difmpics']:
                res += A(IMG(src=s, width=size, alt='difm '+str(i+1)), href=s)
                res += A(IMG(src=self.data['difgpics'][i], width=size, 
                           alt='difg '+str(i+1)),href=self.data['difgpics'][i])+BR()
                i += 1
        form = FORM(action='/deconv', method='POST')
        l = ['G_PARAMS', 'G_POS']
        for e in l:
            form <= BR()+SPAN(SPAN(help.entry[e])+e+':'+BR()+INPUT(type='text', Class=isbad[e], 
                   name=e, value=str(self.data[e]), size='60'), Class='param')
        form <= BR()+INPUT(type='submit', name='run', value='go to deconvolution')+BR()+BR()
        return H2('Results:')+BR() + form + res
    

"""
<script type="text/javascript">
    function toggleContent(id) {
        var contentId = document.getElementById(id);
        contentId.style.display == "block" ? contentId.style.display = "none" : 
        contentId.style.display = "block"; 
    }
</script>
<script type="text/javascript">
    function toggleCons() {
        var cons = document.getElementById('console');
        cons.style.display == "block" ? cons.style.display = "none" : 
        cons.style.display = "block"; 
    }
</script>
<script type="text/javascript">
    function onConsResponse() {   
        var req = new XMLHttpRequest();
        req.open("GET", "/console", true); 
        req.onreadystatechange = function(){
            if (req.readyState != 4)  { return; }
            document.getElementById('console').src = req.responseText;
        };    
        req.send(null);    
        setTimeout("refreshcons()",2000);
    }
</script>
<script type="text/javascript">
    function onConsResponse2() {   
        var req = new XMLHttpRequest();
        req.open("GET", "/console", false); 
        document.getElementById('console').src = req.responseText;
        req.send(null);    
        setTimeout("refreshcons()",2000);
    }
</script>
<script type="text/javascript">
    function refreshcons() {
        onConsResponse2();
    }
</script>
<script type="text/javascript">
    function compute() {
        refreshcons();
        var req = new XMLHttpRequest();
        req.open("GET", "/test2", true); 
        req.onreadystatechange = function(){
            if (req.readyState != 4)  { return; }
            document.src = req.responseText;
        };    
        req.send(null);    
        refreshcons();
    }
</script>""" 
        
        
        
        