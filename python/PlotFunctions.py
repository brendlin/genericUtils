###
#
# New plotting functions :
#
# AddHistogram(can,hist)
# SetAxisLabels(can,xlabel,ylabel)
# SetColors(can,[color1,color2,color3...])
# DrawAtlasInternal(can)
# DrawLuminosity(can)
# SetPlotStyle(can,options...)
# MakeLegend(can,x1,x2,y1,y2,options...)
# SetupStyle()
#
# # MakeRatioPlot() Coming soon!
# # DrawText() Coming soon!
# # DrawHorizontalLine() Coming soon!
# # DrawVerticalLine() Coming soon!
# # SetStyles() Coming soon!
#
###

#
# This is very important. It picks up all the histogram objects that otherwise would
# go out of scope.
#
global tobject_collector;
tobject_collector = []

def AddHistogram(can,hist,drawopt='pE1') :
    from ROOT import TH1F
    tmp = hist.Clone()
    if type(TH1F()) in list(type(a) for a in can.GetListOfPrimitives()) :
        drawopt += 'sames'
    else :
        tmp.GetXaxis().SetTitleOffset(0.98)
    tobject_collector.append(tmp)
    tmp.SetMarkerSize(1)
    tmp.SetMarkerStyle(20)
    tmp.SetName('%s_%s'%(can.GetName(),hist.GetName()))
    can.cd()
    tmp.Draw(drawopt)

def SetAxisLabels(can,xlabel,ylabel) :
    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetXaxis') :
            i.GetXaxis().SetTitle(xlabel)
            i.GetYaxis().SetTitle(ylabel)
            break
    return

def SetStyles(marker_styles=[],marker_sizes=[]) :
    return

def SetColors(can,these_colors=[]) :
    if not these_colors :
        from ROOT import kBlack,kRed,kBlue,kAzure,kGreen,kMagenta,kCyan,kOrange,kGray,kYellow
        these_colors = [kBlack+0,kRed+1,kAzure-2,kGreen+1,kMagenta+1,kCyan+1,kOrange+1
                        ,kBlack+2,kRed+3,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3
                        ,kGray,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7
                        ,kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5
                        ,21,22,23,24,25,26,27,28,29,30
                        ,21,22,23,24,25,26,27,28,29,30
                        ,21,22,23,24,25,26,27,28,29,30
                        ]
        
    color_count = 0
    for i in can.GetListOfPrimitives() :
        if hasattr(i,'SetLineColor') :
            i.SetLineColor(these_colors[color_count])
        if hasattr(i,'SetMarkerColor') :
            i.SetMarkerColor(these_colors[color_count])
            color_count += 1
        if color_count >= len(these_colors) :
            break
    
    return

def MakeRatioPlot() :
    return

def DrawAtlasInternal(can,x=.2,y=.9,angle=0,align='',size=18,preliminary=False) :
    from ROOT import TLatex
    can.cd()
    t = TLatex()
    t.SetNDC()
    t.SetTextSize(size)
    t.SetTextFont(73)
    if align == 'R': t.SetTextAlign(31)
    if angle : t.SetTextAngle(angle)
    status = 'Internal'
    if preliminary : status = 'Preliminary'
    t.DrawLatex(x,y,'ATLAS #font[42]{%s}'%(status)) # for some reason 42 is appropriate, not 43
    t.SetTextSize(size)
    can.Update()
    return

def DrawLuminosity(can,x=.2,y=.84,angle=0,align='',size=18,lumi=20.3,sqrts=8,two_lines=True) :
    from ROOT import TLatex
    can.cd()
    t = TLatex()
    t.SetNDC()
    t.SetTextSize(size)
    if can == 'Top' :
        t.SetTextSize(0.05)
    t.SetTextFont(43)
    if align == 'R': t.SetTextAlign(31)
    if angle : t.SetTextAngle(angle)
    if two_lines :
        t.DrawLatex(x,y,'#sqrt{s} = %d TeV'%(sqrts))
        t.DrawLatex(x,y-.06,'#lower[-0.2]{#scale[0.60]{#int}}Ldt = %1.1f fb^{-1}'%(lumi))
    else :
        t.DrawLatex(x,y,'#sqrt{s} = %d TeV, #lower[-0.2]{#scale[0.60]{#int}}Ldt = %1.1f fb^{-1}'%(sqrts,lumi))
    can.Update()
    return

def DrawText() :
    return

def DrawHorizontalLine() :
    return

def DrawVerticalLine() :
    return

def MakeLegend(can,x1=.8,y1=.8,x2=.9,y2=.9,textsize=18,ncolumns=1) :
    from ROOT import TLegend,TH1,gStyle
    #
    # if a previous version exists from this function, delete it
    #
    if can.GetPrimitive('legend') :
        can.GetPrimitive('legend').Delete()
    leg = TLegend(x1,y1,x2,y2)
    tobject_collector.append(leg)
    leg.SetTextFont(43)
    leg.SetTextSize(textsize)
    leg.SetName('legend')
    leg.SetTextFont(43)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetNColumns(ncolumns)
    #
    # Add by TH1 GetTitle()
    #
    for i in can.GetListOfPrimitives() :
        drawopt = i.GetDrawOption()
        if issubclass(type(i),TH1) :
            leg.AddEntry(i,i.GetTitle(),'f') # plef

    # recipe for making roughly square boxes
    h = leg.GetY2()-leg.GetY1()
    w = leg.GetX2()-leg.GetX1()
    leg.SetMargin(leg.GetNColumns()*h/float(leg.GetNRows()*w))
    leg.Draw()
    can.Update()

def SetPlotStyle(can
                 ,XTitleSize   = 22
                 ,XTitleOffset = 0.98
                 ,XTitleFont   = 43
                 ,XLabelSize   = 22
                 ,XLabelOffset = 0.002
                 ,XLabelFont   = 43
                 
                 ,YTitleSize   = 22
                 ,YTitleOffset = 1.75
                 ,YTitleFont   = 43
                 ,YLabelSize   = 22
                 ,YLabelOffset = 0.006
                 ,YLabelFont   = 43
                 ,YNDiv = [5,5,0]
                 
                 ,ZTitleSize   = 22
                 ,ZTitleOffset = 0.85
                 ,ZTitleFont   = 43
                 ,ZLabelSize   = 22
                 ,ZLabelOffset = 0.002
                 ,ZLabelFont   = 43
                 ) :
    for i in can.GetListOfPrimitives() :
        if not hasattr(i,'GetXaxis') :
            continue
        i.GetXaxis().SetTitleSize  (XTitleSize  )
        i.GetXaxis().SetTitleOffset(XTitleOffset)
        i.GetXaxis().SetTitleFont  (XTitleFont  )
        i.GetXaxis().SetLabelSize  (XLabelSize  )
        i.GetXaxis().SetLabelOffset(XLabelOffset)
        i.GetXaxis().SetLabelFont  (XLabelFont  )
        
        i.GetYaxis().SetTitleSize  (YTitleSize  )
        i.GetYaxis().SetTitleOffset(YTitleOffset)
        i.GetYaxis().SetTitleFont  (YTitleFont  )
        i.GetYaxis().SetLabelSize  (YLabelSize  )
        i.GetYaxis().SetLabelOffset(YLabelOffset)
        i.GetYaxis().SetLabelFont  (YLabelFont  )
        i.GetYaxis().SetNdivisions (YNDiv[0],YNDiv[1],YNDiv[2])
        
        i.GetZaxis().SetTitleSize  (ZTitleSize  )
        i.GetZaxis().SetTitleOffset(ZTitleOffset)
        i.GetZaxis().SetTitleFont  (ZTitleFont  )
        i.GetZaxis().SetLabelSize  (ZLabelSize  )
        i.GetZaxis().SetLabelOffset(ZLabelOffset)
        i.GetZaxis().SetLabelFont  (ZLabelFont  )

        break
    return

def SetupStyle() :
    from ROOT import gROOT,TStyle
    mystyle = TStyle("mystyle","mystyle")
    mystyle.SetStatColor(0)
    mystyle.SetTitleColor(0)
    mystyle.SetCanvasColor(0)
    mystyle.SetPadColor(0)
    mystyle.SetPadBorderMode(0)
    mystyle.SetCanvasBorderMode(0)
    mystyle.SetFrameBorderMode(0)
    mystyle.SetOptStat(0)
    mystyle.SetStatH(0.3)
    mystyle.SetStatW(0.3)
    mystyle.SetTitleColor(1)
    mystyle.SetTitleFillColor(0)
    mystyle.SetTitleBorderSize(0)
    mystyle.SetHistLineWidth(2)
    mystyle.SetLineWidth(1)
    mystyle.SetFrameFillColor(0)
    mystyle.SetOptTitle(0)
    mystyle.SetPaintTextFormat('4.1f ')
    mystyle.SetEndErrorSize(3)

    mystyle.SetPadTopMargin(0.05)
    mystyle.SetPadRightMargin(0.05)
    mystyle.SetPadBottomMargin(0.11)
    mystyle.SetPadLeftMargin(0.16)

    mystyle.SetMarkerStyle(20)
    mystyle.SetMarkerSize(1.2)

    #
    # NOTE that in ROOT rendering the font size is slightly smaller than in pdf viewers!
    # The effect is about 2 points (i.e. 18 vs 20 font)
    #
    # all axes
    mystyle.SetTitleSize  (22   ,'xyz')
    mystyle.SetTitleFont  (43   ,'xyz')
    mystyle.SetLabelSize  (22   ,'xyz')
    mystyle.SetLabelFont  (43   ,'xyz')

    # x axis
    mystyle.SetTitleXOffset(1.0)
    mystyle.SetLabelOffset(0.002,'x')

    # y axis
    mystyle.SetTitleOffset(1.75 ,'y')
    mystyle.SetLabelOffset(0.002,'y')
    
    gROOT.SetStyle("mystyle")

    return
