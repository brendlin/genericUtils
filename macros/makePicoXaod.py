#!/usr/bin/env python

##
## This macro makes a PicoXaod with arbitrary branch names (separated by ",")
##

import ROOT,sys,os
import TAxisFunctions as taxisfunc
import PyAnalysisPlotting as anaplot
import PlotFunctions as plotfunc
import CouplingsHelpers
import PyHelpers

# Get base path (genericUtils)
the_path = ('/').join(os.path.abspath(__file__).split('/')[:-2])

# Add to macro path
ROOT.gROOT.SetMacroPath('%s:%s/share'%(ROOT.gROOT.GetMacroPath(),the_path))

#-------------------------------------------------------------------------
def main(options,args) :

    plotfunc.SetupStyle()

    # The nominal case, where you use an algorithm inside the predefined file
    macroFileName = 'PicoXaodSkimAlgos.h'
    algName = options.alg

    # If a colon is used, it is to specify a different file path
    if ':' in options.alg :
        macroFileName = options.alg.split(':')[0]
        algName = options.alg.split(':')[-1]

    isLoaded = ROOT.gROOT.LoadMacro(macroFileName)
    if (isLoaded < 0) :
        print 'Error! Macro compilation of file %s failed. See error msgs.'%(macroFileName)
        sys.exit()
    else :
        print 'Loaded macro file %s'%(macroFileName)

    print 'Skimming using the \"%s\" algorithm...'%(algName)

    # Here "b" stands for simulation
    files_b,trees_b,keys_b = anaplot.GetTreesFromFiles(options.bkgs  ,treename=options.treename)
    files_d,trees_d,keys_d = anaplot.GetTreesFromFiles(options.data  ,treename=options.treename)

    simcuts = ''
    if ''.join(options.cuts+options.truthcuts) :
        simcuts = '('+' && '.join(options.cuts+options.truthcuts)+')'

    dcuts = '' # cuts applied to data
    if ''.join(options.cuts+options.blindcut) :
        dcuts = '('+' && '.join(options.cuts+options.blindcut)+')'

    if not os.path.exists(options.outdir) :
        os.makedirs(options.outdir)

    for k in keys_d :
        outfilename = os.path.basename(files_d[k].GetName()).replace('.root','')
        outfilename = '%s_pico'%(outfilename)
        outfilename = anaplot.CleanUpName(outfilename,originalIsDirectoryName=True,forFileName=True)
        histname = anaplot.CleanUpName(k,originalIsDirectoryName=True)
        print 'Making picoXaod for %s'%(k)
        getattr(ROOT,algName)(files_d[k],trees_d[k],histname,dcuts,','.join(options.variables),options.outdir,outfilename)

    for k in keys_b :
        outfilename = os.path.basename(files_b[k].GetName()).replace('.root','')
        outfilename = '%s_pico'%(outfilename)
        outfilename = anaplot.CleanUpName(outfilename,originalIsDirectoryName=True,forFileName=True)
        histname = anaplot.CleanUpName(k,originalIsDirectoryName=True)
        print 'Making picoXaod for %s'%(k)
        getattr(ROOT,algName)(files_b[k],trees_b[k],histname,simcuts,','.join(options.variables),options.outdir,outfilename)

    print 'done.'
    return

if __name__ == '__main__':

    p = anaplot.TreePlottingOptParser()
    p.p.add_option('--alg',type='string',default='makePicoXaod',dest='alg',help='Algorithm to use (default is makePicoXaod. Others: makePicoXaod_Categories, makePicoXaod_Zpileup). Can also specify /path/to/file.h:algo')
    options,args = p.parse_args()

    if not options.variables :
        print 'Error! Please specify a variable!'
        sys.exit()

    if not options.outdir :
        print 'Error! Please specify an output directory (--outdir)!'
        sys.exit()

    main(options,args)

