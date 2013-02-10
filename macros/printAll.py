from ROOT import TFile, gDirectory,gROOT,gStyle, TH2F, TH1F, kRed, kGreen, kBlue, kYellow, TCanvas, gPad, TArrow, TText, TFile,TLine,TMarker,TObject,TPad
from PlotUtils import h1types,graphtypes
from types import *
import os
import sys
gROOT.SetBatch(True)
#import AtlasStyle
import rootlogon

#-----------------------------------------------
def checkdir(name) :
    #print "os.getcwd is: "+os.getcwd()
    for dir in os.listdir(os.getcwd()):
        #print dir
        if dir == name:
            return False
    return True

#-----------------------------------------------
def printthings(thelist,log,keyname=''):
    for i in thelist:
        obj = i.ReadObj()
        if i.GetClassName() == "TDirectoryFile":
            newlist = i.ReadObj().GetListOfKeys()
            if checkdir(i.GetName()):
                os.mkdir(i.GetName())
            os.chdir(i.GetName())
            printthings(newlist,log)
        if type(obj) == type(TCanvas()) :
            can = i.ReadObj()
            if log : can.SetLogy()
            can.Print(obj.GetTitle()+".pdf")
        elif type(obj) in h1types :
            can = TCanvas(obj.GetName(),obj.GetName(),500,500)
            if log : can.SetLogy()
            can.cd()
            obj.Draw()
            can.Print(i.GetName()+'.pdf')
            del can
    os.chdir("../")
    return 0

def stripROOT(name) :
    return '.'.join(name.split('.')[:-1])

#-----------------------------------------------
def main(infile,outdir,log):
    name = stripROOT(infile)
    isIDAlignment = ('IDAlignment' in name)
    file = TFile(os.getcwd()+"/"+name+".root","read")
    makedir = True
    for dirs in os.listdir(os.getcwd()):
        if dirs == outdir:
            makedir = False
    if makedir:
        os.mkdir(outdir)

    os.chdir(outdir)

    list = file.GetListOfKeys()
    printthings(list,log)
    
#-----------------------------------------------
if __name__ == "__main__":
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--in',  type = 'string', default = '', dest = 'infile', help = 'Input file' )
    p.add_option('--log',action='store_true', dest='log', help = 'Make log plots', default=False)
    p.add_option('--out',  type = 'string', default = '', dest = 'out', help = 'Output dir' )
    (options,args) = p.parse_args()

    outdir = options.out if options.out else stripROOT(options.infile)

    main(options.infile,outdir,options.log)
