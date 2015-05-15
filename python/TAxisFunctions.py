
def AutoFixAxes(can) :
    from ROOT import TFrame
    FixXaxisRanges(can)
    FixYaxisRanges(can)
    maxy_frac = 1
    #
    # Now we make space for any text we drew on the canvas, and
    # also the Legend
    #
    for i in can.GetListOfPrimitives() :
        if type(i) == type(TFrame()) :
            continue
        if hasattr(i,'GetY') :
            maxy_frac = min(maxy_frac,i.GetY())
        if hasattr(i,'GetY1') :
            maxy_frac = min(maxy_frac,i.GetY1())
    tmp = GetYaxisRanges(can,check_all=True)
    miny = tmp[0]
    maxy = tmp[1]/float(maxy_frac)
    #
    # Special treatment for log plots!
    #
    if can.GetLogy() :
        miny = 0.4*MinimumForLog(can)
        maxy = pow(tmp[1],1/float(maxy_frac))
    SetYaxisRanges(can,miny,maxy)
    return

def MinimumForLog(can) :
    from ROOT import TGraph,TH1,TMath
    ymin = 999999999
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            for y in i.GetY() :
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
        if issubclass(type(i),TH1) :
            for bin in range(i.GetNbinsX()) :
                y = i.GetBinContent(bin+1)
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
    return ymin

def FixYaxisRanges(can) :
    tmp = GetYaxisRanges(can,check_all=True)
    ymin = tmp[0]
    ymax = tmp[1]
    SetYaxisRanges(can,ymin,ymax)
    return

def SetYaxisRanges(can,ymin,ymax) :
    from ROOT import TGraph,TH1
    yaxis = 0
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            yaxis = i.GetHistogram().GetYaxis()
            break
        if issubclass(type(i),TH1) :
            yaxis = i.GetYaxis()
            break
    yaxis.SetRangeUser(ymin,ymax)
    can.Modified()
    can.Update()
    return

def GetYaxisRanges(can,check_all=False) :
    #
    # check_all is if you want to check the maximum extent of all the histograms you plotted.
    #
    from ROOT import TGraph,TH1,TMath
    ymin = 999999999
    ymax = -999999999
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            ymin = min(ymin,TMath.MinElement(i.GetN(),i.GetY()))
            ymax = max(ymax,TMath.MaxElement(i.GetN(),i.GetY()))
            if not check_all :
                return [ymin,ymax]
        if issubclass(type(i),TH1) :
            ymin = min(ymin,i.GetMinimum())
            ymax = max(ymax,i.GetMaximum())
            if not check_all :
                return [ymin,ymax]
    return [ymin,ymax]

def FixXaxisRanges(can) :
    tmp = GetXaxisRanges(can,check_all=True)
    xmin = tmp[0]
    xmax = tmp[1]
    SetXaxisRanges(can,xmin,xmax)
    return

def SetXaxisRanges(can,xmin,xmax) :
    from ROOT import TGraph,TH1
    xaxis = 0
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            xaxis = i.GetHistogram().GetXaxis()
            break
        if issubclass(type(i),TH1) :
            xaxis = i.GetXaxis()
            break
    xaxis.SetLimits(xmin,xmax)
    can.Modified()
    can.Update()
    return

def GetXaxisRanges(can,check_all=False) :
    #
    # check_all is if you want to check the maximum extent of all the histograms you plotted.
    #
    from ROOT import TGraph,TH1
    xmin = 999999999
    xmax = -999999999
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            xaxis = i.GetHistogram().GetXaxis()
            if not check_all :
                return [xaxis.GetXmin(),xaxis.GetXmax()] 
            xmin = min(xmin,xaxis.GetXmin())
            xmax = max(xmax,xaxis.GetXmax())
        if issubclass(type(i),TH1) :
            xaxis = i.GetXaxis()
            if not check_all :
                return [xaxis.GetXmin(),xaxis.GetXmax()]
            xmin = min(xmin,xaxis.GetXmin())
            xmax = max(xmax,xaxis.GetXmax())
    return [xmin,xmax]
