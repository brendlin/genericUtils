###
#
# New plotting functions :
#
# AddHistogram(can,hist)
# SetAxisLabels(can,xlabel,ylabel)
# SetColors(can,[color1,color2,color3...])
# DrawAtlasInternal(can)
# DrawLuminosity(can)
# MakeLegend(can,x1,x2,y1,y2,options...)
# SetupStyle()
# FormatCanvas(can,options...) - must be run AFTER the first histograms are added!
# RatioCanvas()
# ConvertToDifferential()
# SetYaxisRange(can)
# # DrawText() Coming soon!
# # DrawHorizontalLine() Coming soon!
# # DrawVerticalLine() Coming soon!
# # SetMarkerStyles() Coming soon!
# # SetFillStyles() Coming soon!
#
###

#
# This is very important. It picks up all the histogram objects that otherwise would
# go out of scope.
#
global tobject_collector;
tobject_collector = []

def ConvertToDifferential(hist) :
    for i in range(hist.GetNbinsX()) :
        content = hist.GetBinContent(i+1)
        error = hist.GetBinError(i+1)
        width = hist.GetBinWidth(i+1)
        hist.SetBinContent(i+1,content/float(width))
        hist.SetBinError(i+1,error/float(width))
    return

def AddHistogram(can,hist,drawopt='pE1') :
    from ROOT import TH1,TGraph
    tmp = hist.Clone()
    is_graph = issubclass(type(hist),TGraph)

    plot_exists = list(issubclass(type(a),TH1) for a in can.GetListOfPrimitives())
    plot_exists += list(issubclass(type(a),TGraph) for a in can.GetListOfPrimitives())

    if (not is_graph) and (True in plot_exists) :
        drawopt += 'sames'
    if is_graph and not (True in plot_exists) :
        drawopt += 'a'

    tobject_collector.append(tmp)
    tmp.SetMarkerSize(1)
    tmp.SetMarkerStyle(20)
    print tmp.GetName()
    tmp.SetName('%s_%s'%(can.GetName(),hist.GetName()))
    can.cd()
    tmp.Draw(drawopt)

def SetAxisLabels(can,xlabel,ylabel,yratiolabel='ratio') :
    if 'pad_top' in (a.GetName() for a in can.GetListOfPrimitives()) :
        SetAxisLabels(can.GetPrimitive('pad_bot'),xlabel,yratiolabel)
        SetAxisLabels(can.GetPrimitive('pad_top'),'',ylabel)
    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetXaxis') :
            i.GetXaxis().SetTitle(xlabel)
            i.GetYaxis().SetTitle(ylabel)
            break
    return

def SetMarkerStyles(marker_styles=[],marker_sizes=[]) :
    return

def SetFillStyles(marker_styles=[],marker_sizes=[]) :
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
        
    the_primitives = can.GetListOfPrimitives()
    if can.GetPrimitive('pad_top') :
        the_primitives = can.GetPrimitive('pad_top').GetListOfPrimitives()

    color_count = 0
    for i in the_primitives :
        if hasattr(i,'SetLineColor') and hasattr(i,'SetMarkerColor') :
            i.SetLineColor(these_colors[color_count])
            i.SetMarkerColor(these_colors[color_count])
            i.SetFillColor(0)
            #
            # Check if there is a bottom pad, with ratios...
            #
            if can.GetPrimitive('pad_bot') :
                original_name = i.GetName().replace('pad_top_','')
                j = can.GetPrimitive('pad_bot').GetPrimitive('pad_bot_%s_ratio'%(original_name))
                if j :
                    print j.GetName()
                    j.SetLineColor(these_colors[color_count])
                    j.SetMarkerColor(these_colors[color_count])
                    j.SetFillColor(0)
            color_count += 1
        if color_count >= len(these_colors) :
            break
    
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
    can.Modified()
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
        t.DrawLatex(x,y-0.06,'#lower[-0.2]{#scale[0.60]{#int}}Ldt = %1.1f fb^{-1}'%(lumi))
    else :
        t.DrawLatex(x,y,'#sqrt{s} = %d TeV, #lower[-0.2]{#scale[0.60]{#int}}Ldt = %1.1f fb^{-1}'%(sqrts,lumi))
    can.Modified()
    can.Update()
    return

def DrawText() :
    return

def DrawHorizontalLine() :
    return

def DrawVerticalLine() :
    return

def MakeLegend(can,x1=.8,y1=.8,x2=.9,y2=.9,textsize=18,ncolumns=1) :
    from ROOT import TLegend,TH1,gStyle,TGraph
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
        if issubclass(type(i),TH1) or issubclass(type(i),TGraph) :
            leg.AddEntry(i,i.GetTitle(),'f') # plef

    # recipe for making roughly square boxes
    h = leg.GetY2()-leg.GetY1()
    w = leg.GetX2()-leg.GetX1()
    leg.SetMargin(leg.GetNColumns()*h/float(leg.GetNRows()*w))
    can.cd()
    leg.Draw()
    can.Modified()
    can.Update()

def FormatCanvas(can
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

    if can.GetPrimitive('pad_top') :
        FormatCanvas(can.GetPrimitive('pad_top'),XLabelOffset=0.1
                     ,XTitleSize=XTitleSize,XTitleOffset=XTitleOffset,XTitleFont=XTitleFont
                     ,XLabelSize=XLabelSize,XLabelFont=XLabelFont
                     ,YTitleSize=YTitleSize,YTitleOffset=YTitleOffset,YTitleFont=YTitleFont
                     ,YLabelSize=YLabelSize,YLabelOffset=YLabelOffset,YLabelFont=YLabelFont,YNDiv=YNDiv
                     ,ZTitleSize=ZTitleSize,ZTitleOffset=ZTitleOffset,ZTitleFont=ZTitleFont
                     ,ZLabelSize=ZLabelSize,ZLabelOffset=ZLabelOffset,ZLabelFont=ZLabelFont
                     )
    if can.GetPrimitive('pad_bot') :
        FormatCanvas(can.GetPrimitive('pad_bot')
                     ,XTitleSize=XTitleSize,XTitleOffset=XTitleOffset,XTitleFont=XTitleFont
                     ,XLabelSize=XLabelSize,XLabelOffset=XLabelOffset,XLabelFont=XLabelFont
                     ,YTitleSize=YTitleSize,YTitleOffset=YTitleOffset,YTitleFont=YTitleFont
                     ,YLabelSize=YLabelSize,YLabelOffset=YLabelOffset,YLabelFont=YLabelFont,YNDiv=YNDiv
                     ,ZTitleSize=ZTitleSize,ZTitleOffset=ZTitleOffset,ZTitleFont=ZTitleFont
                     ,ZLabelSize=ZLabelSize,ZLabelOffset=ZLabelOffset,ZLabelFont=ZLabelFont
                     )

    for i in can.GetListOfPrimitives() :
        if not hasattr(i,'GetXaxis') :
            continue
        i.GetXaxis().SetTitleSize  (XTitleSize  )
        i.GetXaxis().SetTitleOffset(XTitleOffset/float(can.GetHNDC()))
        i.GetXaxis().SetTitleFont  (XTitleFont  )
        i.GetXaxis().SetLabelSize  (XLabelSize  )
        i.GetXaxis().SetLabelOffset(XLabelOffset/float(can.GetHNDC()))
        i.GetXaxis().SetLabelFont  (XLabelFont  )

        i.GetXaxis().SetTickLength(0.02/float(can.GetHNDC()))
        
        i.GetYaxis().SetTitleSize  (YTitleSize  )
        i.GetYaxis().SetTitleOffset(YTitleOffset)
        i.GetYaxis().SetTitleFont  (YTitleFont  )
        i.GetYaxis().SetLabelSize  (YLabelSize  )
        i.GetYaxis().SetLabelOffset(YLabelOffset)
        i.GetYaxis().SetLabelFont  (YLabelFont  )
        i.GetYaxis().SetNdivisions (YNDiv[0],YNDiv[1],YNDiv[2])

        if not hasattr(i,'GetZaxis') :
            continue
        i.GetZaxis().SetTitleSize  (ZTitleSize  )
        i.GetZaxis().SetTitleOffset(ZTitleOffset)
        i.GetZaxis().SetTitleFont  (ZTitleFont  )
        i.GetZaxis().SetLabelSize  (ZLabelSize  )
        i.GetZaxis().SetLabelOffset(ZLabelOffset)
        i.GetZaxis().SetLabelFont  (ZLabelFont  )

        break

    can.Modified()
    can.Update()
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

def RatioCanvas(canvas_name,canvas_title,canw=500,canh=600,ratio_size_as_fraction=0.35) :
    from ROOT import TCanvas,TPad
    c = TCanvas(canvas_name,canvas_title,canw,canh)
    c.cd()
    top = TPad("pad_top", "This is the top pad",0.0,ratio_size_as_fraction,1.0,1.0)
    top.SetBottomMargin(0.02/float(top.GetHNDC()))
    top.SetTopMargin   (0.04/float(top.GetHNDC()))
    top.SetRightMargin (0.05 )
    top.SetLeftMargin  (0.16 )
    top.SetFillColor(0)
    top.Draw()
    tobject_collector.append(top)

    c.cd()
    bot = TPad("pad_bot", "This is the bottom pad",0.0,0.0,1.0,ratio_size_as_fraction)
    bot.SetBottomMargin(0.09/float(bot.GetHNDC()))
    bot.SetTopMargin   (0.02/float(bot.GetHNDC()))
    bot.SetRightMargin (0.05)
    bot.SetLeftMargin  (0.16)
    bot.SetFillColor(0)
    bot.Draw()
    tobject_collector.append(bot)
    
    return c

def SetLeftMargin(can,margin) :
    if 'pad_top' in (a.GetName() for a in can.GetListOfPrimitives()) :
        SetLeftMargin(can.GetPrimitive('pad_top'),margin)
    if 'pad_bot' in (a.GetName() for a in can.GetListOfPrimitives()) :
        SetLeftMargin(can.GetPrimitive('pad_bot'),margin)
    can.SetLeftMargin(margin)
    can.Modified()
    can.Update()

def SetYaxisRange(can,min,max) :
    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetYaxis') :
            i.GetYaxis().SetRangeUser(min,max)
            break
    return

def GetTopPad(can) :
    return can.GetPrimitive('pad_top')

def GetBotPad(can) :
    return can.GetPrimitive('pad_bot')

def AddHistogramTop(can,hist,drawopt='pE1') :
    AddHistogram(can.GetPrimitive('pad_top'),hist,drawopt)

def AddHistogramBot(can,hist,drawopt='pE1') :
    AddHistogram(can.GetPrimitive('pad_bot'),hist,drawopt)

def AddRatio(can,hist,ref_hist,divide='') : # "" for uncorrelated, "B" for binomial
    ratioplot = hist.Clone()
    ratioplot.SetName(hist.GetName()+'_ratio')
    ratioplot.Divide(hist,ref_hist,1.,1.,divide)
    AddHistogram(can.GetPrimitive('pad_top'),hist)
    AddHistogram(can.GetPrimitive('pad_bot'),ratioplot)
