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
        weight = (weight+'*(%s)'%(' && '.join(options.cuts+options.truthcuts))).lstrip('*')
        dweight = '('+' && '.join(options.cuts+options.blindcut)+')'

    cans = []

    v1 = 'HGamEventInfoAuxDyn.m_yy/1000'
    v2 = 'HGamEventInfoAuxDyn.catCoup_Moriond2017BDT'

    bkg_hists = []
    sig_hists = []
    data_hist = None

    if options.data :
        data_hist = anaplot.Get2dVariableHistsFromTrees(tree_d,key_d,v1,v2,dweight,options)[0]
        data_hist.SetLineWidth(2)
        data_hist.SetLineColor(1)
        data_hist.SetMarkerColor(1)
    if options.bkgs :
        bkg_hists = anaplot.Get2dVariableHistsFromTrees(trees_b,keys_b,v1,v2,weight,options,scales=scales_b)
        bkg_hists,keys_b = anaplot.MergeSamples(bkg_hists,options)
        anaplot.PrepareBkgHistosForStack(bkg_hists,options)
    if options.signal :
        sig_hists = anaplot.Get2dVariableHistsFromTrees(trees_s,keys_s,v1,v2,weight,options,scales=scales_s)
        sig_hists,keys_s = anaplot.MergeSamples(sig_hists,options)
        sig_hists[-1].SetLineColor(2)
        sig_hists[-1].SetMarkerColor(2)

    # get the histograms from the files
    for c in range(len(CouplingsHelpers.categories)) :
        #if not categories[c] : continue
        
        lo_bin = c+1
        hi_bin = c+1
        if c == 0 : # inclusive case.
            lo_bin = 0
            hi_bin = 10000 # just to be safe, 10k categories

        # MERGE VH LEP CATEGORIES (23 and 24 --> 23):
        if CouplingsHelpers.categories[c] == 'M17_VHlep_LOW' :
            hi_bin = hi_bin+1


        name = 'c%d_%s'%(c,CouplingsHelpers.categories[c])
        
        bkg_projs = []
        sig_projs = []
        data_proj = None
        
        if options.data :
            data_proj = data_hist.ProjectionX('%s_data'%(name),lo_bin,hi_bin)
            PyHelpers.PrintNumberOfEvents(data_proj)
        if options.bkgs :
            for i,b in enumerate(bkg_hists) :
                bkg_projs.append(b.ProjectionX('%s_%s'%(name,keys_b[i]),lo_bin,hi_bin))
                PyHelpers.PrintNumberOfEvents(bkg_projs[-1])
        if options.signal :
            for i,s in enumerate(sig_hists) :
                sig_projs.append(s.ProjectionX('%s_%s'%(name,keys_s[i]),lo_bin,hi_bin))
                PyHelpers.PrintNumberOfEvents(sig_projs[-1])
                
        cans.append(anaplot.DrawHistos(v1,options,bkg_projs,sig_projs,data_proj,name=name))
        cans[-1].SetName(anaplot.CleanUpName(name))

    anaplot.UpdateCanvases(options,cans)

    if not options.batch :
        raw_input('Press enter to exit')

    anaplot.doSaving(options,cans)

    # Do this afterwards, to make sure the outdir exists.
    f = ROOT.TFile('%s/couplings.root'%(options.outdir),'RECREATE')
    for can in cans :
        for i in can.GetListOfPrimitives() :
            if i.GetName()[-6:] == '_error' :
                continue
            if 'stack' in i.GetName() :
                if not issubclass(type(i),ROOT.THStack) :
                    continue
                for j in range(i.GetNhists()) :
                    print 'writing from stack:',i.GetHists()[j].GetName()
                    i.GetHists()[j].Write()
            if issubclass(type(i),ROOT.TH1) :
                print 'writing:',i.GetName()
                i.Write()

    f.Close()

    print 'done.'
    return

if __name__ == '__main__':

    p = anaplot.TreePlottingOptParser()
    options,args = p.parse_args()

    if not options.variables :
        print 'Error! Please specify a variable!'
        sys.exit()

    main(options,args)

