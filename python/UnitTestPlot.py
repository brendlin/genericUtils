#!/usr/bin/env python

from ROOT import TH1F,TRandom3,TCanvas,gDirectory,TGraph
from PlotUtils import PlotObject
from PlotFunctions import *
from TAxisFunctions import *
from array import array

def main() :
    a = TH1F('a','a',48,-6,6)
    b = TH1F('b','b',48,-6,6)
    cbins = list(list(a/2. for a in range(-6*2,-3*2))
                 +list(a/4. for a in range(-3*4,3*4))
                 +list(a/2. for a in range(3*2,6*2)))+[6]
    c = TH1F('c','c',len(cbins)-1,array('d',cbins))
    d = TGraph(5,array('d',[-5.5,-4.5,-3.5,-2.5,-2.0,0,3.5,4.5])
               ,array('d',[10000,20000,30000,25000,10000,20000,22000,24000,25000,26000]))
    d.SetNameTitle('mygraph','Legend text for graph')
    d.SetLineWidth(2)

    a.SetTitle('Legend text for a')
    b.SetTitle('Legend text for b')
    c.SetTitle('Legend text for c')

    rand = TRandom3(1)

    for i in range(100000) :
        a.Fill(rand.Gaus(0,1))
        tmp = rand.Gaus(0,1)
        b.Fill(tmp)
        c.Fill(tmp)

    ConvertToDifferential(a)
    ConvertToDifferential(b)
    ConvertToDifferential(c)

    #
    # The class-based way of making plots
    #
    plot_utils_can = PlotObject('plot_utils_can',[a,b,c],drawtitle=False)
    #plot_utils_can.MakeRatioPlot(0,[1,2])
    plot_utils_can.DrawLuminosity()
    plot_utils_can.DrawAtlasPreliminary(internal=True)
    plot_utils_can.SetAxisLabels('x axis','y axis')
    plot_utils_can.RecreateLegend(.6,.83,1.,.93)
    plot_utils_can.SavePDF()

    #
    # The function way of making plots
    #
    SetupStyle()
    plot_functions_can = TCanvas('plot_functions_can','plot_functions_can',500,500)
    AddHistogram(plot_functions_can,b)
    AddHistogram(plot_functions_can,c)
    FormatCanvas(plot_functions_can)
    SetColors(plot_functions_can)
    DrawLuminosity(plot_functions_can)
    DrawAtlasInternal(plot_functions_can,preliminary=True)
    SetAxisLabels(plot_functions_can,'x axis','y axis')
    MakeLegend(plot_functions_can,.6,.83,1.,.93)
    plot_functions_can.SetLogy()
    AutoFixAxes(plot_functions_can)
    plot_functions_can.Print(plot_functions_can.GetName()+'.pdf')

    #
    # A ratio canvas from functions
    #
    plot_functions_can_ratio = RatioCanvas('plot_functions_can_ratio','plot_functions_can_ratio'
                                           ,500,600,.35)
    AddHistogramTop(plot_functions_can_ratio,d,drawopt='pl')
    AddHistogramTop(plot_functions_can_ratio,a)
    AddRatio(plot_functions_can_ratio,b,a)

    SetColors(plot_functions_can_ratio)
    FormatCanvas(plot_functions_can_ratio,YTitleOffset=2.3)
    SetAxisLabels(plot_functions_can_ratio,'x axis','y axis','ratio b/a')
    SetLeftMargin(plot_functions_can_ratio,0.18)
    MakeLegend(GetTopPad(plot_functions_can_ratio),0.55,0.77,1,0.94)
    DrawAtlasInternal(GetTopPad(plot_functions_can_ratio))
    DrawLuminosity(GetTopPad(plot_functions_can_ratio))
    AutoFixAxes(GetTopPad(plot_functions_can_ratio))
    SetYaxisRange(GetBotPad(plot_functions_can_ratio),0,2)
    plot_functions_can_ratio.Print(plot_functions_can_ratio.GetName()+'.pdf')
    
    print '##'
    print '## The PlotFunctions TObject collector saved the follwing objects'
    print '## from going out of scope:'
    print '##'
    for i in tobject_collector :
        print ' -',i,i.GetName()

if __name__ == '__main__':
    main()
