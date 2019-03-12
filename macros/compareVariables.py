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

    files_b,trees_b,keys_b = anaplot.GetTreesFromFiles(options.bkgs  ,treename=options.treename,xAODInit=options.xAODInit)
    files_s,trees_s,keys_s = anaplot.GetTreesFromFiles(options.signal,treename=options.treename,xAODInit=options.xAODInit)
    files_d,trees_d,keys_d = anaplot.GetTreesFromFiles(options.data  ,treename=options.treename,xAODInit=options.xAODInit)

    scales_b = anaplot.GetScales(files_b,trees_b,keys_b,options)
    scales_s = anaplot.GetScales(files_s,trees_s,keys_s,options)

    weight = options.weight
    if ''.join(options.cuts+options.truthcuts) :
        weight = (weight+'*(%s)'%(' && '.join(options.cuts+options.truthcuts).lstrip('& ').rstrip('& '))).lstrip('*')

    dweight = '' # weight value (and cuts) applied to data
    if ''.join(options.cuts+options.blindcut) :
        dweight = '('+' && '.join(options.cuts+options.blindcut).lstrip('& ').rstrip('& ')+')'

    cans = []

    bkg_hists = []
    sig_hists = []
    data_hists = []

    # get the histograms from the files
    for v in options.variables :
        if options.data :
            tmp_hists = anaplot.GetVariableHistsFromTrees(trees_d,keys_d,v,dweight,options,files=files_d)
            hist = anaplot.MergeSamples(tmp_hists,options,requireFullyMerged=True)[0]
            anaplot.PrepareSignalHistos([hist],options)
            hist.SetTitle(('%s, %s'%(hist.GetTitle(),options.xlabel.get(v))).lstrip(','))
            data_hists.append(hist)

        if options.bkgs :
            tmp_hists = anaplot.GetVariableHistsFromTrees(trees_b,keys_b,v,weight,options,scales=scales_b,files=files_b)
            tmp_hists += anaplot.MergeSamples(tmp_hists,options)
            for hist in tmp_hists :
                anaplot.PrepareSignalHistos([hist],options)
                hist.SetTitle(('%s, %s'%(hist.GetTitle(),options.xlabel.get(v))).lstrip(','))
            bkg_hists += tmp_hists

        if options.signal :
            tmp_hists = anaplot.GetVariableHistsFromTrees(trees_s,keys_s,v,weight,options,scales=scales_s,files=files_s)
            tmp_hists = anaplot.MergeSamples(tmp_hists,options)
            for hist in tmp_hists :
                anaplot.PrepareSignalHistos([hist],options)
                hist.SetTitle(('%s, %s'%(hist.GetTitle(),options.xlabel.get(v))).lstrip(','))
            sig_hists += tmp_hists

    if options.normalize :
        for hist in data_hists + bkg_hists + sig_hists :
            if not hist : continue
            hist.Scale(1/float(hist.Integral()))

    anaplot.PrepareSignalHistos(sig_hists+data_hists+bkg_hists,None)
    cans.append(anaplot.DrawHistos(v,options,sig_hists=sig_hists+bkg_hists+data_hists))

    if options.afterburner :
        for can in cans :
            options.afterburner(can)

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

    if not options.variables :
        print 'Error! Please specify a variable!'
        sys.exit()

    main(options,args)

