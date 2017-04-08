#!/usr/bin/env python

##
## This macro takes a file produced using pennSoftLepton using PassEvent functions.
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

    file_d ,tree_d ,key_d  = anaplot.GetChainFromFiles(options.data  ,treename=options.treename)

    dcuts = ' && '.join(options.cuts+options.blindcut)

    if not os.path.exists(options.outdir) :
        os.makedirs(options.outdir)

    from array import array
    categories = '.'.join(CouplingsHelpers.categories)
    print categories
    
    for k in key_d :
        ROOT.makePicoXaod_Categories(tree_d[k],k,dcuts,options.outdir,categories)

    print 'done.'
    return

if __name__ == '__main__':

    p = anaplot.TreePlottingOptParser()
    options,args = p.parse_args()

    if not options.variables :
        print 'Error! Please specify a variable!'
        sys.exit()

    main(options,args)

