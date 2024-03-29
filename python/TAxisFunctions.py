##
## Available functions:
##
def help() :
    print('AutoFixAxes(can,symmetrize=False,ignorelegend=False)')
    print('AutoFixYaxis(can,ignorelegend=False,forcemin=None,minzero=False,ignorezero=False)')
    print('EqualizeYAxes(cans,ignorelegend=False)')
    print()
    print('FixYaxisRanges(can)')
    print('SetYaxisRanges(can,ymin,ymax)')
    print('GetYaxisRanges(can,check_all=False,ignorezero=False)')
    print()
    print('FixXaxisRanges(can)')
    print('SetXaxisRanges(can,xmin,xmax)')
    print('GetXaxisRanges(can,check_all=False)')
## 
## Smaller, helpers:
##  NearestNiceNumber(miny,maxy)
##  MinimumForLog(can)
##  SetNdivisions(can,a,b,c)
##  SetYaxisNdivisions(can,a,b,c)
##  

##
## This function will fit all of the histgram bin content, or TGraph points on a plot.
## If a text or legend has been added to the plot it will force the plot content to appear BELOW
## the text.
##
def AutoFixAxes(can,symmetrize=False,ignorelegend=False,ignorezero=False,ignoretext=False) :
    if can.GetPrimitive('pad_top') :
        AutoFixAxes(can.GetPrimitive('pad_top'),ignorelegend=ignorelegend,ignorezero=ignorezero,ignoretext=ignoretext)
        AutoFixAxes(can.GetPrimitive('pad_bot'),ignorelegend=ignorelegend,ignorezero=ignorezero,ignoretext=ignoretext)
        return
    FixXaxisRanges(can)    
    AutoFixYaxis(can,ignorelegend=ignorelegend,ignorezero=ignorezero,ignoretext=ignoretext)
    return

def AutoFixYaxis(can,ignorelegend=False,forcemin=None,minzero=False,ignorezero=False,ignoretext=False) :
    #
    # Makes space for text as well!
    #
    import ROOT
    import math
    import sys
    can.Update()

    miny,maxy = sys.float_info.max,sys.float_info.min

    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),ROOT.TH2) :
            print('Warning: AutoFixYaxis for a 2d plot. Skipping for this canvas.')
            return miny,maxy

    # maxy_frac is the fractional maximum of the y-axis stuff.
    maxy_frac = 1
    #
    # Now we make space for any text we drew on the canvas, and
    # also the Legend
    #
    plots_exist = False
    tframe_height = 1-can.GetTopMargin()-can.GetBottomMargin()
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),ROOT.TH1) :
            plots_exist = True
        if issubclass(type(i),ROOT.TF1) :
            plots_exist = True
        if issubclass(type(i),ROOT.TGraph) :
            plots_exist = True
        if (ignorelegend) and issubclass(type(i),ROOT.TLegend) and 'legend' in i.GetName() :
            continue
        if (ignoretext) and issubclass(type(i),ROOT.TLegend) and '_text' in i.GetName() :
            continue
        if type(i) == type(ROOT.TFrame()) :
            continue
        if hasattr(i,'GetY1NDC') :
            maxy_frac = min(maxy_frac,i.GetY1NDC())
        if hasattr(i,'GetY') :
            maxy_frac = min(maxy_frac,i.GetY())
    if not plots_exist :
        print('Your plot %s has nothing in it. AutoFixYaxis() is Doing nothing.'%(can.GetName()))
        return  miny,maxy
    (miny,maxy) = GetYaxisRanges(can,check_all=True,ignorezero=ignorezero)
    # print('AutoFixAxes0',miny,maxy)
    if miny == 0 and maxy == 0 :
        return miny,maxy
    miny = (0.95*miny) if (miny>0) else (1.05*miny)
    maxy = (1.05*maxy) if (maxy>0) else (0.95*maxy)
    maxy_frac = maxy_frac-can.GetBottomMargin()

    if maxy_frac < 0 :
        print('Error in AutoFixAxes - somehow there is no more room for your plot.')
        print('(Bad legend placement?)')
        return miny,maxy

    if can.GetLogy() and MinimumForLog(can) > 0 :
        # special treatment for log plots
        miny = 0.85*MinimumForLog(can)
        # some orders of magnitude *above* miny, making room for text
        orderofmagnitude_span = math.log(maxy/miny)/math.log(10)
        orderofmagnitude_span = 1.1*orderofmagnitude_span*tframe_height/maxy_frac
        maxy = miny*math.pow(10,orderofmagnitude_span)
    else :
        # scale to make space for text
        maxy_frac = maxy_frac-.02
        maxy = tframe_height*(maxy-miny)/float(maxy_frac)+miny
        # round y axis to nice round numbers
        (miny,maxy) = NearestNiceNumber(miny,maxy)
    # print('AutoFixAxes',miny,maxy)
#     if symmetrize :
#         (miny,maxy) = -max(math.fabs(miny),math.fabs(maxy)),max(math.fabs(miny),math.fabs(maxy))
    if minzero == True :
        miny = 0
    if forcemin :
        miny = forcemin
    SetYaxisRanges(can,miny,maxy)
    return miny,maxy

##
## Snap to base-ten-centric numbers
##
def NearestNiceNumber(miny,maxy) :
    import math
    round_number = 10 # or 5 perhaps
    smallest_increment = pow(10,math.floor(math.log((maxy-miny))/math.log(10))-2)
    if miny > 0 :
        newminy = round_number*smallest_increment*       int(miny/(round_number*smallest_increment))
    else :
        newminy = round_number*smallest_increment*math.floor(miny/(round_number*smallest_increment))
    newmaxy     = round_number*smallest_increment*math.ceil (maxy/(round_number*smallest_increment))
    # print('NearestNiceNumber',newminy,newmaxy)
    return newminy,newmaxy

##
## Find the non-zero y-axis minimum of plot content.
##
def MinimumForLog(can) :
    from ROOT import TGraph,TH1,TMath,THStack
    import sys
    ymin = sys.float_info.max
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            for ii in range(i.GetN()) :
                y = i.GetY()[ii]
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
        if issubclass(type(i),TH1) :
            for bin in range(i.GetNbinsX()) :
                y = i.GetBinContent(bin+1)
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
        if issubclass(type(i),THStack) :
            j = i.GetHists()[0]
            for bin in range(j.GetNbinsX()) :
                y = j.GetBinContent(bin+1)
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
    # print('MinimumForLog',ymin)
    if ymin == sys.float_info.max :
        print('Error! Trying to use Logy but y minimum is zero! Returning -1')
        return -1
    return ymin

##
## Fit all the data into the canvas (for the y-axis)
##
def FixYaxisRanges(can) :
    (ymin,ymax) = GetYaxisRanges(can,check_all=True)
    SetYaxisRanges(can,ymin,ymax)
    return ymin,ymax

##
## Set the x-axis ranges of a canvas
##
def SetYaxisRanges(can,ymin,ymax) :
    if can.GetPrimitive('pad_top') :
        SetYaxisRanges(can.GetPrimitive('pad_top'),ymin,ymax)
        return
    import ROOT
    yaxis = 0
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),ROOT.TGraph) :
            # print('SetYaxisRanges',ymin,ymax)
            i.SetMinimum(ymin)
            i.SetMaximum(ymax)
            if not yaxis :
                yaxis = i.GetHistogram().GetYaxis()
        if issubclass(type(i),ROOT.TF1) :
            # print('SetYaxisRanges',ymin,ymax)
            i.SetMinimum(ymin)
            i.SetMaximum(ymax)
            if not yaxis:
                yaxis = i.GetHistogram().GetYaxis()
        if issubclass(type(i),ROOT.TH1) :
            # print('SetYaxisRanges',ymin,ymax)
            i.SetMinimum(ymin)
            i.SetMaximum(ymax)
            if not yaxis:
                yaxis = i.GetYaxis()
        if issubclass(type(i),ROOT.THStack) :
            # print('SetYaxisRanges',ymin,ymax)
            i.SetMinimum(ymin)
            i.SetMaximum(ymax)
            if not yaxis :
                yaxis = i.GetHistogram().GetYaxis()
    if not yaxis :
        print('Warning: SetYaxisRange had no effect. Check that your canvas has plots in it.')
        return
    
    yaxis.SetRangeUser(ymin,ymax)
    can.Modified()
    can.Update()
    return

def SetNdivisions(can,a,b,c) :
    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetXaxis') :
            i.GetXaxis().SetNdivisions(a,b,c)
    can.Modified()
    can.Update()
    return

def SetYaxisNdivisions(can,a,b,c) :
    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetYaxis') :
            i.GetYaxis().SetNdivisions(a,b,c)
    can.Modified()
    can.Update()
    return

def SetYaxisProperty(can,property,*args) :
    if can.GetPrimitive('pad_top') :
        SetYaxisProperty(can.GetPrimitive('pad_top'),property,*args)
        SetYaxisProperty(can.GetPrimitive('pad_bot'),property,*args)

    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetYaxis') :
            axis = i.GetYaxis()
            getattr(axis,property)(*args)
    can.Modified()
    can.Update()
    return

def SetXaxisProperty(can,property,*args) :
    if can.GetPrimitive('pad_top') :
        SetXaxisProperty(can.GetPrimitive('pad_top'),property,*args)
        SetXaxisProperty(can.GetPrimitive('pad_bot'),property,*args)

    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetXaxis') :
            axis = i.GetXaxis()
            getattr(axis,property)(*args)

    can.Modified()
    can.Update()
    return

##
## Returns the y-range of the first plotted histogram.
## If you specify "check_all=True", returns the maximal y-range of all the plots in the canvas
##
def GetYaxisRanges(can,check_all=False,ignorezero=False) :
    #
    # check_all is if you want to check the maximum extent of all the histograms you plotted.
    #
    import ROOT
    import sys
    ymin = sys.float_info.max
    ymax = sys.float_info.min
    
    primitives = list(can.GetListOfPrimitives())
    if can.GetPrimitive('stack') :
        the_stack = list(can.GetPrimitive('stack').GetHists())
        primitives += the_stack

    for i in primitives :
        if issubclass(type(i),ROOT.TGraph) :
            tmp_ymin = None
            tmp_ymax = None
            for j in range(i.GetN()) :
                eyl = 0
                eyh = 0
                if issubclass(type(i),ROOT.TGraphAsymmErrors) :
                    eyl = i.GetEYlow()[j]
                    eyh = i.GetEYhigh()[j]
                elif issubclass(type(i),ROOT.TGraphErrors) :
                    eyl = i.GetEY()[j]
                    eyh = i.GetEY()[j]
                if tmp_ymin == None :
                    tmp_ymin = i.GetY()[j]-eyl
                    tmp_ymax = i.GetY()[j]+eyh
                    continue
                tmp_ymin = min(tmp_ymin,i.GetY()[j]-eyl)
                tmp_ymax = max(tmp_ymax,i.GetY()[j]+eyh)
            ymin = min(ymin,tmp_ymin)
            ymax = max(ymax,tmp_ymax)
            if not check_all :
                return ymin,ymax
        if issubclass(type(i),ROOT.TH1) :
            for bin in range(i.GetNbinsX()) :
                if bin+1 < i.GetXaxis().GetFirst() : continue # X-axis SetRange should be done first
                if bin+1 > i.GetXaxis().GetLast() : continue # X-axis SetRange should be done first
                y = i.GetBinContent(bin+1)
                yel = i.GetBinErrorLow(bin+1)
                yeu = i.GetBinErrorUp(bin+1)
                if ignorezero and y == 0 and yel == 0 and yeu == 0 :
                    continue
                ymin = min(ymin,y-yel)
                ymax = max(ymax,y+yeu)
            if not check_all :
                return ymin,ymax
        if issubclass(type(i),ROOT.TF1) :
            ymin = min(ymin,i.GetMinimum())
            ymax = max(ymax,i.GetMaximum())
            if not check_all :
                return ymin,ymax            
        if issubclass(type(i),ROOT.THStack) :
            ymin = min(ymin,i.GetMinimum())
            ymax = max(ymax,i.GetMaximum())
            if not check_all :
                return ymin,ymax

    # print('GetYaxisRanges',ymin,ymax)
    return ymin,ymax

##
## Fit all the data into the canvas (for the x-axis)
##
def FixXaxisRanges(can) :
    (xmin,xmax) = GetXaxisRanges(can,check_all=True)
    SetXaxisRanges(can,xmin,xmax)
    return

##
## Set the x-axis ranges of a canvas
##
def SetXaxisRanges(can,xmin,xmax) :
    if can.GetPrimitive('pad_top') :
        SetXaxisRanges(can.GetPrimitive('pad_top'),xmin,xmax)
        SetXaxisRanges(can.GetPrimitive('pad_bot'),xmin,xmax)
        return
    from ROOT import TGraph,TH1,THStack
    xaxis = 0
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            xaxis = i.GetXaxis()
            xaxis.SetLimits(xmin,xmax)
        if issubclass(type(i),TH1) :
            xaxis = i.GetXaxis()
            xaxis.SetRangeUser(xmin,xmax)
        if issubclass(type(i),THStack) :
            xaxis = i.GetXaxis()
            xaxis.SetRangeUser(xmin,xmax)
    
    if not xaxis :
        print('Warning: SetXaxisRange had no effect. Check that your canvas has plots in it.')
        return

    can.Modified()
    can.Update()
    return

##
## Returns the x-range of the first plotted histogram.
## If you specify "check_all=True", returns the maximal x-range of all the plots in the canvas
##
def GetXaxisRanges(can,check_all=False) :
    if can.GetPrimitive('pad_top') :
        xmintop,xmaxtop = GetXaxisRanges(can.GetPrimitive('pad_top'))
        xminbot,xmaxbot = GetXaxisRanges(can.GetPrimitive('pad_bot'))
        return min(xmintop,xminbot),max(xmaxtop,xmaxbot)

    import ROOT
    xmin = 999999999
    xmax = -999999999
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),ROOT.TGraph) :
            xaxis = i.GetHistogram().GetXaxis()
            if not check_all :
                return xaxis.GetXmin(),xaxis.GetXmax()
            xmin = min(xmin,xaxis.GetXmin())
            xmax = max(xmax,xaxis.GetXmax())
        if issubclass(type(i),ROOT.TH1) :
            xaxis = i.GetXaxis()
            if not check_all :
                return xaxis.GetXmin(),xaxis.GetXmax()
            xmin = min(xmin,xaxis.GetXmin())
            xmax = max(xmax,xaxis.GetXmax())
    return xmin,xmax

##
## Puts the overflow into the last bin
##
def PutOverflowIntoLastBin(hist,high=None) :
    import math

    high_quantized = high

    if high_quantized == None :
        high_quantized = hist.GetXaxis().GetBinLowEdge(hist.GetNbinsX()+1)

    last_bin = hist.GetXaxis().FindBin(high_quantized)-1
    high_quantized = hist.GetXaxis().GetBinLowEdge(last_bin+1)

    for i in range(hist.GetNbinsX()+1) :
        if hist.GetXaxis().GetBinLowEdge(i+1) >= high_quantized :
            hist.SetBinContent(last_bin,hist.GetBinContent(i+1)+hist.GetBinContent(last_bin))
            hist.SetBinError(last_bin,math.sqrt(hist.GetBinError(i+1)**2 + hist.GetBinError(last_bin)**2))
            hist.SetBinContent(i+1,0)
            hist.SetBinError(i+1,0)
    return

##
## Puts the underflow into the first bin
##
def PutUnderflowIntoFirstBin(hist,low=None) :
    import math

    low_quantized = low

    if low_quantized == None :
        low_quantized = hist.GetXaxis().GetBinLowEdge(1)

    first_bin = hist.GetXaxis().FindBin(low_quantized)
    low_quantized = hist.GetXaxis().GetBinLowEdge(first_bin)

    for i in range(hist.GetNbinsX()+1) :

        if hist.GetXaxis().GetBinLowEdge(i+1) <= low_quantized :
            hist.SetBinContent(first_bin,hist.GetBinContent(i)+hist.GetBinContent(first_bin))
            hist.SetBinError(first_bin,math.sqrt(hist.GetBinError(i)**2 + hist.GetBinError(first_bin)**2))
            hist.SetBinContent(i,0)
            hist.SetBinError(i,0)

    return

def EqualizeYAxes(cans,ignorelegend=False,minzero=False,ignoretext=False) :
    import sys
    miny,maxy = sys.float_info.max,sys.float_info.min
    for can in cans :
        tmp_miny,tmp_maxy = AutoFixYaxis(can,ignorelegend=ignorelegend,ignorezero=True,minzero=minzero,ignoretext=ignoretext)
        miny,maxy = min(miny,tmp_miny),max(maxy,tmp_maxy)
    for can in cans :
        SetYaxisRanges(can,miny,maxy)
    return miny,maxy
