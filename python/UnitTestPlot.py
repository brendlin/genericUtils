#!/usr/bin/env python

import ROOT
import PlotFunctions as plotfunc
import TAxisFunctions as taxisfunc
from array import array

# Need to call this once to set up margins and stuff
plotfunc.SetupStyle()

#
# Useful if you don't want to use interactive mode
#
# ROOT.gROOT.SetBatch(True)

def main() :

    a = ROOT.TH1F('a','Legend text for a',48,-6,6)
    b = ROOT.TH1F('b','Legend text for b',48,-6,6)
    d = ROOT.TGraph(8,array('d',[-5.5,-4.5,-3.5,-2.5,-2.0,0,3.5,4.5])
                    ,array('d',[1000,2000,3000,2500,1000,2000,2200,2400,2500,2600]))
    d.SetNameTitle('mygraph','Legend text for graph')
    d.SetLineWidth(2)

    for i in [a,b] :
        i.Sumw2()

    rand = ROOT.TRandom3(1)

    for i in range(100000) :
        a.Fill(rand.Gaus(0,1))
        b.Fill(rand.Gaus(0,1))

    #
    # The class-based way of making plots
    #
    mycanvas = ROOT.TCanvas('mycanvas','blah',600,500)
    plotfunc.AddHistogram(mycanvas,a)
    plotfunc.AddHistogram(mycanvas,b)
    plotfunc.AddHistogram(mycanvas,d,drawopt='l')

    plotfunc.SetAxisLabels(mycanvas,'x axis','y axis')
    mycanvas.SetLogy()

    # Manual
    plotfunc.FormatCanvasAxes(mycanvas)
    plotfunc.SetColors(mycanvas)
    plotfunc.DrawText(mycanvas,[plotfunc.GetAtlasInternalText(status='Preliminary')
                                ,plotfunc.GetSqrtsText(13)+', '+plotfunc.GetLuminosityText()
                                ],0.20,0.78,0.5,0.92,totalentries=3)
    plotfunc.AutoFixAxes(mycanvas)
    plotfunc.MakeLegend(mycanvas)

    # Automatic (this one line replaces everything under "Manual")
    # plotfunc.FullFormatCanvasDefault(mycanvas)



    #
    # A ratio canvas from functions
    #
    mycanvas_ratio = plotfunc.RatioCanvas('my_ratiocanvas','blah',600,500)
    plotfunc.AddHistogram(mycanvas_ratio,d,drawopt='pl')
    plotfunc.AddHistogram(mycanvas_ratio,a)
    plotfunc.AddRatio(mycanvas_ratio,b,a)
    plotfunc.SetAxisLabels(mycanvas_ratio,'x axis','y axis')

    plotfunc.FullFormatCanvasDefault(mycanvas_ratio)
    taxisfunc.SetYaxisRanges(mycanvas_ratio.GetPrimitive('pad_bot'),0,2)
    # mycanvas_ratio.Print(plot_functions_can.GetName()+'.pdf')
    


    #
    # Not very important, but plotted objects are stored in the tobject_collector to prevent
    # them from going out of scope.
    #
    print '##'
    print '## The PlotFunctions TObject collector saved the follwing objects'
    print '## from going out of scope:'
    print '##'
    for i in plotfunc.tobject_collector :
        print ' -',i,i.GetName()

    raw_input('Press enter to exit')

if __name__ == '__main__':
    main()
