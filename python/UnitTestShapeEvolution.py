#!/usr/bin/env python

import ROOT
import PlotFunctions as plotfunc
import TAxisFunctions as taxisfunc
from ShowerShapeEvolutionPlotter import ShowerShapeEvolutionPlot
from array import array

# Need to call this once to set up margins and stuff
plotfunc.SetupStyle()

#
# Useful if you don't want to use interactive mode
#
# ROOT.gROOT.SetBatch(True)

def main() :

    data_plots = []
    mc_plots = []
    for i in range(5) :
        data_plots.append(ROOT.TH1F('a_%d'%(i),'Data',48,-6,6))
        mc_plots  .append(ROOT.TH1F('b_%d'%(i),'MC'  ,48,-6,6))
        mc_plots[-1].SetLineColor(ROOT.kRed+1)

    for plot in data_plots + mc_plots :
        plot.Sumw2()
        plot.SetLineWidth(2)

    rand = ROOT.TRandom3(1)

    for i in range(100000) :
        for j in range(len(data_plots)) :
            data_plots[j].Fill(rand.Gaus(0,1) + j*0.2)
            mc_plots  [j].Fill(rand.Gaus(0,1) + j*0.15)

    #
    # Bin labeling
    #
    bin_edges = [15,20,25,30,40,50]
    template = '%s^{ }<^{ }p_{T}^{ }<^{ }%s GeV'
    labels = list(template%(bin_edges[a],bin_edges[a+1]) for a in range(len(bin_edges)-1))

    mycanvas = ROOT.TCanvas('mycanvas','blah',600,500)

    #
    # The main call:
    #
    ShowerShapeEvolutionPlot(mycanvas,labels,data_plots,mc_plots)
    mycanvas.SetGridx()

    plotfunc.DrawText(mycanvas,[plotfunc.GetAtlasInternalText(status='Internal')
                                ,plotfunc.GetSqrtsText(13)+', '+plotfunc.GetLuminosityText()
                                ],0.27,0.88,0.57,0.99,totalentries=2)


    mycanvas.Print(mycanvas.GetName()+'.pdf')
    raw_input('Press enter to exit')
    return

if __name__ == '__main__':
    main()
