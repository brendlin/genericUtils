
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
def GetRootObj(file,name):
    #print 'file       :',file.GetName()
    #print 'object name:',name
    obj = file.Get(name)
    if not obj :
        print 'Warning in',file.GetName(),':',name,'does not exist.'
        return 0
        #sys.exit()
    else : return obj

def GetListOfKeyNames(file,dir='') :
    if dir :
        return list(i.GetName() for i in file.GetDirectory(dir).GetListOfKeys()) 
    else : 
        return list(i.GetName() for i in file.GetListOfKeys()) 

def MakeDir(file,dir,superdir='') :
    if dir not in GetListOfKeyNames(file,superdir) :
        if superdir :
            file.GetDirectory(superdir).mkdir(dir)
        else :
            file.mkdir(dir)
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
def getFile(filename) :
     if ('eosatlas' in filename) or ('castoratlas' in filename) :
          tfile = TXNetFile(filename,'READ')
     else :
          print 'not an eos file'
          tfile = TFile(filename,'READ')
     return tfile

def getTree(file,tree) :
     nEvents = 0
     for item in file.GetListOfKeys() :
          itree = item.ReadObj()
          if type(itree) == type(TTree()) :
               ievents = int(itree.GetEntries())
               if ievents > nEvents :
                    nEvents = ievents
                    returntree = itree
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

