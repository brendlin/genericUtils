#!/usr/bin/env python

##
## This macro takes a file produced using pennSoftLepton using PassEvent functions.
##

import ROOT,sys,os
import TAxisFunctions as taxisfunc
import PyAnalysisPlotting as anaplot
import PlotFunctions as plotfunc

#-------------------------------------------------------------------------
def main(options,args) :

    plotfunc.SetupStyle()

    files_b,trees_b,keys_b = anaplot.GetTreesFromFiles(options.bkgs  ,treename=options.treename)
    files_s,trees_s,keys_s = anaplot.GetTreesFromFiles(options.signal,treename=options.treename)
    files_d,trees_d,keys_d  = anaplot.GetTreesFromFiles(options.data  ,treename=options.treename)
    print files_d,trees_d,keys_d

    scales_b = anaplot.GetScales(files_b,trees_b,keys_b,options)
    scales_s = anaplot.GetScales(files_s,trees_s,keys_s,options)

    weight = options.weight
    if ''.join(options.cuts+options.truthcuts) :
        weight = (weight+'*(%s)'%(' && '.join(options.cuts+options.truthcuts).lstrip('& ').rstrip('& '))).lstrip('*')

    dweight = '' # weight value (and cuts) applied to data
    if ''.join(options.cuts+options.blindcut) :
        dweight = '('+' && '.join(options.cuts+options.blindcut).lstrip('& ').rstrip('& ')+')'

    cans = []

    # get the histograms from the files
    for v in options.variables.split(',') :
        bkg_hists = []
        sig_hists = []
        data_hist = None

        if options.data :
            data_hists = anaplot.GetVariableHistsFromTrees(trees_d,keys_d,v,dweight,options)
            data_hist = anaplot.MergeSamples(data_hists,options)[0]
            anaplot.PrepareDataHistos(data_hists,options)
        if options.bkgs :
            bkg_hists = anaplot.GetVariableHistsFromTrees(trees_b,keys_b,v,weight,options,scales=scales_b)
            bkg_hists = anaplot.MergeSamples(bkg_hists,options)
            anaplot.PrepareBkgHistosForStack(bkg_hists,options)
        if options.signal :
            sig_hists = anaplot.GetVariableHistsFromTrees(trees_s,keys_s,v,weight,options,scales=scales_s)
            sig_hists = anaplot.MergeSamples(sig_hists,options)
            anaplot.PrepareSignalHistos(sig_hists,options)

        cans.append(anaplot.DrawHistos(v,options,bkg_hists,sig_hists,data_hist))

    anaplot.UpdateCanvases(cans,options)

    if not options.batch :
        raw_input('Press enter to exit')

    anaplot.doSaving(options,cans)

    print 'done.'
    return

if __name__ == '__main__':

    p = anaplot.TreePlottingOptParser()
    options,args = p.parse_args()

    if not options.variables :
        print 'Error! Please specify a variable!'
        sys.exit()

    main(options,args)

