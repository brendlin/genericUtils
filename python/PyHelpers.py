import ROOT
from itertools import product
from array import array

#-------------------------------------------------------------------------
def LoadRootCore() :
    import ROOT
    if 'RootCore' not in ROOT.gSystem.GetLibraries() :
        print 'Loading c++...'
        ROOT.gROOT.ProcessLine (".x $ROOTCOREDIR/scripts/load_packages.C")
        # Some weird bug where functions are not accessible until a class is called
        ROOT.PSL.EDM
    return

#-----------------------------------------------------------------------------------------
def IsFloat(thing) :
    try :
        out = float(thing)
    except ValueError :
        return False
    return True

#-----------------------------------------------------------------------------------------
def IsInt(thing) :
    if not IsFloat(thing) : return False
    return int(float(thing)) == float(thing)

#-----------------------------------------------------------------------------------------
def ConvertToFloat(thing) :
    try :
        out = float(thing)
    except ValueError :
        out = 0
    return out

#-----------------------------------------------------------------------------------------
def ConvertToInt(thing) :
    try :
        out = int(thing)
    except ValueError :
        out = 0
    return out

#-------------------------------------------------------------------------
def PrintNumberOfEvents(hist,isUnicode=False) :
    import math
    import ROOT

    pm = u"\u00B1"
    sumw2 = sum(list(hist.GetSumw2()))

    if issubclass(type(hist),ROOT.TH2) :
        integral = hist.Integral(0,hist.GetNbinsX()+1,0,hist.GetNbinsY()+1)
    elif issubclass(type(hist),ROOT.TH1) :
        integral = hist.Integral(0,hist.GetNbinsX()+1)
    
    text = '%s: %2.2f'%(hist.GetName(),integral)
                        
    if sumw2 :
        text += ' %s %2.2f'%(pm,math.sqrt(sumw2))
    print text.encode('utf-8')
    return text

#-------------------------------------------------------------------------
def PrintCutflow(label,hist,samp_list=[],scientific=False,spreadsheet=False,latex=False) :
    pm = '$\pm$' if latex else u"\u00B1" # unicode +/-
    import ROOT
    if not issubclass(type(hist),ROOT.TH1) :
        print 'problem'
        return
    import math
    colwidth_nevts = 4 # 0.00
    colwidth_err   = 4 # 0.00
    for j in range(hist.GetNbinsY()) : # cut
        for i in range(hist.GetNbinsX()) : # sample
            if samp_list and hist.GetXaxis().GetBinLabel(i+1) not in samp_list : continue
            cont = max(1,hist.GetBinContent(i+1,j+1))
            colwidth_nevts = int(max(colwidth_nevts,3+1+math.floor(math.log(cont)/math.log(10))))
            if scientific :
                colwidth_nevts = 8
            err = max(1,hist.GetBinError(i+1,j+1))
            colwidth_err = int(max(colwidth_err,3+1+math.floor(math.log(err)/math.log(10))))
    
    firstcolwidth = 4
    for i in range(hist.GetNbinsY()) :
        firstcolwidth = int(max(firstcolwidth,len(hist.GetYaxis().GetBinLabel(i+1))))
    firstcolwidth = int(max(firstcolwidth,len(label)))
    firstcolwidth = firstcolwidth + 2

    if spreadsheet :
        firstcolwidth = 25

    colwidth = colwidth_nevts+colwidth_err+6 # 5 for \pm, 1 extra for buffer
    if latex : colwidth += 2
    text = ''
    if not spreadsheet :
        text += label.ljust(firstcolwidth)
        if latex : text += '& '
        for i in range(hist.GetNbinsX()) :
            if samp_list and hist.GetXaxis().GetBinLabel(i+1) not in samp_list : continue
            text += hist.GetXaxis().GetBinLabel(i+1).ljust(colwidth)
            if latex and (i != hist.GetNbinsX()-1) : text += '& '
        if latex : text += '  \\\\'
        text += '\n'
    for j in range(hist.GetNbinsY()) : # cut
        if spreadsheet and hist.GetYaxis().GetBinLabel(j+1) == 'Start' : continue
        text += hist.GetYaxis().GetBinLabel(j+1).ljust(firstcolwidth)
        if latex : text += '& '
        for i in range(hist.GetNbinsX()) : # sample
            if spreadsheet and hist.GetXaxis().GetBinLabel(i+1) == 'data' : continue
            if samp_list and hist.GetXaxis().GetBinLabel(i+1) not in samp_list : continue
            cont = hist.GetBinContent(i+1,j+1)
            err = hist.GetBinError(i+1,j+1)
            if scientific :
                text += ('%.2e'%cont).rjust(colwidth_nevts)
            else :
                text += ('%2.2f'%cont).rjust(colwidth_nevts)
            text += ' %s '%pm
            if scientific :
                text += ('%.2e'%(err)).rjust(colwidth_err)
            else :
                text += ('%2.2f'%(err)).rjust(colwidth_err)
            if latex and (i != hist.GetNbinsX()-1) : text += ' & '
            else : text += '   '
        if latex : text += '\\\\'
        text += '\n'
    if spreadsheet :
        text = text.rstrip('\n')
    print text
    return

#-------------------------------------------------------------------------
def getFile(filename,fatal=True) :
    from ROOT import TFile
    filename = filename.replace('root://hn.at3f/disk/space00/srm/','/xrootd/srm/')
    filename = filename.replace('root://hn.at3f//srm/','/xrootd/srm/')

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

#-------------------------------------------------------------------------
def GetFile(filename,fatal=True) :
    return getFile(filename,fatal)

#-------------------------------------------------------------------------
def getTree(file,tree='') :
    from ROOT import TTree
    nEvents = -1
    returntree = 0
    for item in file.GetListOfKeys() :
        itree = item.ReadObj()
        if tree and itree.GetName() != tree : continue
        if itree.GetName() not in ['photon','egamma','physics','trigger','electron_ID','susy'] :
            continue
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

#-------------------------------------------------------------------------
def GetRootObj(file,name,printWarning=True,fatal=False):
    obj = file.Get(name)
    if not obj :
        if printWarning : print 'Warning in %s: %s does not exist. %s'%(file.GetName(),name,'Fatal; exiting.' if fatal else '')
        if fatal :
            import sys
            sys.exit()
        return 0
    else : return obj

#-------------------------------------------------------------------------
def SaveConfigInOutputDirectory(fileloc,outputdir) :
    import time
    import os
    while True :
        if not os.path.exists(outputdir) :
            time.sleep(2)
            continue
        os.system('cp %s %s/.'%(fileloc,outputdir))
        break
    return

#-------------------------------------------------------------------------
def GetHWWColors() :
    import ROOT
    colors_dict = {'ggww' :ROOT.kBlue-8
                   ,'qqww':ROOT.kBlue-9
                   ,'smww':ROOT.kBlue-9
                   ,'wz'  :ROOT.kMagenta-3
                   ,'zz'  :ROOT.kMagenta-2
                   ,'wzzz':ROOT.kMagenta-3
                   ,'singletop':ROOT.kYellow+2
                   ,'ttbar':ROOT.kYellow+1
                   ,'vvv' :220
                   ,'upsl' :ROOT.kGreen-1
                   ,'jpsi' :ROOT.kGreen-2
                   ,'zjet' :ROOT.kGreen-3
                   ,'zjee' :ROOT.kGreen-4
                   ,'zjmm' :ROOT.kGreen-5
                   ,'zjtt' :ROOT.kGreen-6
                   ,'zgam' :ROOT.kOrange-3
                   ,'wgam' :ROOT.kOrange
                   ,'wjet' :ROOT.kCyan-9
                   ,'wje'  :ROOT.kCyan-8
                   ,'wjm'  :ROOT.kCyan-7
                   ,'wjt'  :ROOT.kCyan-5
                   ,'wgvbs':ROOT.kCyan-6
                   ,'dijet':ROOT.kWhite
                   ,'dijetdd':ROOT.kGray
                   ,'higgs':2
                   }
    return colors_dict

#-------------------------------------------------------------------------
