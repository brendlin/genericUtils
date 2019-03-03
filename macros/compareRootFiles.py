#!/usr/bin/env python

import ROOT
import PlotFunctions as plotfunc
import TAxisFunctions as taxisfunc
import PyAnalysisPlotting as anaplot
import os,sys
from inspect import currentframe

ROOT.gROOT.SetBatch(True)
plotfunc.SetupStyle()

#-----------------------------------------------
def IterateAllTheThings(i,j,outdir,options):

    #if type(i) in unsupported_types : return

    # TH1, TGraph Types
    if issubclass(type(i),ROOT.TH1) or issubclass(type(i),ROOT.TGraph) :
        c = plotfunc.RatioCanvas(i.GetName(),i.GetName(),600,500)
        i.SetTitle(options.label1)
        j.SetTitle(options.label2)
        plotfunc.AddHistogram(c,i)
        plotfunc.AddRatio(c,j,i)
        plotfunc.SetAxisLabels(c,j.GetXaxis().GetTitle(),j.GetYaxis().GetTitle())
        plotfunc.FormatCanvasAxes(c)
        plotfunc.SetColors(c)
        plotfunc.MakeLegend(c)
        taxisfunc.AutoFixAxes(c)
        if not os.path.exists(outdir) :
            os.makedirs(outdir)
        c.Print('%s/%s.pdf'%(outdir,c.GetName()))
        c.Print('%s/%s.C'%(outdir,c.GetName()))
        
    # TCanvas
    elif issubclass(type(i),ROOT.TCanvas) :
        newdir = '%s/%s'%(outdir,i.GetName())
        print 'Making new directory %s (line %d)'%(newdir,currentframe().f_lineno)
        IterateAllTheThings(i.GetListOfPrimitives(),j.GetListOfPrimitives(),newdir,options)
        
    # TDirectoryFile
    elif issubclass(type(i),ROOT.TDirectoryFile) :
        newdir = '%s/%s'%(outdir,i.GetName())
        print 'Making new directory %s (line %d)'%(newdir,currentframe().f_lineno)
        IterateAllTheThings(i.GetListOfKeys(),j.GetListOfKeys(),newdir,options)

    #TTree
    elif issubclass(type(i),ROOT.TTree) :

        cans = []
        treename = i.GetName()
        
        # for compatibility with GetVariableHistsFromTrees
        i_keys = [options.label1]
        i_trees = {options.label1:i}

        j_keys = [options.label2]
        j_trees = {options.label2:j}

        # get the histograms from the files
        variables = []
        variables_j = list(vv.GetName() for vv in j.GetListOfBranches())

        for vv in i.GetListOfBranches() :
            v = vv.GetName()

            # print v,vv.GetClassName()
            skip = ['AuxContainerBase',
                    'DataVector',
                    'EventFormat',
                    'MissingETContainer',
                    'EventInfo',
                    'EventAuxInfo',
                    'AuxInfoBase',
                    ]
            if True in list(a in vv.GetClassName() for a in skip) :
                print 'Skipping %s (type %s)'%(v,vv.GetClassName())
                continue

            if v not in variables_j :
                print 'Warning! %s not in second file. Skipping.'%(v)
                continue

            # print v,vv.GetClassName()
            variables.append(v)

        for v in variables :

            if v not in options.histformat.keys() :
                options.limits[v] = [-1,-1,-1]
                options.xlabel[v] = v

            mc_hists = []

            if True :
                mc_hists.append(anaplot.GetVariableHistsFromTrees(i_trees,i_keys,v,'',options)[0])
                mc_hists[-1].SetTitle(options.label1)
                mc_hists[-1].SetLineWidth(2)
                mc_hists[-1].SetLineColor(1)
                mc_hists[-1].SetMarkerColor(1)

            if True :
                mc_hists.append(anaplot.GetVariableHistsFromTrees(j_trees,j_keys,v,'',options)[0])
                mc_hists[-1].SetTitle(options.label2)
                mc_hists[-1].SetLineWidth(ROOT.kRed+1)
                mc_hists[-1].SetLineColor(ROOT.kRed+1)
                mc_hists[-1].SetMarkerColor(ROOT.kRed+1)

            options.stack = False
            options.ratio = True
            cans.append(anaplot.DrawHistos(v,options,mc_hists))

        anaplot.UpdateCanvases(options,cans)
        if not os.path.exists(outdir) :
            os.makedirs(outdir)
        for c in cans :
            c.Print('%s/%s.pdf'%(outdir,c.GetName()))
            c.Print('%s/%s.C'%(outdir,c.GetName()))
        # anaplot.doSaving(options,cans)

    #TList,THashList,ListOfKeys
    elif issubclass(type(i),ROOT.TList) :

        secondarray = list(jitem.GetName() for jitem in j)

        for iitem in i :
            if iitem.GetName() not in secondarray : 
                print 'Warning! %s not in second file. Skipping.'%(iitem.GetName())
                continue
            jitem = j.At(secondarray.index(iitem.GetName()))

            is_tkey = False
            is_th1_or_tgraph = False

            if issubclass(type(iitem.ReadObj()),ROOT.TH1) :
                #print '%s is a TH1!'%(iitem.GetName())
                is_th1_or_tgraph = True
            elif issubclass(type(iitem.ReadObj()),ROOT.TGraph) :
                #print '%s is a TGraph!'%(iitem.GetName())
                is_th1_or_tgraph = True
            elif issubclass(type(iitem),ROOT.TKey) :
                #print '%s is a TKey!'%(iitem.GetName())
                is_tkey = True

            # TH1, TGraph
            if is_th1_or_tgraph :
                print 'Processing %s as a TH1 or TGraph.'%(iitem.GetName())
                IterateAllTheThings(iitem.ReadObj(),jitem.ReadObj(),outdir,options)

            # TKey (not sure why we have to find is_tkey earlier)
            elif is_tkey :
                newdir = '%s/%s'%(outdir,iitem.GetName())
                print 'Processing %s as a TKey. Making new directory %s (line %d)'%(iitem.GetName(),newdir,currentframe().f_lineno)
                IterateAllTheThings(iitem.ReadObj(),jitem.ReadObj(),newdir,options)

            else :
                print 'Within list: %s type'%(iitem.GetName()),type(iitem),'not supported yet. Let Kurt know! (Ref: 2)'

    else :
        print '%s type'%(i.GetName()),type(i),'not supported yet. Let Kurt know! (Ref: 1)'
        return

#-----------------------------------------------
if __name__ == '__main__':
    p = anaplot.TreePlottingOptParser()
    p.p.add_option('--first', type = 'string', default = 'first.root', dest = 'first', help = 'input File one' )
    p.p.add_option('--second', type = 'string', default = 'second.root', dest = 'second', help = 'input File two' )
    p.p.add_option('--ignore1', type = 'string', default = '', dest = 'ignore1', help = 'Ignore 1 (string to ignore)' )
    p.p.add_option('--ignore2', type = 'string', default = '', dest = 'ignore2', help = 'Ignore 2 (string to ignore)' )
    p.p.add_option('--label1', type = 'string', default = 'first', dest = 'label1', help = 'Ignore 1 (plot label 1)' )
    p.p.add_option('--label2', type = 'string', default = 'second', dest = 'label2', help = 'Ignore 2 (plot label 2)' )
    # --outdir is in TreePlottingOptParser

    p.p.remove_option('--bkgs')
    p.p.remove_option('--signal')
    p.p.remove_option('--data')

    (options,args) = p.parse_args()

    firstfile = ROOT.TFile(options.first,'READ')
    secondfile = ROOT.TFile(options.second,'READ')

    firstkeys = firstfile.GetListOfKeys()
    secondkeys = secondfile.GetListOfKeys()

    IterateAllTheThings(firstkeys,secondkeys,options.outdir,options)
