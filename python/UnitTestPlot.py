#!/usr/bin/env python

from ROOT import TH1F,TRandom3,TCanvas,gDirectory
from PlotUtils import PlotObject
from PlotFunctions import *

def main() :
    a = TH1F('a','a',100,-5,5)
    b = TH1F('b','b',100,-5,5)
    c = TH1F('c','c',100,-5,5)
    
    rand = TRandom3(1)

    for i in range(10000) :
        a.Fill(rand.Gaus(0,1))
        b.Fill(rand.Gaus(0,1))
        c.Fill(rand.Gaus(0,1))


    #
    # The class-based way of making plots
    #
    plot_utils_can = PlotObject('plot_utils_can',[a,b,c],drawtitle=False)
    #plot_utils_can.MakeRatioPlot(0,[1,2])
    plot_utils_can.DrawLuminosity()
    plot_utils_can.DrawAtlasPreliminary(internal=True)
    plot_utils_can.SetAxisLabels('x axis','y axis')
    plot_utils_can.RecreateLegend(.8,.8,.9,.9)
    plot_utils_can.SavePDF()

    #
    # The function way of making plots
    #
    SetupStyle()
    plot_functions_can = TCanvas('plot_functions_can','plot_functions_can',500,500)
    AddHistogram(plot_functions_can,a)
    AddHistogram(plot_functions_can,b)
    AddHistogram(plot_functions_can,c)
    SetPlotStyle(plot_functions_can)
    SetColors(plot_functions_can)
    DrawLuminosity(plot_functions_can)
    DrawAtlasInternal(plot_functions_can,preliminary=True)
    SetAxisLabels(plot_functions_can,'x axis','y axis')
    MakeLegend(plot_functions_can,.8,.75,.9,.85)
    plot_functions_can.Print(plot_functions_can.GetName()+'.pdf')

    # def SetAxisProperties(**kwargs) :
    #     for i in kwargs.keys() :
    #         print i,kwargs[i]

    # mydict = {'a':1,'b':2}
    # SetAxisProperties(asdf='',svgs='')

if __name__ == '__main__':
    main()
