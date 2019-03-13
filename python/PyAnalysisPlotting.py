
#-------------------------------------------------------------------------
def PrepareBkgHistosForStack(bkg_hists,options) :
    from PlotFunctions import KurtColorPalate
    from PyHelpers import GetHWWColors
    import re

    colors = getattr(options,'colors',None)
    labels = getattr(options,'labels',None)

    if not colors :
        colors = GetHWWColors()
    used_colors = []

    if not labels :
        labels = dict()

    for i in bkg_hists :

        # Set colors according to your color dictionary, or the HWW color dictionary
        i.SetMarkerColor(colors.get(i.GetTitle(),1))
        i.SetFillColor(colors.get(i.GetTitle(),1))
        used_colors.append(i.GetFillColor())
        i.SetLineWidth(1)
        i.SetLineColor(1)

        # Set labels according to "labels" dict (allows for reg-exp)
        for j in labels.keys() :
            # Compare to regexp
            if not re.match(j.replace('%','.*'),i.GetTitle()) :
                continue
            i.SetTitle(labels[j])

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
def PrepareDataHistos(data_hists,options) :
    import re

    labels = getattr(options,'labels',None)
    if not labels :
        labels = dict()

    for i in data_hists :
        i.SetLineWidth(2)
        i.SetLineColor(1)
        i.SetMarkerColor(1)
        i.SetMarkerStyle(20)
        i.SetMarkerSize(1)

        # Set labels according to "labels" dict (allows for reg-exp)
        for j in labels.keys() :
            # Compare to regexp
            if not re.match(j.replace('%','.*'),i.GetTitle()) :
                continue
            i.SetTitle(labels[j])

    return

#-------------------------------------------------------------------------
def PrepareSignalHistos(sig_hists,options) :
    import re
    import ROOT

    labels = getattr(options,'labels',None)
    if not labels :
        labels = dict()

    signal_colors = [ROOT.kRed,ROOT.kBlue,ROOT.kSpring-8,ROOT.kMagenta+1,ROOT.kAzure+8
                     ,21,22,23,24,25,26,27,28,29,30
                     ,21,22,23,24,25,26,27,28,29,30]

    for i,sig_hist in enumerate(sig_hists) :
        sig_hist.SetLineWidth(2)
        sig_hist.SetLineColor(signal_colors[i])
        sig_hist.SetMarkerColor(signal_colors[i])
        sig_hist.SetMarkerStyle(20)
        sig_hist.SetMarkerSize(1)

        # Set labels according to "labels" dict (allows for reg-exp)
        for j in labels.keys() :
            # Compare to regexp
            if not re.match(j.replace('%','.*'),sig_hist.GetTitle()) :
                continue
            sig_hist.SetTitle(labels[j])

    return

#-------------------------------------------------------------------------
def DrawHistos(variable,options,bkg_hists=[],sig_hists=[],data_hist=None,name='') :
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
    canname = CleanUpName(variable)

    #
    # stack, before adding SUSY histograms
    #
    if not options.ratio :
        can = ROOT.TCanvas(canname,canname,500,500)
    else :
        can = plotfunc.RatioCanvas(canname,canname,500,500)

    if bkg_hists :

        # Make a histogram that includes the total of all bkgs:
        totb = bkg_hists[0].Clone()
        totb.SetNameTitle(('%s_%s_SM'%(canname,name)).replace('__','_'),'remove me')
        totb.SetLineColor(1)
        totb.SetLineWidth(1)
        totb.SetMarkerSize(0)
        totb.SetFillColor(0)
        for i in bkg_hists[1:] :
            totb.Add(i)

        # A copy of the total bkg histo, for plotting the error bar
        totberror = totb.Clone()
        totberror.SetName(totb.GetName().replace('_SM','_error'))
        totberror.SetTitle('SM (stat)')
        totberror.SetFillColor(12)
        totberror.SetFillStyle(3254)

    for index,i in enumerate(bkg_hists) :
        # if no data, but you specified you wanted a ratio, then do ratio of MC
        if (not options.stack) :
            i.SetLineWidth(2)
            i.SetLineColor(i.GetMarkerColor())
        if (index > 0) and (not data_hist) and (not options.stack) and (options.ratio) :
            plotfunc.AddRatio(can,i,bkg_hists[0])
        else :
            plotfunc.AddHistogram(can,i)

    if bkg_hists and options.stack :
        plotfunc.Stack(can)
        plotfunc.AddHistogram(can,totberror,drawopt='E2',keepname=True)
        plotfunc.AddHistogram(can,totb,drawopt='hist',keepname=True)

    for h in sig_hists :
        plotfunc.AddHistogram(can,h)

    if data_hist :
        if options.ratio :
            plotfunc.AddRatio(can,data_hist,totb)
        else :
            plotfunc.AddHistogram(can,data_hist)

    plotfunc.FormatCanvasAxes(can)
    text_lines = [plotfunc.GetSqrtsText(13)]
    if options.fb > 0 :
        text_lines += [plotfunc.GetLuminosityText(options.fb)]
    text_lines += [plotfunc.GetAtlasInternalText()]
    if hasattr(options,'plottext') and options.plottext :
        text_lines += options.plottext

    if options.log :
        if options.ratio :
            if taxisfunc.MinimumForLog(can.GetPrimitive('pad_top')) > 0 :
                can.GetPrimitive('pad_top').SetLogy()
        else :
            if taxisfunc.MinimumForLog(can) > 0 :
                can.SetLogy()

    if options.ratio :
        plotfunc.DrawText(can,text_lines,0.2,0.65,0.5,0.90,totalentries=4)
        plotfunc.MakeLegend(can,0.53,0.65,0.92,0.90,totalentries=5,ncolumns=2,skip=['remove me'])
        taxisfunc.SetYaxisRanges(plotfunc.GetBotPad(can),0,2)
    else :
        plotfunc.DrawText(can,text_lines,0.2,0.75,0.5,0.94,totalentries=4)
        plotfunc.MakeLegend(can,0.53,0.75,0.94,0.94,totalentries=5,ncolumns=2,skip=['remove me'])
    ylabel = 'entries (normalized)' if options.normalize else 'entries'
    plotfunc.SetAxisLabels(can,options.xlabel.get(variable),ylabel)
    plotfunc.AutoFixAxes(can)

    if not options.log :
        if can.GetPrimitive('pad_top') :
            plotfunc.AutoFixYaxis(can.GetPrimitive('pad_top'),minzero=True)
        else :
            plotfunc.AutoFixYaxis(can,minzero=True)

    return can

#-------------------------------------------------------------------------
def GetTreesFromFiles(filelist_csv,treename='physics',xAODInit=False) :
    import ROOT,os

    tmperror = ROOT.gErrorIgnoreLevel        
    ROOT.gErrorIgnoreLevel = ROOT.kFatal

    files = dict()
    trees = dict()
    keys = []
    for f in filelist_csv.split(',') :
        if not f : continue
        name = f.replace('.root','')
        #
        # folder of files
        #
        if not os.path.isfile(f) :
            files[name] = []
            trees[name]= ROOT.TChain(treename)
            for ff in os.listdir(f) :
                tmpfilename = '%s/%s'%(f,ff)
                if not os.path.isfile(tmpfilename) :
                    continue
                files[name].append(ROOT.TFile(tmpfilename))
                if files[name][-1].IsZombie() :
                    print 'exiting'
                    import sys
                    sys.exit()
                #print 'adding',tmpfilename
                trees[name].Add(tmpfilename)
                
            keys.append(name)
            continue

        #
        # regular files
        # 
        files[name] = ROOT.TFile(f)
        if files[name].IsZombie() :
            print 'exiting'
            import sys
            sys.exit()
        keys.append(name)

        # Regular files: Get tree
        if xAODInit :
            trees[name] = ROOT.xAOD.MakeTransientTree( files[name] )
        else :
            trees[name] = files[name].Get(treename)


        if not trees[name] :
            print 'Error! Tree \"%s\" does not exist! Exiting.'%(treename)
            import sys; sys.exit()

    ROOT.gErrorIgnoreLevel = tmperror
    return files,trees,keys

#-------------------------------------------------------------------------
def GetChainFromFiles(filelist_csv,treename='physics',chainname='data') :

    # Please do not use this! Use GetTreesFromFiles and MergeSamples instead!

    import ROOT,os

    files = dict()
    trees = dict()
    keys = [chainname]

    if not filelist_csv :
        return files,trees,keys

    trees[chainname] = ROOT.TChain(treename)

    # Need this to read individual branches that are part of a class.
    # Note that now things like "blah.pt[0]" do not work.
    trees[chainname].SetMakeClass(1)

    for f in filelist_csv.split(',') :
        if not f : continue
        name = f.replace('.root','').replace('/','_').replace('-','_').replace('.','_')

        files[name] = ROOT.TFile(f)

        if files[name].IsZombie() :
            print 'exiting'
            import sys
            sys.exit()

        if not files[name].Get(treename) :
            print 'Error: No Tree named %s. Exiting.'%(treename)
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
def RunMacro(macro,thefile,histnamekey) :
    import ROOT

    macro_name = macro.replace('.h','').replace('.cxx','').replace('.cpp','')
    macro_name = macro_name.replace('.C','')

    if getattr(ROOT,macro_name,None) :
        print 'Macro %s already loaded.'%(macro)
    else :
        print 'Loading macro %s'%(macro)
        ROOT.gROOT.LoadMacro(macro)

        if not getattr(ROOT,macro_name,None) :
            print 'ERROR Macro named %s not found in file %s'%(macro_name,macro)
            import sys; sys.exit()

    # Macro should take a TTree and a key name
    print 'Running macro %s...'%(macro_name)
    getattr(ROOT,macro_name)(thefile,histnamekey)

    return

#-------------------------------------------------------------------------
def GetVariableHistsFromTrees(trees,keys,variable,weight,options=None,scales=0,inputname='',files=None) :
    import ROOT
    from array import array
    import PlotFunctions as plotfunc
    import TAxisFunctions as taxisfunc
    import math
    import PyHelpers

    # Parse options
    n,low,high = -1,-1,-1
    if hasattr(options,'limits') :
        n,low,high = options.limits.get(variable,[-1,-1,-1])
    rebin = options.rebin.get(variable,[]) if hasattr(options,'rebin') else []
    showflows = hasattr(options,'showflows') and options.showflows

    if not inputname :
        inputname = variable

    hists = []
    for k in keys :
        name = CleanUpName('%s_%s'%(inputname,k))

        if issubclass(type(ROOT.gDirectory.Get(name)),ROOT.TH1) :
            print 'Using existing histogram, %s'%(name)
            # will load the histogram later...

        elif options.macro :

            RunMacro(options.macro,files[k],CleanUpName(k))

            # if Draw did not work, then exit.
            if not issubclass(type(ROOT.gDirectory.Get(name)),ROOT.TH1) :
                print 'ERROR Macro failed trying to create %s Exiting.'%(name)
                import sys; sys.exit()

        else :

            if rebin and type(rebin) == type([]) :
                name = name+'_unrebinned'

            bins = '(%s,%s,%s)'%(n,low,high)
            if (n <= 0) :
                bins = ''
            arg1,arg2,arg3 = '%s>>%s%s'%(variable,name,bins),weight,'egoff'

            # Reset the default binning to 100, if "n" is not specified.
            ROOT.gEnv.SetValue('Hist.Binning.1D.x','100')

            print 'tree.Draw(\'%s\',\'%s\',\'%s\')'%(arg1,arg2,arg3)
            tmp = ROOT.gErrorIgnoreLevel
            ROOT.gErrorIgnoreLevel = ROOT.kFatal
            trees[k].Draw(arg1,arg2,arg3)
            ROOT.gErrorIgnoreLevel = tmp

            # if Draw did not work, then exit.
            if not issubclass(type(ROOT.gDirectory.Get(name)),ROOT.TH1) :
                print 'ERROR TTree::Draw failed trying to draw %s Exiting.'%(name)
                import sys; sys.exit()

            if rebin and type(rebin) == type([]) :
                tmp = ROOT.gDirectory.Get(name)
                name = name.replace('_unrebinned','')
                tmp.Rebin(len(rebin)-1,name,array('d',rebin))

        hists.append(ROOT.gDirectory.Get(name))
        hists[-1].SetDirectory(0)

        if rebin and type(rebin) == type(1) :
            hists[-1].Rebin(rebin)

        if (n <= 0) :
            print 'Changing limits to match those from the first plot.'
            n    = hists[-1].GetNbinsX()
            low  = hists[-1].GetBinLowEdge(1)
            high = hists[-1].GetBinLowEdge(n+1)
            if hasattr(options,'limits') :
                options.limits[variable] = [n,low,high]

        if showflows :
            taxisfunc.PutOverflowIntoLastBin(hists[-1])
            taxisfunc.PutUnderflowIntoFirstBin(hists[-1])

        #RebinSmoothlyFallingFunction(hists[-1])

        hists[-1].SetTitle(k)
        if scales and (scales[k] != 1) :
            hists[-1].Scale(scales[k])

        # print the yield and error after cuts (includes overflow)
        PyHelpers.PrintNumberOfEvents(hists[-1])

        if rebin :
            plotfunc.ConvertToDifferential(hists[-1])

    return hists

#-------------------------------------------------------------------------
def Get2dVariableHistsFromTrees(trees,keys,variable1,variable2,weight,options,scales=0,inputname='',files=None) :
    import ROOT
    from array import array
    import PlotFunctions as plotfunc
    import math
    import PyHelpers

    if not options.macro :
        if not options.limits.get(variable1,None) or not options.limits.get(variable2,None) :
            print 'Error - you need to specify limits for both %s and %s.'%(variable1,variable2)
            print '(Note you probably have to add these variables to the list of variables as well.)'
            import sys; sys.exit()

    n1,low1,high1 = options.limits.get(variable1)
    n2,low2,high2 = options.limits.get(variable2)

    if not inputname :
        inputname = '%s_%s'%(variable1,variable2)
        
    hists = []
    for k in keys :
        name = CleanUpName('%s_%s'%(inputname,k))

        if issubclass(type(ROOT.gDirectory.Get(name)),ROOT.TH1) :
            print 'Using existing histogram, %s'%(name)
            # will load the histogram later...

        elif options.macro :

            RunMacro(options.macro,files[k],CleanUpName(k))

            # if Draw did not work, then exit.
            if not issubclass(type(ROOT.gDirectory.Get(name)),ROOT.TH1) :
                print 'ERROR Macro failed trying to create %s Exiting.'%(name)
                import sys; sys.exit()

        else :

            arg1 = '%s:%s>>%s(%s,%s,%s,%s,%s,%s)'%(variable2,variable1,name,
                                                   n1,low1,high1,n2,low2,high2)
            arg2 = weight
            arg3 = 'egoff'
            print 'tree.Draw(\'%s\',\'%s\',\'%s\')'%(arg1,arg2,arg3)
            tmp = ROOT.gErrorIgnoreLevel
            ROOT.gErrorIgnoreLevel = ROOT.kFatal
            trees[k].Draw(arg1,arg2,arg3)
            ROOT.gErrorIgnoreLevel = tmp

            # if Draw did not work, then exit.
            if not issubclass(type(ROOT.gDirectory.Get(name)),ROOT.TH1) :
                print 'ERROR TTree::Draw failed trying to draw %s Exiting.'%(name)
                import sys
                sys.exit()

        hists.append(ROOT.gDirectory.Get(name))
        hists[-1].SetDirectory(0)

        hists[-1].SetTitle(k)
        if scales and (scales[k] != 1) :
            hists[-1].Scale(scales[k])

        # print the yield and error after cuts (includes overflow)
        PyHelpers.PrintNumberOfEvents(hists[-1])

        if options.normalize :
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
        self.p.add_option('--showflows',action='store_true',default=False,dest='showflows',help='show overflows/underflows as first and last bin')
        self.p.add_option('--plottext',type='string',default='',dest='plottext',help='Additional plot text')

        # other options
        self.p.add_option('--batch',action='store_true',default=False,dest='batch',help='run in batch mode')
        self.p.add_option('--save',action='store_true',default=False,dest='save',help='save cans to pdf')
        self.p.add_option('--outdir',type='string',default='',dest='outdir',help='output directory')
        self.p.add_option('-l','--log',action='store_true',default=False,dest='log',help='log')
        self.p.add_option('--xAODInit',action='store_true',default=False,dest='xAODInit',help='run xAOD::Init()')
        self.p.add_option('--macro',type='string',default='',dest='macro',help='Load and run a macro')
        
    def parse_args(self) :
        import sys,os
        import ROOT
        import importlib
        #LoadRootCore()

        self.options,self.args = self.p.parse_args()

        ROOT.gROOT.SetBatch(self.options.batch)

        self.options.stack = not self.options.nostack

        if self.options.save and not self.options.outdir :
            self.options.outdir = os.getcwd()
        
        if self.options.signal and not '.root' in self.options.signal :
            dir = self.options.signal
            self.options.signal = ','.join('%s/%s'%(dir,a) for a in os.listdir(self.options.signal))

        if len(self.options.limits.split(',')) != 3 :
            print 'Error! Please specify --limits using 3 numbers in the format nbins,lowedge,highedge'
            sys.exit()

        self.options.variables = self.options.variables.split(',')
        self.options.plottext = self.options.plottext.split(',')


        # some defaults are not set in the option parser
        defaults = {'blindcut':[],
                    'truthcuts':[],
                    'mergesamples':dict(),
                    'colors':dict(),
                    'labels':dict(),
                    'histformat':dict(),
                    'usermodule':None,
                    'afterburner':None,
                    }
        for k in defaults.keys() :
            setattr(self.options,k,defaults[k])




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

        if self.options.xAODInit :
            if not os.getenv('AtlasArea') :
                print 'Error! Specified --xAODInit but did not set up ATLAS! Exiting.'
                import sys; sys.exit()
            ROOT.xAOD.Init()

        # to get your current directory viewable by the code:
        sys.path.append(os.getcwd())
        # Read in options from config file:
        if self.options.config :
            usermodule = importlib.import_module(self.options.config.replace('.py',''))
            self.options.usermodule = usermodule

            for x in ['histformat','weight','weightscale','blindcut','truthcuts'
                      ,'treename','fb','colors','labels','mergesamples','bkgs','data','signal','plottext'
                      ,'afterburner'] :
                if hasattr(usermodule,x) :
                    setattr(self.options,x,getattr(usermodule,x))

            if hasattr(usermodule,'cuts') :
                self.options.cuts = usermodule.cuts
                if len(self.options.cuts) > 1 :
                    for i,c in enumerate(self.options.cuts) :
                        self.options.cuts[i] = '('+c+')'

            if hasattr(usermodule,'variables') :
                self.options.variables = usermodule.variables

        def ExpandWildcard(csv_list) :
            import re
            tmp = csv_list.split(',')
            tmp_new = []
            for i in range(len(tmp)) :
                if not tmp[i] :
                    continue
                if '%' in tmp[i] :
                    for j in sorted(os.listdir('.')) :
                        if re.match(tmp[i].replace('%','.*'),j) :
                            tmp_new.append(j)
                else :
                    tmp_new.append(tmp[i])
            return ','.join(tmp_new)

        def AddDotRoot(csv_list) :
            tmp = csv_list.split(',')
            for i in range(len(tmp)) :
                if not tmp[i] :
                    continue
                if '.root' not in tmp[i] :
                    tmp[i] = tmp[i]+'.root'
            return ','.join(tmp)
        
        # add .root to each background name.
        self.options.bkgs = ExpandWildcard(self.options.bkgs)
        self.options.bkgs = AddDotRoot(self.options.bkgs)
        self.options.signal = ExpandWildcard(self.options.signal)
        self.options.signal = AddDotRoot(self.options.signal)

        # add up multiple data files
        if self.options.data == 'all' :
            dirlist = os.listdir('.')
            datalist = []
            for i in dirlist :
                if (not '.root' in i) or (not 'data' in i) :
                    continue
                datalist.append(i)
            self.options.data = ','.join(datalist)

        self.options.data = ExpandWildcard(self.options.data)

        self.options.mergesamples['data'] = []
        for a in self.options.data.split(',') :
            if not a : continue
            self.options.mergesamples['data'].append(a.replace('.root',''))
        self.options.data = AddDotRoot(self.options.data)

        if self.p.has_option('--bkgs') :
            if (not self.options.bkgs) and (not self.options.signal) and (not self.options.data) :
                print 'No --bkgs, --signal, or --data specified. Exiting.'
                sys.exit()

        self.options.xlabel = dict()
        self.options.rebin = dict()

        # turn limits into variable-specific values
        tmp_limits = self.options.limits
        self.options.limits = dict()

        # Prepare stuff related to the variables.
        for v in self.options.variables :
            if v == '' : continue
            if v in self.options.histformat.keys() :
                if len(self.options.histformat[v]) < 4 :
                    self.options.histformat[v].append(v)
            else :
                n,low,high = tmp_limits.split(',')
                self.options.histformat[v] = [int(n),float(low),float(high),v]
            
            # set limits and xlabel:
            self.options.limits[v] = self.options.histformat[v][:3]
            self.options.xlabel[v] = self.options.histformat[v][3]

            if hasattr(self.options.usermodule,'rebin') and v in self.options.usermodule.rebin.keys() :
                self.options.rebin[v] = self.options.usermodule.rebin[v]
            

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
    if hasattr(options,'outdir') and options.outdir :
        directory = options.outdir
        if not os.path.exists(directory) :
            os.makedirs(directory)
        options.save = True
    if not options.save :
        return 
    for can in cans :
        while True :
            log = '_log' if (can.GetLogy() or can.GetLogz()) else ''
            name = directory + '/' + CleanUpName(can.GetName())+log+'.pdf'
            try :
                open(name, 'a').close()
                can.Print(name)
                can.Print(name.replace('.pdf','.C'))
                can.Print(name.replace('.pdf','.eps'))
                #can.Print(name.replace('.pdf','.root'))
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
def UpdateCanvases(cans,options=None) :
    if (not options) or (not options.batch) :
        for can in cans :
            can.Update()
            if can.GetPrimitive('pad_bot') :
                can.GetPrimitive('pad_bot').Update()
            if can.GetPrimitive('pad_top') :
                can.GetPrimitive('pad_top').Update()                
    return

#-------------------------------------------------------------------------
def MergeSamples(hists,options,requireFullyMerged=False) :
    #
    # Yeah so this adds the samples together that you specify, in a resonable
    # order close to the one you specify in the command line "bkgs"
    # If you require that the samples are fully merged, this means that N
    # inputs is merged into one output (a check we require for data).
    #
    import math
    import ROOT
    import PyHelpers
    import re

    if not options.mergesamples :
        return hists

    hists_new = []
    keys_new = []
    hists_index = dict()
    for i in hists :
        added = False
        for j in options.mergesamples.keys() :

            # Compare to regexp
            if type(options.mergesamples[j]) == type('') :
                if not re.match(options.mergesamples[j].replace('%','.*'),i.GetTitle()) :
                    continue

            # Compare to list of samples
            if type(options.mergesamples[j]) == type([]) :
                match = False
                for mergesample in options.mergesamples[j] :
                    if re.match(mergesample.replace('%','.*'),i.GetTitle()) :
                        match = True
                if not match :
                    continue

            if j in hists_index.keys() :
                #print 'adding to existing histo'
                hists_new[hists_index[j]].Add(i)
                added = True
            else :
                #print 'starting a new histo'
                hists_index[j] = len(hists_new)
                hists_new.append(i)
                keys_new.append(j)
                hists_new[-1].SetTitle(j)
                hists_new[-1].SetName(CleanUpName(j))
                added = True
        if not added :
            hists_new.append(i)
            keys_new.append(i.GetTitle())

    for i in hists_index.keys() :
        PyHelpers.PrintNumberOfEvents(hists_new[hists_index[i]])

    if requireFullyMerged and len(hists_new) > 1 :
        print 'Error! Failed to merge histograms into one histogram! (Usually required for data.) Check your sample merging.'
        import sys; sys.exit()

    return hists_new

#-------------------------------------------------------------------------
def RebinSmoothlyFallingFunction(hist,error=0.10) :
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
        if weight > 0 and math.sqrt(err2)/weight < error :
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
    tmp = tmp.replace('!','not').replace('*','times').replace('+','plus')
    tmp = tmp.replace('::','_').replace(':','_')
    tmp = tmp.replace(',','_')
    tmp = tmp.replace('#','')
    tmp = tmp.replace('@','')
    tmp = tmp.replace('____','_').replace('___','_').replace('__','_')
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
