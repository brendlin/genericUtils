#!/usr/bin/env python

import ROOT
import PlotFunctions as plotfunc
import TAxisFunctions as taxisfunc
import os,sys

ROOT.gROOT.SetBatch(True)
plotfunc.SetupStyle()

#-----------------------------------------------
def IterateAllTheThings(i,j,outdir):

    #if type(i) in unsupported_types : return

    #TH1 Types
    if issubclass(type(i),ROOT.TH1) :
        #OverlayPlots(outdir,'',i.GetName(),[i,j])
        c = plotfunc.RatioCanvas(i.GetName(),i.GetName(),600,500)
        plotfunc.AddHistogram(c,i)
        plotfunc.AddRatio(c,j,i)
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
        newdir = '%s/%s'%(outdir,mkdir(i.GetName()))
        IterateAllTheThings(i.GetListOfPrimitives(),j.GetListOfPrimitives(),newdir)
        
    # TDirectoryFile
    elif issubclass(type(i),ROOT.TDirectoryFile) :
        newdir = '%s/%s'%(outdir,mkdir(i.GetName()))
        IterateAllTheThings(i.GetListOfKeys(),j.GetListOfKeys(),newdir)

    #TTree
    elif issubclass(type(i),ROOT.TTree) :
        print '\nType TTree not supported. And it\'s a fucking shame.'
        return
        treedir = outdir.mkdir(i.ReadObj().GetName())
        tree1 = firstfile.Get('TestTree')
        tree2 = secondfile.Get(j.ReadObj().GetName())
        tree1.Draw('class')

    #TList,THashList
    elif issubclass(type(i),ROOT.TList) :
        secondarray = []
        for jitem in j :
            secondarray.append(jitem.GetName())
        for iitem in i :
            if iitem.GetName() not in secondarray : continue
            jitem = j.At(secondarray.index(iitem.GetName()))

            #TKey
            if issubclass(type(iitem),ROOT.TKey) :
                newdir = '%s/%s'%(outdir,iitem.GetName())
                IterateAllTheThings(iitem.ReadObj(),jitem.ReadObj(),newdir)
            elif issubclass(type(iitem),ROOT.TH1) or issubclass(type(iitem),ROOT.TGraph) :
                newdir = '%s/%s'%(outdir,iitem.GetName())
                IterateAllTheThings(iitem,jitem,newdir)
            #elif type(iitem) in unsupported_types : return
            else :
                print 'Within list: Type',type(iitem),'not supported yet. Let Kurt know! (Ref: 2)'

    else :
        print 'Type',type(i),'not supported yet. Let Kurt know! (Ref: 1)'
        return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--first', type = 'string', default = 'TMVA_showerppetzetaa.root', dest = 'first', help = 'input File one' )
    p.add_option('--second', type = 'string', default = 'TMVA_showerppxsetzetaa.root', dest = 'second', help = 'input File two' )
    p.add_option('--key1', type = 'string', default = '', dest = 'key1', help = 'Key 1 (string to ignore)' )
    p.add_option('--key2', type = 'string', default = '', dest = 'key2', help = 'Key 2 (string to ignore)' )
    #p.add_option('--out', type = 'string', default = 'tmva_comparison.root', dest = 'output', help = 'Output file' )
    p.add_option('--outdir', type = 'string', default = 'out', dest = 'outdir', help = 'Output file' )

    (options,args) = p.parse_args()

    firstfile = ROOT.TFile(options.first,'READ')
    secondfile = ROOT.TFile(options.second,'READ')
    #outputfile = ROOT.TFile(options.output,'RECREATE')

    firstkeys = firstfile.GetListOfKeys()
    secondkeys = secondfile.GetListOfKeys()

    IterateAllTheThings(firstkeys,secondkeys,options.outdir)
