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

    for i in options.histformat.keys() :
        print '\'%s\':'%(i),options.histformat[i]

    #anaplot.LoadRootCore()
    
    files_b,trees_b,keys_b = anaplot.GetTreesFromFiles(options.bkgs  ,treename=options.treename)
    files_s,trees_s,keys_s = anaplot.GetTreesFromFiles(options.signal,treename=options.treename)
    file_d ,tree_d ,key_d  = anaplot.GetTreesFromFiles(options.data  ,treename=options.treename)

    #options.fb,lumi_scale_factor = helpers.GetTTreeLumiScaleFactor(files_b+files_s,options.fb)

    dweight = '' # weight value (and cuts) applied to data
    weight = options.weight
    if ''.join(options.cuts) :
        weight = weight+'*(%s)'%(' && '.join(options.cuts))
        dweight = '('+' && '.join(options.cuts)+')'

    cans = []

    # get the histograms from the files
    for v in options.variables.split(',') :
        n,low,high = options.histformat[v][:3]
        xlabel = options.histformat[v][3]

        bkg_hists = []
        sig_hists = []
        data_hist = None

        rebin = []
        if hasattr(options.usermodule,'rebin') and v in options.usermodule.rebin.keys() :
            rebin = options.usermodule.rebin[v]

        if options.bkgs :
            bkg_hists = anaplot.GetVariableHistsFromTrees(trees_b,keys_b,v,weight ,n,low,high,normalize=options.normalize,rebin=rebin,scale=1.)
            anaplot.PrepareBkgHistosForStack(bkg_hists)
        if options.signal :
            sig_hists = anaplot.GetVariableHistsFromTrees(trees_s,keys_s,v,weight ,n,low,high,normalize=options.normalize,rebin=rebin,scale=1.)
        if options.data :
            data_hist = anaplot.GetVariableHistsFromTrees(tree_d ,key_d ,v,dweight,n,low,high,normalize=options.normalize,rebin=rebin,scale=1.)[0]
            data_hist.SetLineWidth(2)
            data_hist.SetLineColor(1)
            data_hist.SetMarkerColor(1)

        cans.append(anaplot.DrawHistos(v,v,xlabel,bkg_hists,sig_hists,data_hist,dostack=options.stack,log=options.log,ratio=options.ratio,fb=options.fb))

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

