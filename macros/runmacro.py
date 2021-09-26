#!/usr/bin/env python

##
## This macro takes a file produced using pennSoftLepton using PassEvent functions.
##

import ROOT,sys,os
if sys.version_info.major == 3:
    sys.path.insert(0, "%s/.."%(os.path.dirname(__file__)))
    from python.PyAnalysisPlotting import CleanUpName,RunMacro,GetTreesFromFiles,TreePlottingOptParser
    from python.PlotFunctions import SetupStyle
else :
    from PyAnalysisPlotting import CleanUpName,RunMacro,GetTreesFromFiles,TreePlottingOptParser
    from PlotFunctions import SetupStyle

# ROOT.xAOD.Init()
# f = ROOT.TFile('DAOD_TRUTH1.sherpa224_tarball5_newjo_truth1.root')
# ROOT.xAOD.MakeTransientTree(f)
# ROOT.gROOT.LoadMacro("GammaStarGammaSM.h")
# print 'Macro loaded'

#-------------------------------------------------------------------------
def runMacroOnTrees(trees,keys,options=None,inputname='',files=None) :

    if not inputname :
        inputname = 'nominal'

    hists = []
    for k in keys :
        k_clean = CleanUpName(k,originalIsDirectoryName=True)
        name = CleanUpName('%s_%s'%(inputname,k_clean))

        RunMacro(options.macro,files[k],CleanUpName(k),verbose=False,xAODInit=options.xAODInit)

    return


#-------------------------------------------------------------------------
def main(options,args) :

    SetupStyle()

    files_b,trees_b,keys_b = GetTreesFromFiles(options.bkgs  ,treename=options.treename,xAODInit=options.xAODInit)
    files_s,trees_s,keys_s = GetTreesFromFiles(options.signal,treename=options.treename,xAODInit=options.xAODInit)
    files_d,trees_d,keys_d = GetTreesFromFiles(options.data  ,treename=options.treename,xAODInit=options.xAODInit)

    # Run the macro on all files

    if options.data :
        runMacroOnTrees(trees_d,keys_d,options,files=files_d)

    if options.bkgs :
        runMacroOnTrees(trees_b,keys_b,options,files=files_b)

    if options.signal :
        runMacroOnTrees(trees_s,keys_s,options,files=files_s)

    if options.xAODInit :
        ROOT.xAOD.ClearTransientTrees()

    print('done.')
    return

if __name__ == '__main__':

    p = TreePlottingOptParser()
    options,args = p.parse_args()

    if not options.variables :
        print('Error! Please specify a variable!')
        sys.exit()

    main(options,args)

