
#-------------------------------------------------------------------------
def PrepareBkgHistosForStack(bkg_hists,colors=None,labels=None) :
    from PlotFunctions import KurtColorPalate
    from PyHelpers import GetHWWColors
    if not colors :
        colors = GetHWWColors()
    used_colors = []
    
    if not labels :
        labels = dict()

    # Set colors according to your color dictionary, or the HWW color dictionary
    for i in bkg_hists :
        i.SetLineColor(1)
        i.SetMarkerColor(colors.get(i.GetTitle(),1))
        i.SetFillColor(colors.get(i.GetTitle(),1))
        used_colors.append(i.GetFillColor())
        i.SetLineWidth(1)
        i.SetTitle(labels.get(i.GetTitle(),i.GetTitle()))

    # Set the un-assigned colors to random stuff in this KurtPalate. Make sure the color is unused.
    colors_for_unassigned_samples = KurtColorPalate()
    index = 0
    for i in bkg_hists :
        if i.GetMarkerColor() == 1 :
            while True :
                if colors_for_unassigned_samples[index] in used_colors :
                    index += 1
                else :
                    break
            i.SetMarkerColor(colors_for_unassigned_samples[index])
            i.SetFillColor(colors_for_unassigned_samples[index])
            index += 1

    return

#-------------------------------------------------------------------------
def DrawHistos(name,variable,xlabel,bkg_hists=[],sig_hists=[],data_hist=None,dostack=True,log=False,ratio=False,fb=10) :
    #
    # bkg_hists is a list of background histograms (TH1)
    # sig_hists is a list of signal histograms (TH1)
    # variable is a variable name available in pennSoftLepton/Variables.cxx
    #
    import ROOT
    import PlotFunctions as plotfunc
    import TAxisFunctions as taxisfunc
    
    #
    # Clean up name
    #
    canname = CleanUpName(name)

    #
    # stack, before adding SUSY histograms
    #
    if not ratio :
        can = ROOT.TCanvas(canname,canname,500,500)
        if log : can.SetLogy()
    else :
        can = plotfunc.RatioCanvas(canname,canname,500,500)
        if log : can.GetPrimitive('pad_top').SetLogy()

    if bkg_hists :
        totb = bkg_hists[0].Clone()
        totb.SetNameTitle('SM_%s'%(canname),'remove me')
        totb.SetLineColor(1)
        totb.SetLineWidth(1)
        totb.SetMarkerSize(0)
        totb.SetFillColor(0)
        for i in bkg_hists[1:] :
            totb.Add(i)
        totberror = totb.Clone()
        totberror.SetName(totb.GetName()+'_error')
        totberror.SetTitle('SM (stat)')
        totberror.SetFillColor(12)
        totberror.SetFillStyle(3254)

    for index,i in enumerate(bkg_hists) :
        # if no data, but you specified you wanted a ratio, then do ratio of MC
        if (not dostack) :
            i.SetLineWidth(2)
            i.SetLineColor(i.GetMarkerColor())
        if (index > 0) and (not data_hist) and (not dostack) and (ratio) :
            plotfunc.AddRatio(can,i,bkg_hists[0])
        else :
            plotfunc.AddHistogram(can,i)

    if bkg_hists and dostack :
        plotfunc.Stack(can)
        plotfunc.AddHistogram(can,totberror,drawopt='E2')
        plotfunc.AddHistogram(can,totb,drawopt='hist')

    for h in sig_hists :
        plotfunc.AddHistogram(can,h)

    if data_hist :
        if ratio :
            plotfunc.AddRatio(can,data_hist,totb)
        else :
            plotfunc.AddHistogram(can,data_hist)

    plotfunc.FormatCanvasAxes(can)
    text_lines = [plotfunc.GetSqrtsText(13)]
    if fb > 0 :
        text_lines += [plotfunc.GetLuminosityText(fb)]
    text_lines += [plotfunc.GetAtlasInternalText()]

    if ratio :
        plotfunc.DrawText(can,text_lines,0.2,0.65,0.5,0.90,totalentries=4)
        plotfunc.MakeLegend(can,0.53,0.65,0.92,0.90,totalentries=5,ncolumns=2,skip=['remove me'])
        taxisfunc.SetYaxisRanges(plotfunc.GetBotPad(can),0,2)
    else :
        plotfunc.DrawText(can,text_lines,0.2,0.75,0.5,0.94,totalentries=4)
        plotfunc.MakeLegend(can,0.53,0.75,0.94,0.94,totalentries=5,ncolumns=2,skip=['remove me'])
    plotfunc.SetAxisLabels(can,xlabel,'entries')
    plotfunc.AutoFixAxes(can)
    return can

#-------------------------------------------------------------------------
def GetTreesFromFiles(filelist_csv,treename='physics') :
    import ROOT,os

    files = dict()
    trees = dict()
    keys = []
    for f in filelist_csv.split(',') :
        if not f : continue
        name = f.replace('.root','').replace('/','_').replace('-','_').replace('.','_')
        #
        # regular files
        # 
        files[name] = ROOT.TFile(f)
        if files[name].IsZombie() :
            print 'exiting'
            import sys
            sys.exit()
        keys.append(name)
        trees[name] = files[name].Get(treename)
        if not trees[name] :
            print 'Error! Tree \"%s\" does not exist! Exiting.'%(treename)
            import sys; sys.exit()
    return files,trees,keys

#-------------------------------------------------------------------------
def GetChainFromFiles(filelist_csv,treename='physics',chainname='data') :
    
    import ROOT,os

    files = dict()
    trees = dict()
    keys = [chainname]

    trees[chainname] = ROOT.TChain(treename)

    for f in filelist_csv.split(',') :
        if not f : continue
        name = f.replace('.root','').replace('/','_').replace('-','_').replace('.','_')

        files[name] = ROOT.TFile(f)

        if files[name].IsZombie() :
            print 'exiting'
            import sys
            sys.exit()

        trees[chainname].Add(f)

    print keys[0],'will be composed of',','.join(k for k in files.keys())
    return files,trees,keys

#-------------------------------------------------------------------------
def GetScales(files,trees,keys,options) :

    weights = dict()
    #
    # get weight from file, like sumw or something
    #
    for k in keys :
        if options.weightscale :
            weights[k] = options.weightscale(files[k]) * options.fb

    return weights
    
#-------------------------------------------------------------------------
def GetVariableHistsFromTrees(trees,keys,variable,weight,limits,normalize=False,rebin=[],scales=0) :
    import ROOT
    from array import array
    import PlotFunctions as plotfunc
    import math

    n,low,high = limits

    hists = []
    for k in keys :
        name = CleanUpName('%s_%s'%(variable,k))
        while ROOT.gDirectory.Get(name) :
            #print 'changing name'
            name = name+'x'
        if rebin and type(rebin) == type([]) :
            name = name+'_unrebinned'
        bins = '(%s,%s,%s)'%(n,low,high)
        if (n <= 0) :
            bins = ''
        arg1,arg2,arg3 = '%s>>%s%s'%(variable,name,bins),weight,'egoff'
        #arg1,arg2,arg3 = '%s>>%s'%(variable,name),weight,'egoff'
        print 'tree.Draw(\'%s\',\'%s\',\'%s\')'%(arg1,arg2,arg3)
        tmp = ROOT.gErrorIgnoreLevel
        ROOT.gErrorIgnoreLevel = ROOT.kFatal
        trees[k].Draw(arg1,arg2,arg3)
        ROOT.gErrorIgnoreLevel = tmp

        # if Draw did not work, then exit.
        if not issubclass(type(ROOT.gDirectory.Get(name)),ROOT.TH1) :
            print 'ERROR TTree::Draw failed. Exiting.'
            import sys
            sys.exit()

        if rebin and type(rebin) == type([]) :
            tmp = ROOT.gDirectory.Get(name)
            name = name.replace('_unrebinned','')
            tmp.Rebin(len(rebin)-1,name,array('d',rebin))

        hists.append(ROOT.gDirectory.Get(name))
        if rebin and type(rebin) == type(1) :
            hists[-1].Rebin(rebin)

        if (n <= 0) :
            print 'Changing limits to match those from the first plot.'
            limits[0] = hists[-1].GetNbinsX()
            limits[1] = hists[-1].GetBinLowEdge(1)
            limits[2] = hists[-1].GetBinLowEdge(limits[0]+1)

        #RebinSmoothlyFallingFunction(hists[-1])

        hists[-1].SetTitle(k)
        if scales and (scales[k] != 1) :
            hists[-1].Scale(scales[k])

        # print the yield and error after cuts (includes overflow)
        pm = u"\u00B1"
        print '%s: %2.2f %s %2.2f'%(name,hists[-1].Integral(0,hists[-1].GetNbinsX()+1)
                                    ,pm,math.sqrt(sum(list(hists[-1].GetSumw2()))))        

        if normalize :
            hists[-1].Scale(1/float(hists[-1].Integral()))
        if rebin :
            plotfunc.ConvertToDifferential(hists[-1])

    return hists

#-------------------------------------------------------------------------
def Get2dVariableHistsFromTrees(trees,keys,variable1,variable2,weight,n1,low1,high1,n2,low2,high2
                                ,normalize=False,rebin1=[],rebin2=[],scale=0) :
    import ROOT
    from array import array
    import PlotFunctions as plotfunc
    import math

    def formatfloat(a) :
        a = str(a).rstrip('0') if '.' in str(a) else a
        return a

    n1,low1,high1 = formatfloat(n1),formatfloat(low1),formatfloat(high1)
    n2,low2,high2 = formatfloat(n2),formatfloat(low2),formatfloat(high2)
        
    hists = []
    for k in keys :
        name = '%s_%s_%s'%(variable1,variable2,k)
        name = name.replace('[','_').replace(']','_').replace('(','_').replace(')','_').replace('/','_over_')
        while ROOT.gDirectory.Get(name) :
            #print 'changing name'
            name = name+'x'

        arg1,arg2,arg3 = '%s:%s>>%s(%s,%s,%s,%s,%s,%s)'%(variable2,variable1,name,n1,low1,high1,n2,low2,high2),weight,'egoff'
        print 'tree.Draw(\'%s\',\'%s\',\'%s\')'%(arg1,arg2,arg3)
        tmp = ROOT.gErrorIgnoreLevel
        ROOT.gErrorIgnoreLevel = ROOT.kFatal
        trees[k].Draw(arg1,arg2,arg3)
        ROOT.gErrorIgnoreLevel = tmp

        hists.append(ROOT.gDirectory.Get(name))

        hists[-1].SetTitle(k)
        hists[-1].SetMinimum(-0.00001)

        if scale and (scale != 1) :
            hists[-1].Scale(scale)

        # print the yield and error after cuts (includes overflow)
        pm = u"\u00B1"
        print '%s: %2.2f %s %2.2f'%(name,hists[-1].Integral(0,hists[-1].GetNbinsX()+1
                                                            ,0,hists[-1].GetNbinsY()+1)
                                    ,pm,math.sqrt(sum(list(hists[-1].GetSumw2()))))        

        if normalize :
            hists[-1].Scale(1/float(hists[-1].Integral()))

    return hists

#-------------------------------------------------------------------------
class TreePlottingOptParser :
    def __init__(self) :
        from optparse import OptionParser
        self.p = OptionParser()
        # file steering
        self.p.add_option('--bkgs',type='string',default='',dest='bkgs',help='input files for bkg (csv)')
        self.p.add_option('--signal',type='string',default='',dest='signal',help='input files for signal (csv)')
        self.p.add_option('--data',type='string',default='',dest='data',help='input file for data (csv)')
        
        # can also be specified in the config file
        self.p.add_option('--fb',type='float',default=1,dest='fb',help='int luminosity (fb)')
        self.p.add_option('--treename',type='string',default='physics',dest='treename',help='Treename (physics, CollectionTree)')
        self.p.add_option('-v','--variables',type='string',default='',dest='variables',help='Variables (see Variables.cxx for names)')
        self.p.add_option('-c','--cuts',type='string',default='',dest='cuts',help='cut string')
        self.p.add_option('--weight',type='string',default='',dest='weight',help='Monte Carlo event weight')
        self.p.add_option('--weightscale',type='string',default='',dest='weightscale',help='(built-in) function for non-event weight (xs, feff, etc)')

        # point to config file
        self.p.add_option('--config',type='string',default='',dest='config',help='Input configuration file (python module)')

        # histogram limits - only really useful if you are plotting a single variable
        self.p.add_option('--limits',type='string',default='-1,-1,-1',dest='limits',help='Limits (only useful for single plot')

        # plot manipulation
        self.p.add_option('--ratio',action='store_true',default=False,dest='ratio',help='Plot as a ratio')
        self.p.add_option('--nostack',action='store_true',default=False,dest='nostack',help='do not stack')
        self.p.add_option('--normalize',action='store_true',default=False,dest='normalize',help='normalize')

        # other options
        self.p.add_option('--batch',action='store_true',default=False,dest='batch',help='run in batch mode')
        self.p.add_option('--save',action='store_true',default=False,dest='save',help='save cans to pdf')
        self.p.add_option('--outdir',type='string',default='',dest='outdir',help='output directory')
        self.p.add_option('-l','--log',action='store_true',default=False,dest='log',help='log')
        
    def parse_args(self) :
        import sys,os
        import ROOT
        import importlib
        #LoadRootCore()

        self.options,self.args = self.p.parse_args()

        if self.options.batch :
            ROOT.gROOT.SetBatch(True)
        else :
            ROOT.gROOT.SetBatch(False)

        self.options.stack = not self.options.nostack

        if not self.options.outdir :
            self.options.outdir = os.getcwd()
        
        if self.options.signal and not '.root' in self.options.signal :
            dir = self.options.signal
            self.options.signal = ','.join('%s/%s'%(dir,a) for a in os.listdir(self.options.signal))

        if len(self.options.limits.split(',')) != 3 :
            print 'Error! Please specify --limits using 3 numbers in the format nbins,lowedge,highedge'
            sys.exit()





        # some defaults are not set in the option parser
        for x in ['blindcut','mergesamples','colors','labels','histformat','usermodule'] :
            defaults = {'blindcut':[],
                        'mergesamples':None,
                        'colors':dict(),
                        'labels':dict(),
                        'histformat':dict(),
                        'usermodule':None,
                        }
            setattr(self.options,x,defaults.get(x,None))




        # if you indicate 'HZY' then the function weightscaleHZY() will be used.
        if self.options.weightscale :
            print 'INFO: Using weightscale function weightscale%s(tree)'%(self.options.weightscale)
            self.options.weightscale = eval('weightscale%s'%(self.options.weightscale))
        else :
            def defaultweightscale(tfile) :
                return 1
            self.options.weightscale = defaultweightscale

        if self.options.fb <= 0 :
            self.options.fb = 1.




        # to get your current directory viewable by the code:
        sys.path.append(os.getcwd())
        # Read in options from config file:
        if self.options.config :
            usermodule = importlib.import_module(self.options.config.replace('.py',''))
            self.options.usermodule = usermodule

            for x in ['histformat','weight','weightscale','blindcut'
                      ,'treename','fb','colors','labels','mergesamples','bkgs','data'] :
                if hasattr(usermodule,x) :
                    setattr(self.options,x,getattr(usermodule,x))

            if hasattr(usermodule,'cuts') :
                self.options.cuts = usermodule.cuts
                for i,c in enumerate(self.options.cuts) :
                    self.options.cuts[i] = '('+c+')'

            if hasattr(usermodule,'variables') :
                self.options.variables = ','.join(usermodule.variables)



        
        # add .root to each background name.
        self.options.bkgs = self.options.bkgs.split(',')
        for b in range(len(self.options.bkgs)) :
            if not self.options.bkgs[b] :
                continue
            if '.root' not in self.options.bkgs[b] :
                self.options.bkgs[b] = self.options.bkgs[b]+'.root'
        self.options.bkgs = ','.join(self.options.bkgs)

        # add up multiple data files
        if self.options.data == 'all' :
            dirlist = os.listdir('.')
            datalist = []
            for i in dirlist :
                if (not '.root' in i) or (not 'data' in i) :
                    continue
                datalist.append(i)
            self.options.data = ','.join(datalist)

        if '.root' not in self.options.data :
            self.options.data = self.options.data + '.root'

        if (not self.options.bkgs) and (not self.options.signal) and (not self.options.data) :
            print 'No --bkgs, --signal, or --data specified. Exiting.'
            sys.exit()




        # Prepare stuff related to the variables.
        for v in self.options.variables.split(',') :
            if v == '' : continue
            if v in self.options.histformat.keys() :
                if len(self.options.histformat[v]) < 4 :
                    self.options.histformat[v].append(v)
                continue
            else :
                n,low,high = self.options.limits.split(',')
                self.options.histformat[v] = [int(n),float(low),float(high),v]


        # scripts will be looking for a python list of cuts
        if type(self.options.cuts) == type('') :
            self.options.cuts = [self.options.cuts]

        return self.options,self.args

#-------------------------------------------------------------------------
#
# Save plots (argument is a list of canvases)
#
def doSaving(options,cans) :
    import os,sys
    directory = os.getcwd()
    if not options.save :
        return 
    for can in cans :
        while True :
            name = directory + '/' + can.GetName()+'.pdf'
            try :
                open(name, 'a').close()
                can.Print(name)
                can.Print(name.replace('.pdf','.C'))
                # some weird quirk in can.Print(blah.C) requires us to remove "__1" suffixes
                sed_mac_quirk = ''
                if 'darwin' in sys.platform :
                    sed_mac_quirk = '\'\''
                os.system('sed -i %s \'s/\_\_[0-9]*//g\' %s'%(sed_mac_quirk,name.replace('.pdf','.C')))
                break
            except IOError :
                directory = raw_input('Cannot write to this directory. Specify a different one:')
                directory = directory.replace('~',os.getenv('HOME'))
                if not os.path.exists(directory) :
                    os.makedirs(directory)
    return

#-------------------------------------------------------------------------
#
# Update plots (argument is a list of canvases)
#
def UpdateCanvases(options,cans) :
    if not options.batch :
        for can in cans :
            can.Update()
            if can.GetPrimitive('pad_bot') :
                can.GetPrimitive('pad_bot').Update()
            if can.GetPrimitive('pad_top') :
                can.GetPrimitive('pad_top').Update()                
    return

#-------------------------------------------------------------------------
def MergeSamples(bkg_hists,options) :
    #
    # Yeah so this adds the samples together that you specify, in a resonable
    # order close to the one you specify in the command line "bkgs"
    #
    import math

    if not options.mergesamples :
        return bkg_hists
    bkg_hists_new = []
    bkg_hists_index = dict()
    for i in bkg_hists :
        added = False
        for j in options.mergesamples.keys() :
            if i.GetTitle() not in options.mergesamples[j] :
                continue
            if j in bkg_hists_index.keys() :
                #print 'adding to existing histo'
                bkg_hists_new[bkg_hists_index[j]].Add(i)
                added = True
            else :
                #print 'starting a new histo'
                bkg_hists_index[j] = len(bkg_hists_new)
                bkg_hists_new.append(i)
                bkg_hists_new[-1].SetTitle(j)
                added = True
        if not added :
            bkg_hists_new.append(i)

    for i in bkg_hists_index.keys() :
        pm = u"\u00B1"
        tmphist = bkg_hists_new[bkg_hists_index[i]]
        print '%s: %2.2f %s %2.2f'%(i,tmphist.Integral(0,tmphist.GetNbinsX()+1)
                                    ,pm,math.sqrt(sum(list(tmphist.GetSumw2()))))

    return bkg_hists_new

#-------------------------------------------------------------------------
def RebinSmoothlyFallingFunction(hist) :
    #
    # This function defines a new binning such that the error is not more than 10% in any bin.
    #
    import math
    therange = []
    therange.append(hist.GetBinLowEdge(1))
    binj = 1
    weight = 0
    err2 = 0
    while binj < hist.GetNbinsX() :
        weight += hist.GetBinContent(binj)
        #print weight
        err2 += hist.GetBinError(binj)**2
        if weight > 0 and math.sqrt(err2)/weight < 0.10 :
            'error is',math.sqrt(err2)/weight
            therange.append(hist.GetBinLowEdge(binj+1))
            weight = 0
            err2 = 0
        binj += 1
    therange.append(hist.GetBinLowEdge(hist.GetNbinsX()+1))

    print therange
    # import sys
    # sys.exit()
    return

#-------------------------------------------------------------------------
def CleanUpName(name) :
    tmp = name.replace('[','_').replace(']','').replace('_index','').replace('.','_')
    tmp = tmp.replace('[','_').replace(']','_').replace('(','_').replace(')','_')
    tmp = tmp.replace('/','_over_').replace('&&','and')
    tmp = tmp.replace('>','gt').replace('<','lt').replace('-','minus').replace(' ','_')
    tmp = tmp.lstrip('_').rstrip('_')
    return tmp

#-------------------------------------------------------------------------
def weightscaleHZY(tfile) :
    import re
    for i in tfile.GetListOfKeys() :
        name = i.GetName()
        if not re.match('cutflow_[0-9]*_w',name) :
            continue
        if re.match('cutflow_[0-9]*_w2',name) :
            continue
        j = i.ReadObj()
        #print j.GetName()
        xAOD = j.GetBinContent(1) # hopefully unskimmed MC sumw
        DxAOD = j.GetBinContent(2) # hopefully unskimmed MC sumw
        Ntuple_DxAOD = j.GetBinContent(3) # hopefully unskimmed MC sumw

    sumweight = 0
    if (DxAOD>0.001 and xAOD>0.001) :
        sumweight = xAOD/float(DxAOD) * Ntuple_DxAOD;
    else :
        sumweight = Ntuple_DxAOD;

    #print 'scaling by one over ',sumweight
    return 1.0/sumweight
