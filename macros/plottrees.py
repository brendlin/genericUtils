#!/usr/bin/env python

##
## This macro takes a file produced using pennSoftLepton using PassEvent functions.
##

import ROOT,sys,os
import TAxisFunctions as taxisfunc
import PyAnalysisPlotting as anaplot
import PlotFunctions as plotfunc

signal_colors = [ROOT.kRed,ROOT.kBlue,ROOT.kGreen,ROOT.kOrange,ROOT.kCyan]*5

#-------------------------------------------------------------------------
def main(options,args) :

    plotfunc.SetupStyle()

    files_b,trees_b,keys_b = anaplot.GetTreesFromFiles(options.bkgs  ,treename=options.treename)
    files_s,trees_s,keys_s = anaplot.GetTreesFromFiles(options.signal,treename=options.treename)
    file_d ,tree_d ,key_d  = anaplot.GetChainFromFiles(options.data  ,treename=options.treename)

    scales_b = anaplot.GetScales(files_b,trees_b,keys_b,options)
    scales_s = anaplot.GetScales(files_s,trees_s,keys_s,options)

    dweight = '' # weight value (and cuts) applied to data
    weight = options.weight
    if ''.join(options.cuts) :
        weight = (weight+'*(%s)'%(' && '.join(options.cuts))).lstrip('*')
        dweight = '('+' && '.join(options.cuts+options.blindcut)+')'

    cans = []

    # get the histograms from the files
    for v in options.variables.split(',') :
        bkg_hists = []
        sig_hists = []
        data_hist = None

        rebin = []

        if options.data :
            data_hist = anaplot.GetVariableHistsFromTrees(tree_d,key_d,v,dweight,options)[0]
            data_hist.SetLineWidth(2)
            data_hist.SetLineColor(1)
            data_hist.SetMarkerColor(1)
        if options.bkgs :
            bkg_hists = anaplot.GetVariableHistsFromTrees(trees_b,keys_b,v,weight,options,scales=scales_b)
            bkg_hists = anaplot.MergeSamples(bkg_hists,options)
            anaplot.PrepareBkgHistosForStack(bkg_hists,options)
        if options.signal :
            sig_hists = anaplot.GetVariableHistsFromTrees(trees_s,keys_s,v,weight,options,scales=scales_s)
            sig_hists[-1].SetLineColor(2)
            sig_hists[-1].SetMarkerColor(2)

        cans.append(anaplot.DrawHistos(v,options,bkg_hists,sig_hists,data_hist))

    anaplot.UpdateCanvases(options,cans)

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

