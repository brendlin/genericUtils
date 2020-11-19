from TAxisFunctions import *

##
## New plotting functions :
##
def help() :
    print 'FullFormatCanvasDefault(can,lumi=36.1,sqrts=13,additionaltext='',preliminary=False)'
    print 'ConvertToDifferential(hist)'
    print 'AddHistogram(can,hist)'
    print 'SetAxisLabels(can,xlabel,ylabel)'
    print 'SetColors(can,[color1,color2,color3...])'
    print 'SetMarkerStyles(can,these_styles=[],these_sizes=[])'
    print 'GetLuminosityText(lumi)'
    print 'GetSqrtsText(sqrts)'
    print 'GetAtlasInternalText(status=\'Internal\')'
    print 'DrawText(can,text,x1,y1,x2,y2,...)'
    print 'MakeLegend(can,x1,x2,y1,y2,...)'
    print 'FormatCanvasAxes(can,options...) - must be run AFTER the first histograms are added!'
    print 'SetupStyle()'
    print 'RatioCanvas(name,title,canw,canh,ratio_size_as_fraction)'
    print 'SetLeftMargin(can,margin), SetRightMargin(can,margin)'
    print 'GetTopPad(can), GetBotPad(can)'
    print 'AddHistogramTop(can,hist)'
    print 'AddHistogramBot(can,hist)'
    print 'AddRatio(can,hist,ref_hist)'
    print 'AddRatioManual(can,hist,ratioplot,drawopt1=\'pE1\',drawopt2=\'pE1\')'
    print 'Stack(can,reverse=False)'
    print 'ColorGradient(i,ntotal)'
    print 'SetColorGradient(name=\'MyThermometer\')'
##
## # SetFillStyles() Coming soon!
##

##
## This global list called "tobject_collector" collects TObjects (TH1, TGraph, TLegend, TLatex...)
## that are created in these functions. It is a way of preventing these objects from going out of 
## scope (and thus being deleted) while requiring very little from the user.
##
## IMPORTANT NOTE! If you are using too much memory because of the proliferation of TObjects in this
## list, you can periodically delete them (after you have printed the canvas to pdf) by calling
## del tobject_collector[:]
## in your script. (tobject_collector is a global variable, so this single line is sufficient.)
##
global tobject_collector;
tobject_collector = []

##
## FullFormatCanvasDefault is a collection of functions for easy "1-step" plotting.
##
def FullFormatCanvasDefault(can,lumi=36.1,sqrts=13,additionaltext='',status='Internal') :
    FormatCanvasAxes(can)
    if not can.GetPrimitive('stack') :
        SetColors(can)

    text_lines = []
    text_lines += [GetAtlasInternalText(status)]
    if sqrts and lumi :
        text_lines += [GetSqrtsText(sqrts)+', '+GetLuminosityText(lumi)]
    elif sqrts :
        text_lines += [GetSqrtsText(sqrts)]
    elif lumi :
        text_lines += [GetLuminosityText(lumi)]
    if additionaltext :
        text_lines += [additionaltext]

    if can.GetPrimitive('pad_top') :
        DrawText(can,text_lines,.2,.73,.5,.93,totalentries=3)
        MakeLegend(can,.6,.73,.8,.93,totalentries=3)
    else :
        DrawText(can,text_lines,0.20,0.78,0.5,0.92,totalentries=3)
        MakeLegend(can,.6,.78,.8,.94,totalentries=3)
    AutoFixAxes(can)
    return

##
## Convert a histogram to a differential histogram. Remember to change your y-axis label accordingly
## (e.g. events/GeV)
##
def ConvertToDifferential(hist) :
    hist.Scale(1,'width')
    if ('[GeV]' in hist.GetXaxis().GetTitle()) :
        hist.GetYaxis().SetTitle('%s/GeV'%(hist.GetYaxis().GetTitle()))
    else :
        hist.GetYaxis().SetTitle('%s/(bin width)'%(hist.GetYaxis().GetTitle()))
    return

##
## Add a TH1 or a TGraph to a canvas.
## If a RatioCanvas is specified as the canvas, then the histogram will be added to the top pad
## by default. (To specifically add a canvas to the bottom, do AddHistogram(GetBotPad(can),hist)
## This will *make a copy* of the histogram or graph, so that when you further manipulate the histogram
## in its canvas it will only affect the appearance in this one canvas. This way you
## can add the same histogram to multiple canvases and be able to manipulate the appearance of each
## instance separately.
##
def AddHistogram(can,hist,drawopt='pE1',keepname=False) :
    if can.GetPrimitive('pad_top') :
        return_hist = AddHistogram(can.GetPrimitive('pad_top'),hist,drawopt,keepname)
        return return_hist
    import ROOT
    tmp = hist.Clone()

    use_drawopt_a = issubclass(type(hist),ROOT.TGraph)
    use_same = not use_drawopt_a
    has_GetHistogram = issubclass(type(hist),ROOT.TGraph) or issubclass(type(hist),ROOT.TF1)

    plot_exists = list(issubclass(type(a),ROOT.TH1) for a in can.GetListOfPrimitives())
    plot_exists += list(issubclass(type(a),ROOT.TGraph) for a in can.GetListOfPrimitives())
    plot_exists += list(issubclass(type(a),ROOT.TF1) for a in can.GetListOfPrimitives())
    plot_exists = (True in plot_exists)

    if hasattr(tmp,'SetDirectory') :
        tmp.SetDirectory(0)

    drawopt_orig = drawopt
    if use_same and plot_exists :
        drawopt += 'same'
    if use_drawopt_a and (not plot_exists) :
        drawopt += 'a'

    tobject_collector.append(tmp)
    if not keepname :
        tmp.SetName('%s_%s'%(can.GetName(),hist.GetName()))
    can.cd()
    tmp.Draw(drawopt)
    if has_GetHistogram :
        tmp.GetHistogram().SetOption(drawopt_orig)
    else :
        tmp.SetOption(drawopt_orig)

    can.Modified()
    #can.Update()
    return tmp

##
## Set x- and y-axis labels. Do this *after* you have added your first histogram to the canvas.
##
def SetAxisLabels(can,xlabel,ylabel,yratiolabel='ratio') :
    if 'pad_top' in (a.GetName() for a in can.GetListOfPrimitives()) :
        SetAxisLabels(can.GetPrimitive('pad_bot'),xlabel,yratiolabel)
        SetAxisLabels(can.GetPrimitive('pad_top'),'',ylabel)
    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetXaxis') :
            i.GetXaxis().SetTitle(xlabel)
            differential = ''
            if '/GeV' in i.GetYaxis().GetTitle() :
                differential = '/GeV'
            elif '/(bin width)' in i.GetYaxis().GetTitle() and 'GeV' in i.GetXaxis().GetTitle() :
                differential = '/GeV'
            elif '/(bin width)' in i.GetYaxis().GetTitle() :
                differential = '/(bin width)'
            i.GetYaxis().SetTitle(ylabel+differential)
            break
    can.Modified()
    #can.Update()
    return


def SetMarkerStyles(can,these_styles=[],these_sizes=[]) :
    if not these_styles :
        these_styles = [20 for i in xrange(30)]
                        
    if not these_sizes :
        these_sizes = [1 for i in xrange(30)]

    the_primitives = can.GetListOfPrimitives()
    if can.GetPrimitive('pad_top') :
        the_primitives = can.GetPrimitive('pad_top').GetListOfPrimitives()

    style_count = 0
    for i in the_primitives :
        if hasattr(i,'SetMarkerColor') :
            i.SetMarkerStyle(these_styles[style_count])
            i.SetMarkerSize(these_sizes[style_count])
            #
            # Check if there is a bottom pad, with ratios...
            #
            if can.GetPrimitive('pad_bot') :
                original_name = i.GetName().replace('pad_top_','')
                j = can.GetPrimitive('pad_bot').GetPrimitive('pad_bot_%s_ratio'%(original_name))
                if j :
                    j.SetMarkerStyle(these_styles[style_count])
                    j.SetMarkerSize(these_sizes[style_count])
                    can.GetPrimitive('pad_bot').Modified()
                    #can.GetPrimitive('pad_bot').Update()
            style_count += 1
        if style_count >= len(these_styles) :
            break

    can.Modified()
    #can.Update()
    return


def SetFillStyles(marker_styles=[],marker_sizes=[]) :
    return

def KurtColorPalate() :
    from ROOT import kBlack,kRed,kBlue,kAzure,kGreen,kMagenta,kCyan,kOrange,kGray,kYellow
    return [kBlack+0,kRed+1,kAzure-2,kGreen+1,kMagenta+1,kCyan+1,kOrange+1
            #,kGray,kRed-7,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3
            ,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7
            ,kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5
            ,21,22,23,24,25,26,27,28,29,30
            ,21,22,23,24,25,26,27,28,29,30
            ,21,22,23,24,25,26,27,28,29,30
            ]

##
## Set colors. A default color list is provided, though you can provide your own list.
## Do this *after all of the histograms* have been added to the canvas.
## If you give this function a RatioCanvas, it will make histograms and their corresponding 
## ratio histograms the same color.
##
def SetColors(can,these_colors=[],fill=False,line=False) :

    if can.GetPrimitive('stack') :
        print 'WARNING in PlotFunctions SetColors: canvas has a THStack, but colors must be set'
        print '  before adding to the THStack. Please call SetColors() before calling Stack(). Doing nothing.'
        return

    if not these_colors :
        these_colors = KurtColorPalate()
        
    the_primitives = list(can.GetListOfPrimitives())
    if can.GetPrimitive('pad_top') :
        the_primitives = list(can.GetPrimitive('pad_top').GetListOfPrimitives())

    color_count = 0
    for i in the_primitives :
        if hasattr(i,'SetLineColor') and hasattr(i,'SetMarkerColor') :
            i.SetLineColor(these_colors[color_count])
            i.SetMarkerColor(these_colors[color_count])
            i.SetFillColor(0)
            if fill :
                i.SetFillColor(these_colors[color_count])
                if not line :
                    i.SetLineColor(1)
            #
            # Check if there is a bottom pad, with ratios...
            #
            if can.GetPrimitive('pad_bot') :
                original_name = i.GetName().replace('pad_top_','')
                j = can.GetPrimitive('pad_bot').GetPrimitive('pad_bot_%s_ratio'%(original_name))
                if j :
                    j.SetLineColor(these_colors[color_count])
                    j.SetMarkerColor(these_colors[color_count])
                    j.SetFillColor(0)
                    can.GetPrimitive('pad_bot').Modified()
                    can.GetPrimitive('pad_bot').Update()
            color_count += 1
        if color_count >= len(these_colors) :
            break

    if can.GetPrimitive('pad_top') :
        can.GetPrimitive('pad_top').Modified()
        can.GetPrimitive('pad_top').Update()

    can.Modified()
    can.Update()
    return




##
## Draw luminosity on your plot. Give it the lumi and sqrts.
## The x and y coordinates are the fractional distances, with the origin at the bottom left.
##
def GetLuminosityText(lumi=20.3) :
    unit = 'fb'
    if lumi < 1 :
        unit = 'pb'
        lumi = lumi * 1000.

    # Version with int Ldt:
    #return '#lower[-0.2]{#scale[0.60]{#int}}Ldt = %1.1f %s^{#minus1}'%(lumi,unit)

    if unit == 'fb' and lumi > 100 :
        return '%d %s^{#minus1}'%(int(lumi),unit)

    return '%1.1f %s^{#minus1}'%(lumi,unit)

def GetSqrtsText(sqrts=13) :
    return '#sqrt{s} = %d TeV'%(sqrts)

def GetAtlasInternalText(status='Internal') :
    return '#font[72]{ATLAS} #font[42]{%s}'%(status)
    
##
## Draw some additional text on your plot, in the form of a TLegend (easier to manage)
## The x and y coordinates are the fractional distances, with the origin at the bottom left.
## Specify multi-lines by specifing a list ['line1','line2','line3'] instead of a string 'single line'.
##
def DrawText(can,text='text',x1=None,y1=None,x2=None,y2=None,angle=0,align='',textsize=18,totalentries=1) :

    if x1 == None : x1 = 0.2
    if x2 == None : x2 = 0.5

    if can.GetPrimitive('pad_top') :
        if y1 == None : y1 = 0.73
        if y2 == None : y2 = 0.93
    else :
        if y1 == None : y1 = 0.78
        if y2 == None : y2 = 0.94

    can.cd()
    if can.GetPrimitive('pad_top') :
        can.GetPrimitive('pad_top').cd()
    from ROOT import TLegend
    leg = TLegend(x1,y1,x2,y2)
    leg.SetMargin(0)
    leg.SetName(can.GetName()+'_text')
    tobject_collector.append(leg)
    leg.SetTextSize(textsize)
    leg.SetTextFont(43)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    if type(text) == type('') :
        text = [text]
    total = 0
    for i in text :
        leg.AddEntry(0,i,'')
        total += 1
    while (total < totalentries) :
        leg.AddEntry(0,'','')
        total += 1
    leg.Draw()
    can.Modified()
    #can.Update()
    return

def CanvasEmpty(can) :
    from ROOT import TH1,TGraph
    is_th1 = list(issubclass(type(i),TH1) for i in can.GetListOfPrimitives())
    is_tgr = list(issubclass(type(i),TGraph) for i in can.GetListOfPrimitives())
    if not (True in is_th1+is_tgr) :
        return True
    return False

##
## The MakeLegend function looks for any TH1 or TGraph you added to your canvas, and puts them
## in a legend in the order that you added them to a canvas.
## The entry label is taken from the title of the TH1 or TGraph. *Be sure to set the title
## of your TH1 or TGraph *before* you add it to the canvas.*
## The x and y coordinates are the fractional distances, with the origin at the bottom left.
## 
def MakeLegend(can,x1=None,y1=None,x2=None,y2=None,textsize=18,ncolumns=1,totalentries=3,option=None,skip=[],extend=False,order=[]) :

    import ROOT

    if x1 == None : x1 = 0.6
    if x2 == None : x2 = 0.8

    if can.GetPrimitive('pad_top') :
        if y1 == None : y1 = 0.73
        if y2 == None : y2 = 0.93
    else :
        if y1 == None : y1 = 0.78
        if y2 == None : y2 = 0.94

    if can.GetPrimitive('pad_top') :
        MakeLegend(can.GetPrimitive('pad_top'),x1,y1,x2,y2,textsize,ncolumns,totalentries,option,skip=skip,extend=extend)
        return
    if CanvasEmpty(can) :
        print 'Error: trying to make legend from canvas with 0 plots. Will do nothing.'
        return
    #
    # if a previous version exists from this function, delete it
    #
    if can.GetPrimitive('legend') :
        can.GetPrimitive('legend').Delete()
    leg = ROOT.TLegend(x1,y1,x2,y2)
    leg.SetName('legend')
    tobject_collector.append(leg)
    leg.SetTextFont(43)
    leg.SetTextSize(textsize)
    leg.SetTextFont(43)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetNColumns(ncolumns)
    #
    # Add by TH1 GetTitle()
    #
    the_primitives = can.GetListOfPrimitives()
    if can.GetPrimitive('pad_top') :
        the_primitives = can.GetPrimitive('pad_top').GetListOfPrimitives()
    if can.GetPrimitive('stack') :
        the_stack = list(can.GetPrimitive('stack').GetHists())
        the_primitives = the_stack+list(the_primitives)

    if order :
        tmp = []
        for i in order :
            tmp.append(the_primitives[i])
        the_primitives = tmp

    total = 0
    for i in the_primitives :
        if 'stack' in i.GetTitle() :
            continue
        if 'remove' in i.GetTitle() :
            continue
        if (not issubclass(type(i),ROOT.TH1)) and (not issubclass(type(i),ROOT.TGraph)) and (not issubclass(type(i),ROOT.TF1)) :
            continue
        if i.GetTitle() in skip :
            continue

        drawopt = i.GetOption().replace('same','').replace('hist','l').replace('E2','f')
        if issubclass(type(i),ROOT.TGraph) :
            drawopt = i.GetHistogram().GetOption().replace('same','').replace('hist','l')
        if issubclass(type(i),ROOT.TF1) :
            drawopt = i.GetHistogram().GetOption().replace('same','').replace('hist','l')
        if (type(option) == type([])) and len(option) > total :
            drawopt = option[total]
        if (type(option) == type('')) :
            drawopt = option
        if not drawopt and issubclass(type(i),ROOT.TH1) :
            drawopt = 'f'
        if not drawopt and issubclass(type(i),ROOT.TGraph) :
            drawopt = 'p'

        # print '%s: drawopt \"%s\"'%(i.GetName(),drawopt)
        leg.AddEntry(i,'^{ }'+i.GetTitle(),drawopt) # plef
        total += 1

    #
    # Add empty entries to ensure a standard layout
    #            
    while (total < totalentries) :
        leg.AddEntry(0,'','')
        total += 1

    # if the option is set, extend the legend downward to accommodate more entries
    if (total > totalentries) and extend :
        leg.SetY1(leg.GetY2() - total*(leg.GetY2() - leg.GetY1())/float(totalentries) )

    # recipe for making roughly square boxes
    h = leg.GetY2()-leg.GetY1()
    w = leg.GetX2()-leg.GetX1()
    h_can = can.GetWh()
    w_can = can.GetWw()
    h_pad = can.GetAbsHNDC()
    w_pad = can.GetAbsWNDC()
    leg.SetMargin(leg.GetNColumns()*h*h_can*h_pad/float(leg.GetNRows()*w*w_can*w_pad))
    can.cd()
    if can.GetPrimitive('pad_top') :
        can.GetPrimitive('pad_top').cd()
    leg.Draw()
    can.Modified()
    can.Update()
    return

##
## Format the axes of your canvas or RatioCanvas, including axis labels, sizes, offsets. 
## Call this *after* one or more histograms have been added to the canvas.
##
def FormatCanvasAxes(can
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
                     ,YNDiv = [10,5,0]
                     
                     ,ZTitleSize   = 22
                     ,ZTitleOffset = 0.85
                     ,ZTitleFont   = 43
                     ,ZLabelSize   = 22
                     ,ZLabelOffset = 0.006
                     ,ZLabelFont   = 43
                     ) :

    if can.GetPrimitive('pad_top') :
        FormatCanvasAxes(can.GetPrimitive('pad_top'),XLabelOffset=0.1
                         ,XTitleSize=XTitleSize,XTitleOffset=XTitleOffset,XTitleFont=XTitleFont
                         ,XLabelSize=XLabelSize,XLabelFont=XLabelFont
                         ,YTitleSize=YTitleSize,YTitleOffset=YTitleOffset,YTitleFont=YTitleFont
                         ,YLabelSize=YLabelSize,YLabelOffset=YLabelOffset,YLabelFont=YLabelFont
                         ,YNDiv=YNDiv
                         ,ZTitleSize=ZTitleSize,ZTitleOffset=ZTitleOffset,ZTitleFont=ZTitleFont
                         ,ZLabelSize=ZLabelSize,ZLabelOffset=ZLabelOffset,ZLabelFont=ZLabelFont
                         )
    if can.GetPrimitive('pad_bot') :
        FormatCanvasAxes(can.GetPrimitive('pad_bot'),YLabelOffset=0.009
                         ,XTitleSize=XTitleSize,XTitleOffset=XTitleOffset,XTitleFont=XTitleFont
                         ,XLabelSize=XLabelSize,XLabelOffset=XLabelOffset,XLabelFont=XLabelFont
                         ,YTitleSize=YTitleSize,YTitleOffset=YTitleOffset,YTitleFont=YTitleFont
                         ,YLabelSize=YLabelSize,YLabelFont=YLabelFont
                         ,YNDiv = [5,5,0]
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
    #can.Update()
    return

##
## Setup general style.
##
def SetupStyle() :
    import ROOT
    from array import array

    mystyle = ROOT.TStyle("mystyle","mystyle")
    mystyle.SetTextFont(42)
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
    #mystyle.SetLineWidth(2) # no
    mystyle.SetFrameFillColor(0)
    mystyle.SetOptTitle(0)
    mystyle.SetPaintTextFormat('4.1f ')
    mystyle.SetEndErrorSize(0)

    # For top (x) / right (y) ticks
    mystyle.SetPadTickX(1)
    mystyle.SetPadTickY(1)

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
    mystyle.SetLabelOffset(0.006,'y')
    mystyle.SetNdivisions(510,'y') # n1 = 10, n2 = 5, n3 = 0 -> 00 05 10 = 510

    # z axis
    mystyle.SetTitleOffset(0.85,'z')
    mystyle.SetLabelOffset(0.006,'z')

    # Legend
    mystyle.SetLegendTextSize(18)
    mystyle.SetLegendFont(43)
    mystyle.SetLegendFillColor(0)
    mystyle.SetLegendBorderSize(0)
    
    mystyle.SetNumberContours(255)
    SetColorGradient('Grayscale')

    ROOT.gROOT.SetStyle("mystyle")

    return mystyle

##
## Call this if you want a TCanvas especially prepared for ratio plots. It creates two
## sub-pads, "pad_top" and "pad_bot", and the rest of the functions in this file will
## specifically look for this type of configuration and act accordingly. See also the special
## functions GetTopPad(can) and GetBotPad(can) if you want to manipulate the sub-pads yourself.
## To add histograms to the top pad, do AddHistogram(can,hist) or AddHistogramTop(can,hist)
## To add histograms to the bot pad, do AddHistogramBot(can,hist).
## To add a histogram to the top pad, and its ratio with a reference histogram to the bottom pad,
## do AddRatio(can,hist,ref_hist,'B') (the B is for binomial errors).
##
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
    bot.SetBottomMargin(0.11/float(bot.GetHNDC()))
    bot.SetTopMargin   (0.02/float(bot.GetHNDC()))
    bot.SetRightMargin (0.05)
    bot.SetLeftMargin  (0.16)
    bot.SetFillColor(0)
    bot.Draw()
    tobject_collector.append(bot)
    
    return c

##
## Set the left margin - useful for the RatioCanvas in particular (since it will handle sub-pads)
##
def SetLeftMargin(can,margin) :
    if can.GetPrimitive('pad_top') :
        SetLeftMargin(can.GetPrimitive('pad_top'),margin)
    if can.GetPrimitive('pad_bot') :
        SetLeftMargin(can.GetPrimitive('pad_bot'),margin)
    can.SetLeftMargin(margin)
    can.Modified()
    can.Update()
    return

##
## Set the right margin - useful for the RatioCanvas in particular (since it will handle sub-pads)
##
def SetRightMargin(can,margin) :
    if can.GetPrimitive('pad_top') :
        SetRightMargin(can.GetPrimitive('pad_top'),margin)
    if can.GetPrimitive('pad_bot') :
        SetRightMargin(can.GetPrimitive('pad_bot'),margin)
    can.SetRightMargin(margin)
    can.RedrawAxis()
    can.Modified()
    can.Update()
    return

##
## Return a pointer to the top pad of a RatioCanvas
##
def GetTopPad(can) :
    return can.GetPrimitive('pad_top')

##
## Return a pointer to the bottom pad of a RatioCanvas
##
def GetBotPad(can) :
    return can.GetPrimitive('pad_bot')

##
## Add a TH1 or TGraph to the top pad of a RatioCanvas
##
def AddHistogramTop(can,hist,drawopt='pE1') :
    AddHistogram(can.GetPrimitive('pad_top'),hist,drawopt)
    return

##
## Add a TH1 or TGraph to the bottom pad of a RatioCanvas
##
def AddHistogramBot(can,hist,drawopt='pE1') :
    AddHistogram(can.GetPrimitive('pad_bot'),hist,drawopt)
    return

##
## Adds a histogram to the top pad of a RatioCanvas, and a ratio (dividing by some reference
## histogram ref_hist) to the bottom pad of the RatioCanvas. Specify the division type
## by the "divide" option ("B" for binomial, "" for uncorrelated histograms)
##
def AddRatio(can,hist,ref_hist,divide='',drawopt='pE1') :
    import ROOT
    import math
    ROOT.TH1.SetDefaultSumw2(True)
    ratioplot = hist.Clone()
    ratioplot.SetName(hist.GetName()+'_ratio')
    if issubclass(type(hist),ROOT.TGraph) :
        ratioplot.GetYaxis().SetTitle('ratio')
        for i in range(ratioplot.GetN()) :
            if ref_hist.GetY()[i] == 0 : continue
            ratioplot.SetPoint(i,hist.GetX()[i],hist.GetY()[i]/float(ref_hist.GetY()[i]))
    else :
        if divide == 'pull' :
            ratioplot.GetYaxis().SetTitle('pull')
            for i in range(ratioplot.GetNbinsX()+2) :
                bc1 = hist.GetBinContent(i)
                bc2 = ref_hist.GetBinContent(i)
                be1 = hist    .GetBinErrorLow(i) if (bc1 > bc2) else hist    .GetBinErrorUp(i)
                be2 = ref_hist.GetBinErrorLow(i) if (bc2 > bc1) else ref_hist.GetBinErrorUp(i)

                if (be1**2 + be2**2) :
                    ratioplot.SetBinContent(i,(bc1-bc2)/math.sqrt(be1**2+be2**2))
                ratioplot.SetBinError(i,1)
        else :
            ratioplot.GetYaxis().SetTitle('ratio')
            ratioplot.Divide(hist,ref_hist,1.,1.,divide)

    return_hist = AddHistogram(can.GetPrimitive('pad_top'),hist,drawopt=drawopt)
    return_ratio = AddHistogram(can.GetPrimitive('pad_bot'),ratioplot,drawopt=drawopt)
    return return_hist, return_ratio

def AddRatioManual(can,hist,ratioplot,drawopt1='pE1',drawopt2='pE1') :
    ratioplot.SetName(hist.GetName()+'_ratio')
    return_hist = AddHistogram(can.GetPrimitive('pad_top'),hist,drawopt=drawopt1)
    return_ratio = AddHistogram(can.GetPrimitive('pad_bot'),ratioplot,drawopt=drawopt2)
    return return_hist, return_ratio

##
## Stack plot functionality
##
def Stack(can,reverse=False) :
    if can.GetPrimitive('pad_top') :
        return Stack(can.GetPrimitive('pad_top'),reverse=reverse)
    
    from ROOT import TH1,THStack
    stack = THStack('stack','stack')
    xaxislabel,yaxislabel = '',''
    binlabels = []
    if reverse :
        the_primitives = reversed(can.GetListOfPrimitives())
    else :
        the_primitives = can.GetListOfPrimitives()
    for i in the_primitives :
        if issubclass(type(i),TH1) :
            stack.Add(i)
            if not xaxislabel : xaxislabel = i.GetXaxis().GetTitle()
            if not yaxislabel : yaxislabel = i.GetYaxis().GetTitle()
            if not binlabels and i.GetXaxis().GetBinLabel(1) :
                for j in range(i.GetNbinsX()) :
                    binlabels.append(i.GetXaxis().GetBinLabel(j+1))
    # The original objects are cleared from the histogram:
    can.Clear()
    tobject_collector.append(stack)

    # Set draw option of underlying histograms for automatically nice legends
    for hist in stack.GetHists() :
        hist.SetOption('f')

    can.cd()
    stack.Draw('hist')
    stack.GetXaxis().SetTitle(xaxislabel)
    stack.GetYaxis().SetTitle(yaxislabel)
    if binlabels :
        for i in range(stack.GetXaxis().GetNbins()) :
            stack.GetXaxis().SetBinLabel(i+1,binlabels[i])
    can.RedrawAxis()
    can.Modified()
    can.Update()
    return

def ColorGradient(i,ntotal) :
    import ROOT
    if ntotal == 1 :
        return ROOT.kBlack

    NCont = 255
    ROOT.gStyle.SetNumberContours(NCont)
    the_int = int((NCont-1)*i/float(ntotal-1))
    return ROOT.gStyle.GetColorPalette(the_int)

def SetColorGradient(name='MyThermometer',mystyle = None) :

    import ROOT
    from array import array
    NCont = 255
    ROOT.gStyle.SetNumberContours(255)

    if name == 'MyThermometer' :
        # Blue -> Red (but it doesn't go through white)
        stops = array('d',[ 0.00,1.00 ])
        red   = array('d',[ 0.10,0.90 ])
        green = array('d',[ 0.10,0.10 ])
        blue  = array('d',[ 1.00,0.10 ])

    if name == 'HiggsBlue' :
        # Higgs white -> Blue
        stops = array('d',[ 0.00,1.00 ])
        red   = array('d',[ 1.00,0.50 ])
        green = array('d',[ 1.00,0.50 ])
        blue  = array('d',[ 1.00,1.00 ])

    if name == 'Grayscale' :
        # Higgs white -> Blue
        stops = array('d',[ 0.00,1.00 ])
        red   = array('d',[ 1.00,0.00 ])
        green = array('d',[ 1.00,0.00 ])
        blue  = array('d',[ 1.00,0.00 ])

    if name == 'DarkRainbow' :
        stops = array('d',[0.00, 0.34, 0.61, 0.84, 1.00])
        red   = array('d',[0.00, 0.00, 0.87, 1.00, 0.51])
        green = array('d',[0.00, 0.81, 1.00, 0.20, 0.00])
        blue  = array('d',[0.51, 1.00, 0.12, 0.00, 0.00])

    if name == 'Rainbow' :
        stops = array('d',[0.00, 0.50, 1.00])
        red   = array('d',[0.00, 0.50, 1.00])
        green = array('d',[0.00, 1.00, 0.00])
        blue  = array('d',[1.00, 0.50, 0.00])

    ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, NCont)
    return
