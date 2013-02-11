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
