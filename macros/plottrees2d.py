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

    style = plotfunc.SetupStyle()
    style.SetPadRightMargin(0.16)

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

    for v in options.variables :
        if v not in options.histformat.keys() or len(options.histformat[v]) < 4 :
            print 'Warning: need to set the label of %s using the histformat option.'%(v)

    # get the histograms from the files
    for vi,v1 in enumerate(options.variables) :

        labelv1 = v1
        if v1 in options.histformat.keys() and len(options.histformat[v1]) >= 4:
            labelv1 = options.histformat[v1][3]

        for vj,v2 in enumerate(options.variables) :

            if v2 == v1 : continue
            if vj < vi : continue

            labelv2 = v2
            if v2 in options.histformat.keys() and len(options.histformat[v2]) >= 4:
                labelv2 = options.histformat[v2][3]

            bkg_hists = []
            sig_hists = []
            data_hist = None

            if options.data :
                data_hists = anaplot.Get2dVariableHistsFromTrees(trees_d,keys_d,v1,v2,dweight,options,files=files_d)
                data_hist = anaplot.MergeSamples(data_hists,options,requireFullyMerged=True)[0]

                canname = anaplot.CleanUpName('%s_%s_%s'%(v1,v2,'data'))
                cans.append(ROOT.TCanvas(canname,canname,600,500))
                data_hist.SetMinimum(-0.00001)
                plotfunc.AddHistogram(cans[-1],data_hist,drawopt='colz')
                plotfunc.SetAxisLabels(cans[-1],labelv1,labelv2)

            if options.bkgs :
                bkg_hists = anaplot.Get2dVariableHistsFromTrees(trees_b,keys_b,v1,v2,weight,options,scales=scales_b,files=files_b)
                bkg_hists = anaplot.MergeSamples(bkg_hists,options)
                for i,h in enumerate(bkg_hists) :
                    canname = anaplot.CleanUpName('%s_%s_%s'%(v1,v2,keys_b[i]))
                    cans.append(ROOT.TCanvas(canname,canname,600,500))
                    h.SetMinimum(-0.00001)
                    plotfunc.AddHistogram(cans[-1],h,drawopt='colz')
                    plotfunc.SetAxisLabels(cans[-1],labelv1,labelv2)

            if options.signal :
                sig_hists = anaplot.Get2dVariableHistsFromTrees(trees_s,keys_s,v1,v2,weight,options,scales=scales_s,files=files_s)
                sig_hists = anaplot.MergeSamples(sig_hists,options)
                for i,h in enumerate(sig_hists) :
                    canname = anaplot.CleanUpName('%s_%s_%s'%(v1,v2,keys_s[i]))
                    cans.append(ROOT.TCanvas(canname,canname,600,500))
                    h.SetMinimum(-0.00001)
                    plotfunc.AddHistogram(cans[-1],h,drawopt='colz')
                    plotfunc.SetAxisLabels(cans[-1],labelv1,labelv2)

    if options.afterburner :
        for can in cans :
            options.afterburner(can)

    anaplot.UpdateCanvases(cans,options)

    if options.xAODInit :
        ROOT.xAOD.ClearTransientTrees()

    if not options.batch :
        import code
        code.interact(banner='Pausing... Press Contol-D to exit.',local=locals())

    anaplot.doSaving(options,cans)

    print 'done.'
    return

if __name__ == '__main__':

    p = anaplot.TreePlottingOptParser()
    options,args = p.parse_args()

#     if int(bool(options.signal)) + int(bool(options.bkgs)) + int(bool(options.data)) > 1 :
#         print 'Error! Cannot deal with more than one input at this moment. Use --signal please.'
#         sys.exit()

    if not options.variables :
        print 'Error! Please specify a variable!'
        sys.exit()

    main(options,args)

