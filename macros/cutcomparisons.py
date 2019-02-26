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

def DrawHistosCutComparison(variable,options,sig_hists=[],data_hists=[],name='') :
    #
    # Clean up name
    #
    canname = anaplot.CleanUpName(variable)

    #
    # stack, before adding SUSY histograms
    #
    if not options.ratio :
        can = ROOT.TCanvas(canname,canname,500,500)
    else :
        can = plotfunc.RatioCanvas(canname,canname,500,500)

    if sig_hists :
        plotfunc.AddHistogram(can,sig_hists[0])
        for h in sig_hists[1:] :
            if options.ratio :
                plotfunc.AddRatio(can,h,sig_hists[0])
            else :
                plotfunc.AddHistogram(can,h)

    if data_hists :
        plotfunc.AddHistogram(can,data_hists[0])
        for h in data_hists[1:] :
            if options.ratio :
                plotfunc.AddRatio(can,h,data_hists[0])
            else :
                plotfunc.AddHistogram(can,h)

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
        plotfunc.MakeLegend(can,0.53,0.65,0.92,0.90,totalentries=5,ncolumns=1,skip=['remove me'])
    else :
        plotfunc.DrawText(can,text_lines,0.2,0.75,0.5,0.94,totalentries=4)
        plotfunc.MakeLegend(can,0.53,0.75,0.94,0.94,totalentries=5,ncolumns=1,skip=['remove me'])
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
        data_hists = []

        for cname in options.cutcomparisons.keys() :
            cutcomp = options.cutcomparisons[cname]
            inputname = '%s_%s'%(v,cname)

            weight = options.weight
            if ''.join(options.cuts+cutcomp+options.truthcuts) :
                weight = (weight+'*(%s)'%(' && '.join(options.cuts+cutcomp+options.truthcuts).lstrip('& ').rstrip('& '))).lstrip('*')

            dweight = '' # weight value (and cuts) applied to data
            if ''.join(options.cuts+cutcomp[1:]+options.blindcut) :
                dweight = '('+' && '.join(options.cuts+cutcomp+options.blindcut).lstrip('& ').rstrip('& ')+')'

            if options.data :
                data_hists_tmp = anaplot.GetVariableHistsFromTrees(trees_d,keys_d,v,dweight,options,files=files_d)
                data_hists_tmp = anaplot.MergeSamples(data_hists_tmp,options,requireFullyMerged=True)
                anaplot.PrepareDataHistos(data_hists_tmp,options)

                for d in data_hists_tmp :
                    d.SetTitle('%s, %s'%(d.GetTitle(),cname))
                    data_hists.append(d)

            if options.signal :
                sig_hists_tmp = anaplot.GetVariableHistsFromTrees(trees_s,keys_s,v,weight,options,scales=scales_s,files=files_s,inputname=inputname)
                sig_hists_tmp = anaplot.MergeSamples(sig_hists_tmp,options)
                anaplot.PrepareSignalHistos(sig_hists_tmp,options)

                for s in sig_hists_tmp :
                    s.SetTitle('%s, %s'%(s.GetTitle(),cname))
                    sig_hists.append(s)

        if options.normalize :
            for hist in data_hists + sig_hists :
                if not hist : continue
                hist.Scale(1/float(hist.Integral()))

        anaplot.PrepareSignalHistos(sig_hists+data_hists,None)

        ## Special canvas:
        cans.append(DrawHistosCutComparison(v,options,sig_hists=sig_hists,data_hists=data_hists))

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

