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

isLoaded = ROOT.gROOT.LoadMacro('Extras.h')
if (isLoaded < 0) :
    print 'Error! Macro compilation Extras.h failed. See error messages.'
    sys.exit()
else :
    print 'Loaded Macro Extras.h'

#-------------------------------------------------------------------------
def main(options,args) :

    plotfunc.SetupStyle()

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
        name = '%s_pico'%(k)
        print 'Making picoXaod for %s'%(k)
        ROOT.makePicoXaod(trees_d[k],k,dcuts,options.variables,options.outdir,name)

    for k in keys_b :
        name = '%s_pico'%(k)
        print 'Making picoXaod for %s'%(k)
        ROOT.makePicoXaod(trees_b[k],k,simcuts,options.variables,options.outdir,name)

    print 'done.'
    return

if __name__ == '__main__':

    p = anaplot.TreePlottingOptParser()
    p.p
    options,args = p.parse_args()

    if not options.variables :
        print 'Error! Please specify a variable!'
        sys.exit()

    if not options.outdir :
        print 'Error! Please specify an output directory (--outdir)!'
        sys.exit()

    main(options,args)

