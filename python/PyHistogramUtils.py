import math

#-- TH2F methods --------------------------------------------------
def getIntegralAllFlows(h) :
    total = h.Integral(0,h.GetNbinsX()+1,0,h.GetNbinsY()+1)
    #print 'Total:',total
    middle = h.Integral(1,h.GetNbinsX(),1,h.GetNbinsY())
    #print 'total :',total
    #print 'middle:',middle
    #print 'over  :',getIntegralXOverflows(h)
    #print 'under :',getIntegralXUnderflows(h)
    extra_bit  = h.Integral(1,h.GetNbinsX(),0,0)
    extra_bit += h.Integral(1,h.GetNbinsX(),h.GetNbinsY()+1,h.GetNbinsY()+1)
    #print 'extra:',extra_bit
    assert total == middle+extra_bit+getIntegralXOverflows(h)+getIntegralXUnderflows(h),'Error in integral!'
    #assert ((total > 0) and (extra_bit/float(total) < 0.001)),'Error - significant unaccounted-for chunk!'
    return total
def getIntegralXOverflows(h) :
   obin = h.GetNbinsX()+1
   #print 'Overflows:',h.Integral(obin,obin,-1,h.GetNbinsY()+1)
   return h.Integral(obin,obin,0,h.GetNbinsY()+1)
def getIntegralXUnderflows(h) :
   ubin = 0
   #print 'Underflows:',h.Integral(ubin,ubin,-1,h.GetNbinsY()+1)
   return h.Integral(ubin,ubin,0,h.GetNbinsY()+1)
#
def getXprojectionWithFlows(h,name) :
    obin =h.GetNbinsY()+1
    ubin = -1 # 0 also works
    return h.ProjectionX(name,ubin,obin)
def getXprojectionOnlyOverflows(h,name) :
    obin = h.GetNbinsY()+1
    return h.ProjectionX(name,obin,obin)
def getXprojectionOnlyUnderflows(h,name) :
    ubin = -1 # 0 also works
    return h.ProjectionX(name,ubin,ubin)
#
def getYprojectionWithFlows(h,name) :
    obin =h.GetNbinsX()+1
    ubin = -1 # 0 also works
    return h.ProjectionY(name,ubin,obin)
def getYprojectionOnlyOverflows(h,name) :
    obin = h.GetNbinsX()+1
    return h.ProjectionY(name,obin,obin)
def getYprojectionOnlyUnderflows(h,name) :
    ubin = -1 # 0 also works
    return h.ProjectionY(name,ubin,ubin)

#-- TH1 Methods -----------------------------------------------------
def getIntegralFlows(h) :
    total = h.Integral(-1,h.GetNbinsX()+1)
    #print 'Total:',total
    middle = h.Integral(1,h.GetNbinsX())
    assert total == middle+getIntegralOverflows(h)+getIntegralUnderflows(h),'Error in integral!'
    return total
def getIntegralOverflows(h) :
   obin = h.GetNbinsX()+1
   #print 'Overflows:',h.Integral(obin,obin,-1,h.GetNbinsY()+1)
   return h.Integral(obin,obin)
def getIntegralUnderflows(h) :
   ubin = 0
   #print 'Underflows:',h.Integral(ubin,ubin,-1,h.GetNbinsY()+1)
   return h.Integral(ubin,ubin)

#----------------------------------------------------
def set1dErrors(th,errs) :
    for i in range(th.GetNbinsX()) :
        th.SetBinError(i+1,errs.GetBinContent(i+1))
    return

def setErrorsFractional(th,hx1,hx2) :
    for i in range(th.GetNbinsX()) :
        f = th.GetBinContent(i+1)
        x1 = float(hx1.GetBinContent(i+1))
        dx1 = hx1.GetBinError(i+1)
        x2 = float(hx2.GetBinContent(i+1))
        dx2 = hx2.GetBinError(i+1)
        if (x1 == 0) or (x2 == 0) : continue
        th.SetBinError(f*math.sqrt(math.pow(dx1/x1,2)+mth.pow(dx2/x2,2)))
        
def setEffErrors(th,den) :
    for i in range(th.GetNbinsX()) :
        eff = th.GetBinContent(i+1)
        if eff < 0: eff = 0
        if eff > 1: eff = 1
        n = den.GetBinContent(i+1)
        if n != 0 and 0 <= eff and eff <= 1 :
            err = math.sqrt(eff*(1-eff)/n)
            th.SetBinError(i+1,err)
            
    return

def setEffContentErrorsWeights(th,num,fail) :
    for i in range(th.GetNbinsX()) :
        nm = num.GetBinContent(i+1)
        if nm < 0 : nm = 0
        fl = fail.GetBinContent(i+1)
        if fl <= 0 : fl = 1
        eff = nm/float(nm+fl)
        if eff < 0: eff = 0
        if eff > 1: eff = 1
        nm_sumw2 = num.GetSumw2()[i+1]
        fl_sumw2 = fail.GetSumw2()[i+1]
        err = math.sqrt(math.pow(fl,2)*nm_sumw2+math.pow(nm,2)*fl_sumw2)/float(math.pow(nm+fl,2))
        th.SetBinContent(i+1,eff)
        th.SetBinError(i+1,err)

    return


#----------------------------------------------------
def MakeEffPlotsFromNumDen(thnum,thden) :
    for i in range(thnum.GetNbinsX()) :
        bin = i+1
        num = thnum.GetBinContent(bin)
        den = float(thden.GetBinContent(bin))
        if den <=0. : den = 1.
        eff = num/den
        thnum.SetBinContent(bin,eff)
        if 0 <= eff and eff <= 1 :
            efferr = math.sqrt(eff*(1-eff)/den)
            thnum.SetBinError(bin,efferr)
    return
