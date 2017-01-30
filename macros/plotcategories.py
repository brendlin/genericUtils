#!/usr/bin/env python

##
## This macro takes a file produced using pennSoftLepton using PassEvent functions.
##

import ROOT,sys,os
import TAxisFunctions as taxisfunc
import PyAnalysisPlotting as anaplot
import PlotFunctions as plotfunc

categories = [
    None,
    'M17_ggH_0J_Cen',        # 1
    'M17_ggH_0J_Fwd',        # 2
    'M17_ggH_1J_LOW',        # 3
    'M17_ggH_1J_MED',        # 4
    'M17_ggH_1J_HIGH',       # 5
    'M17_ggH_1J_BSM',        # 6
    'M17_ggH_2J_LOW',        # 7
    'M17_ggH_2J_MED',        # 8
    'M17_ggH_2J_HIGH',       # 9
    'M17_ggH_2J_BSM',        # 10
    'M17_VBF_HjjLOW_loose',  # 11
    'M17_VBF_HjjLOW_tight',  # 12
    'M17_VBF_HjjHIGH_loose', # 13
    'M17_VBF_HjjHIGH_tight', # 14
    'M17_VHhad_loose',       # 15
    'M17_VHhad_tight',       # 16
    'M17_qqH_BSM',           # 17
    'M17_VHMET_LOW',         # 18
    'M17_VHMET_HIGH',        # 19
    'M17_VHMET_BSM',         # 20
    'M17_VHlep_LOW',         # 21
    'M17_VHlep_HIGH',        # 22
    'M17_VHdilep_LOW',       # 23
    'M17_VHdilep_HIGH',      # 24
    'M17_ttH',               # 25
    'M17_ttH_Had_6j2b',      # 25
    'M17_ttH_Had_6j1b',      # 26
    'M17_ttH_Had_5j2b',      # 27
    'M17_ttH_Had_5j1b',      # 28
    'M17_ttH_Had_4j2b',      # 29
    'M17_ttH_Had_4j1b',      # 30
    'M17_ttH_Lep',           # 31
    'M17_ttH_Lep_0fwd',      # 32
    'M17_ttH_Lep_1fwd',      # 33
    ]

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

    v1 = 'HGamEventInfoAuxDyn.m_yy/1000'
    v2 = 'HGamEventInfoAuxDyn.catCoup_Moriond2017'
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
        bkg_hists = anaplot.MergeSamples(bkg_hists,options)
        anaplot.PrepareBkgHistosForStack(bkg_hists,options)
    if options.signal :
        sig_hists = anaplot.Get2dVariableHistsFromTrees(trees_s,keys_s,v1,v2,weight,options,scales=scales_s)
        sig_hists = anaplot.MergeSamples(sig_hists,options)
        sig_hists[-1].SetLineColor(2)
        sig_hists[-1].SetMarkerColor(2)

    # get the histograms from the files
    for c in range(len(categories)) :
        if not categories[c] : continue

        name = '_c%d_%s'%(c,categories[c])
        
        bkg_projs = []
        sig_projs = []
        data_proj = None
        
        if options.data :
            data_proj = data_hist.ProjectionX(name,c+1,c+1)
        if options.bkgs :
            for b in bkg_hists :
                bkg_projs.append(b.ProjectionX(name,c+1,c+1))
        if options.signal :
            for s in sig_hists :
                sig_projs.append(s.ProjectionX(name,c+1,c+1))

        cans.append(anaplot.DrawHistos(v1,options,bkg_projs,sig_projs,data_proj))
        cans[-1].SetName(anaplot.CleanUpName(name))

    anaplot.UpdateCanvases(options,cans)

    if not options.batch :
        raw_input('Press enter to exit')


    f = ROOT.TFile('couplings.root','RECREATE')
    for can in cans :
        can.Write()
    f.Close()
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

