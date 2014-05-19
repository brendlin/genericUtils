from ROOT import TFile,TTree,TGraph,TH1F,TLine
from array import array

def MakeListMatrix(*lists) :
    lol = list(range(len(x)) for x in lists)
    a = []
    if len(lol) < 1 : return []
    if len(lol) > 5 : return []
    for i in lol[0] :
        a.append([])
        if len(lol) < 2 : continue
        for j in lol[1] :
            a[i].append([])
            if len(lol) < 3 : continue
            for k in lol[2] :
                a[i][j].append([])
                if len(lol) < 4 : continue
                for l in lol[3] :
                    a[i][j][k].append([])
                    if len(lol) < 5 : continue
                    for m in lol[4] :
                        a[i][j][k][l].append([])
    return a

def MakeDictMatrix(*lists) :
    #
    # Makes a dictionary matrix, up to 5 layers deep.
    #
    lol = list(range(len(x)) for x in lists)
    a = dict()
    if len(lol) < 1 : return dict()
    if len(lol) > 5 : return dict()
    for i in lol[0] :
        a[lists[0][i]] = dict()
        if len(lol) < 2 : continue
        for j in lol[1] :
            a[lists[0][i]][lists[1][j]] = dict()
            if len(lol) < 3 : continue
            for k in lol[2] :
                a[lists[0][i]][lists[1][j]][lists[2][k]] = dict()
                if len(lol) < 4 : continue
                for l in lol[3] :
                    a[lists[0][i]][lists[1][j]][lists[2][k]][lists[3][l]] = dict()
                    if len(lol) < 5 : continue
                    for m in lol[4] :
                        a[lists[0][i]][lists[1][j]][lists[2][k]][lists[3][l]][lists[4][m]] = 0
    return a

def listKeys(dir,subdir='') :
    if subdir : dir = dir.Get(subdir)
    for i in dir.GetListOfKeys() : print i.GetName()

#----------------------------------------------------
def GetRootObj(file,name,printWarning=True,fatal=False):
    obj = file.Get(name)
    if not obj :
        if printWarning : print 'Warning in %s: %s does not exist. %s'%(file.GetName(),name,'Fatal; exiting.' if fatal else '')
        if fatal :
            import sys
            sys.exit()
        return 0
    else : return obj

def CheckRootObj(file,name) :
    return GetRootObj(file,name,printWarning=False)

def GetListOfKeyNames(file,dir='') :
    if dir :
        return list(i.GetName() for i in file.GetDirectory(dir).GetListOfKeys()) 
    else : 
        return list(i.GetName() for i in file.GetListOfKeys()) 

def MakeDir(file,dir,superdir='') :
    if superdir : dir = '/'.join(superdir,dir)
    MakeDirV2(file,dir)
#     if dir not in GetListOfKeyNames(file,superdir) :
#         if superdir :
#             file.GetDirectory(superdir).mkdir(dir)
#         else :
#             file.mkdir(dir)
    return

def MakeDirV2(file,dir) :
    dirs = dir.split('/')
    for i in range(dirs.count('')) :
        dirs.remove('')
    for i in range(len(dirs)) :
        if dirs[i] not in GetListOfKeyNames(file,'/'.join(dirs[:i])) :
            file.GetDirectory('/'.join(dirs[:i])).mkdir(dirs[i])
    return file.GetDirectory(dir)

#------------------------------------------------------------------
def GetInHMS(seconds):
    seconds = int(seconds)
    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes
    return "%02d:%02d:%02d" % (hours, minutes, seconds)

#------------------------------------------------------------------
def GetFile(filename,fatal=True) :
    if ('eosatlas' in filename) or ('castoratlas' in filename) :
        tfile = TXNetFile(filename,'READ')
    else :
        #print 'not an eos file'
        tfile = TFile(filename,'READ')
    if tfile.IsZombie() and fatal :
        print 'Fatal. Exiting.'
        import sys
        sys.exit()
    return tfile

def getTree(file,tree='') :
    nEvents = -1
    returntree = 0
    for item in file.GetListOfKeys() :
        itree = item.ReadObj()
        if tree and itree.GetName() != tree : continue
        if itree.GetName() not in ['photon','egamma','physics'] : continue
        if type(itree) == type(TTree()) :
            ievents = int(itree.GetEntries())
            if ievents > nEvents :
                nEvents = ievents
                returntree = itree
    if tree and (not returntree) :
        print 'Error! Tree %s not found! Trying to find any tree.'%tree
        return getTree(file)
    if not returntree : print 'Error! Tree not found!',file
    return returntree

#--------------------------------------------------------------------------------
def CopyV2(indir,outdir,keys=[]) :
    #print 'indir:',indir.GetName()
    #print 'outdir:',outdir.GetName()
    for i in indir.GetListOfKeys() :
        n = i.GetName()
        if i.GetClassName() == 'TDirectoryFile' :
            #print 'making dir',n
            MakeDirV2(outdir,n)
            CopyV2(indir.GetDirectory(n),outdir.GetDirectory(n))
        else :
            if n in list(a.GetName() for a in outdir.GetListOfKeys()) :
                print 'Error! Hist already exists!'
                continue
            if keys and not (True in (k in n for k in keys)) : continue
            outdir.cd()
            i.ReadObj().Write()
    #print 'copy finsihed'
    return

def printArray(lists,brackets='{}',nsf=5,duplicatefirst=False) :
    sig_fig_str = '%'+str(4+nsf)+'.'+str(nsf)+'f'
    lb,rb = brackets[0],brackets[1]
    text = ''
    if lb == '{' : text += '{'
    for l in range(len(lists)) :
        if not l : text += lb
        for m in range(len(lists[l])) :
            if not m : text += lb
            n = 1
            if not m and duplicatefirst : n = 2
            if type(lists[l][m]) == type([])      : text += ','.join([sig_fig_str%(0.)]*n)
            if type(lists[l][m]) == type(int())   : lists[l][m] = float(lists[l][m])
            if type(lists[l][m]) == type(float()) : text += ','.join([sig_fig_str%lists[l][m]]*n)
            if m+1 == len(lists[l]) : text += rb
            else : text += ','
        if l+1 == len(lists) : text += rb
        else : text += ','
        if l+1 == len(lists) and rb == '}' : text += '};'
        text += '\n'
    print text
    return text

def TGraphFromLists(x,y) :
    xx = array('d',x)
    yy = array('d',y)
    return TGraph(len(xx),xx,yy)

def HistThief(name,can,xbounds,doErrors=True) :
    values = dict()
    errors = dict()
    for y in can.GetListOfPrimitives() :
        if type(y) == type(TLine()) :
            values[y.GetX1()] = y.GetY1()
            errors[y.GetX1()] = abs(y.GetY1()-y.GetY2())
    x = array('d',xbounds)
    tmp = TH1F(name,name,len(x)-1,x)
    for i in range(tmp.GetNbinsX()) :
        tmp.SetBinContent(i+1,values[sorted(values.keys())[i]])
        if doErrors : 
            tmp.SetBinError(i+1,errors[sorted(values.keys())[i]])
        print '%04.4f pm %04.4f'%(tmp.GetBinContent(i+1),tmp.GetBinError(i+1))
    return tmp

def CleanNameForMacro(nm) :
    nm = nm.replace(' ','_')
    nm = nm.replace('_','PUPPIES')
    nm = ''.join(ch for ch in nm if ch.isalnum())
    nm = nm.replace('PUPPIES','_')
    return nm
