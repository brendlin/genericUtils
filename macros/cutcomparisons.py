#!/usr/bin/env python

##
## This macro offers a way to compare different cut selection.
## Right now it only works for --signal MC.
## To use it, make a config file and define inside a list called "cutcomparisons", e.g. to compare
## "CutSet1" (comprised of cut1a, cut1b, cut1c) and "CutSet2" (comprised of cut2a, cut2b, cut2c) do:
## cutcomparisons = [ ['CutSet1',['cut1a','cut1b','cut1c']], ['CutSet2',['cut2a','cut2b','cut2c']] ]
##

import ROOT,sys,os
import TAxisFunctions as taxisfunc
import PyAnalysisPlotting as anaplot
import PlotFunctions as plotfunc

#-------------------------------------------------------------------------
def main(options,args) :

    plotfunc.SetupStyle()

    files_b,trees_b,keys_b = anaplot.GetTreesFromFiles(options.bkgs  ,treename=options.treename,xAODInit=options.xAODInit)
    files_s,trees_s,keys_s = anaplot.GetTreesFromFiles(options.signal,treename=options.treename,xAODInit=options.xAODInit)
    files_d,trees_d,keys_d = anaplot.GetTreesFromFiles(options.data  ,treename=options.treename,xAODInit=options.xAODInit)

    scales_b = anaplot.GetScales(files_b,trees_b,keys_b,options)
    scales_s = anaplot.GetScales(files_s,trees_s,keys_s,options)

    cans = []

    # get the histograms from the files
    for v in options.variables :
        bkg_hists = []
        sig_hists = []
        data_hist = None

        for i,cutcomp in enumerate(options.cutcomparisons) :
            
            inputname = '%s_%s'%(v,cutcomp[0])

            weight = options.weight
            if ''.join(options.cuts+options.truthcuts) :
                weight = (weight+'*(%s)'%(' && '.join(options.cuts+cutcomp[1:]+options.truthcuts).lstrip('& ').rstrip('& '))).lstrip('*')

            dweight = '' # weight value (and cuts) applied to data
            if ''.join(options.cuts+options.blindcut) :
                dweight = '('+' && '.join(options.cuts+cutcomp[1:]+options.blindcut).lstrip('& ').rstrip('& ')+')'

            if options.signal :
                sig_hists_tmp = anaplot.GetVariableHistsFromTrees(trees_s,keys_s,v,weight,options,scales=scales_s,files=files_s,inputname=inputname)
                sig_hists_tmp = anaplot.MergeSamples(sig_hists_tmp,options)
                anaplot.PrepareSignalHistos(sig_hists_tmp,options)

            for s in sig_hists_tmp :
                s.SetTitle(cutcomp[0])
                s.SetMarkerColor(plotfunc.KurtColorPalate()[i])
                s.SetLineColor(plotfunc.KurtColorPalate()[i])
                sig_hists.append(s)

        print sig_hists
        cans.append(anaplot.DrawHistos(v,options,sig_hists=sig_hists))

    anaplot.UpdateCanvases(cans,options)

    if options.xAODInit :
        ROOT.xAOD.ClearTransientTrees()

    if not options.batch :
        raw_input('Press enter to exit')

    anaplot.doSaving(options,cans)

    print 'done.'
    return

if __name__ == '__main__':

    p = anaplot.TreePlottingOptParser()
    options,args = p.parse_args()

    if hasattr(options.usermodule,'cutcomparisons') :
        options.cutcomparisons = options.usermodule.cutcomparisons

    if not options.variables :
        print 'Error! Please specify a variable!'
        sys.exit()

    main(options,args)

