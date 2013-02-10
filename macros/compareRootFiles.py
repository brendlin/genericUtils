#from ROOT import TFile,TKey,TDirectoryFile,TTree,TBranch,gDirectory,gROOT,gStyle, TH2F, TH1F, kRed, kGreen, kBlue, kYellow, TCanvas, gPad, TArrow, TText, TFile,TLine,TMarker,TObject,TPad
from ROOT import *
from PlotUtils import *
import os
import sys
from types import *
gROOT.SetBatch(True)

#-----------------------------------------------
def IterateAllTheThings(i,j,outputfileordir):

    if type(i) in unsupported_types : return

    #TH1 Types
    if type(i) in h1types :
        OverlayPlots(outputfileordir,'',i.GetName(),[i,j])
        
    # TCanvas
    elif type(i) == type(TCanvas()) :
        newdir = outputfileordir.mkdir(i.GetName())
        IterateAllTheThings(i.GetListOfPrimitives(),j.GetListOfPrimitives(),newdir)
        
    # TDirectoryFile
    elif type(i) == type(TDirectoryFile()) :
        dirdir = outputfileordir.mkdir(i.GetName())
        IterateAllTheThings(i.GetListOfKeys(),j.GetListOfKeys(),dirdir)

    #TTree
    elif type(i) == type(TTree()) :
        print '\nType TTree not supported. And it\'s a fucking shame.'
        return
        treedir = outputfileordir.mkdir(i.ReadObj().GetName())
        tree1 = firstfile.Get('TestTree')
        tree2 = secondfile.Get(j.ReadObj().GetName())
        tree1.Draw('class')

    #TList,THashList
    elif type(i) in listtypes :
        secondarray = []
        for jitem in j :
            secondarray.append(jitem.GetName())
        for iitem in i :
            if iitem.GetName() not in secondarray : continue
            jitem = j.At(secondarray.index(iitem.GetName()))

            #TKey
            if type(iitem) == type(TKey()) :
                IterateAllTheThings(iitem.ReadObj(),jitem.ReadObj(),outputfileordir)
            elif (type(iitem) in h1types) or (type(iitem) in graphtypes) :
                IterateAllTheThings(iitem,jitem,outputfileordir)
            elif type(iitem) in unsupported_types : return
            else :
                print 'Within list: Type',type(iitem),'not supported yet. Let Kurt know! (Ref: 2)'
    else :
        print 'Type',type(i),'not supported yet. Let Kurt know! (Ref: 1)'
        return

#-----------------------------------------------
if __name__ == "__main__":
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--first', type = 'string', default = "TMVA_showerppetzetaa.root", dest = 'first', help = 'input File one' )
    p.add_option('--second', type = 'string', default = "TMVA_showerppxsetzetaa.root", dest = 'second', help = 'input File two' )
    p.add_option('--key1', type = 'string', default = '', dest = 'key1', help = 'Key 1 (string to ignore)' )
    p.add_option('--key2', type = 'string', default = '', dest = 'key2', help = 'Key 2 (string to ignore)' )
    p.add_option('--out', type = 'string', default = "tmva_comparison.root", dest = 'output', help = 'Output file' )

    (options,args) = p.parse_args()

    firstfile = TFile(options.first,"READ")
    secondfile = TFile(options.second,"READ")
    outputfile = TFile(options.output,"RECREATE")

    firstkeys = firstfile.GetListOfKeys()
    secondkeys = secondfile.GetListOfKeys()

    IterateAllTheThings(firstkeys,secondkeys,outputfile)
