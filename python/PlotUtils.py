from ROOT import TCanvas,TLegend,TGraph,TGraphErrors,TH1F,gROOT
from ROOT import TLine,TMath,TPad,gStyle,TROOT,TText,TProfile,TH2F,TH1D
from ROOT import kRed,kMagenta,kBlue,kCyan,kGreen,kGray,kBlack,kOrange,kYellow
from ROOT import TLatex,TAxis
#import AtlasStyle
from array import array
gROOT.SetBatch(True)
gStyle.SetStatColor(0)
gStyle.SetTitleColor(0)
gStyle.SetCanvasColor(0)
gStyle.SetPadColor(0)
gStyle.SetPadBorderMode(0)
gStyle.SetCanvasBorderMode(0)
gStyle.SetFrameBorderMode(0)
#gStyle.SetOptStat(1110)
gStyle.SetOptStat(0)
gStyle.SetStatH(0.3)
gStyle.SetStatW(0.3)
gStyle.SetTitleColor(1)
gStyle.SetTitleFillColor(0)
gStyle.SetTitleY(1.)
gStyle.SetTitleX(.1)
gStyle.SetTitleBorderSize(0)
gStyle.SetHistLineWidth(2)
gStyle.SetLineWidth(2)
gStyle.SetFrameFillColor(0)
gStyle.SetOptTitle(0)
gStyle.SetPadTopMargin(0.1)
gStyle.SetTitleFontSize(0.4)
gStyle.SetTitleYOffset(1.75)
gStyle.SetPaintTextFormat('4.1f ')

#color = [1,3,2,4,6,9,11,46,49,12,13,14,15,16,5,7,8,10,17,18,19,20,21,22,23,24,25,26]
color = [kBlack+0,kRed+1,kBlue+1,kGreen+1,kMagenta+1,kCyan+1,kOrange+1
         ,kBlack+2,kRed+3,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3
         ,kGray,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7
         ,kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5
         ,21,22,23,24,25,26,27,28,29,30
         ]

graphtypes = [type(TGraph()),type(TGraphErrors())]
histtypes = [type(TH1F()),type(TH1D()),type(TProfile()),type(TH2F())]
h1types = [type(TH1F()),type(TH1D()),type(TProfile())]
#listtypes = [type(TList),type(THashList())]

def GetZaxisReasonableRanges(hist,forcelow=None,forcehigh=None) :
    if type(hist) is not type(TH2F()) :
        print 'Error in Z axis.'
        return
    minz = 0
    maxz = 0
    for x in range(hist.GetNbinsX()) :
        for y in range(hist.GetNbinsY()) :
            z = hist.GetBinContent(x+1,y+1)
            if z < minz : minz = z
            if z > maxz : maxz = z
    if type(forcelow) != type(None) and minz > forcelow :
        minz = forcelow
    if type(forcehigh) != type(None) and maxz < forcehigh :
        maxz = forcehigh
    hist.GetZaxis().SetRangeUser(minz,maxz)

def GetReasonableRanges(plots,ranges=0,log=False):
    minx,miny,maxx,maxy = 0.,0.,1.,1.
    for pl in range(len(plots)) :
        localminx,localmaxx,localminy,localmaxy = 0.,0.,1.,1.
        if type(plots[pl]) in graphtypes :
            localminx = TMath.MinElement(plots[pl].GetN(),plots[pl].GetX())
            localmaxx = TMath.MaxElement(plots[pl].GetN(),plots[pl].GetX())
            localminy = TMath.MinElement(plots[pl].GetN(),plots[pl].GetY())
            localmaxy = TMath.MaxElement(plots[pl].GetN(),plots[pl].GetY())
        elif type(plots[pl]) in h1types :
            localminx = plots[pl].GetBinLowEdge(1)
            localmaxx = plots[pl].GetBinLowEdge(plots[pl].GetNbinsX()+1)
            localminy = plots[pl].GetMinimum()
            localmaxy = plots[pl].GetMaximum()
        if not pl :
            minx,maxx,miny,maxy = localminx,localmaxx,localminy,localmaxy
        minx = localminx if (localminx < minx) else minx
        maxx = localmaxx if (localmaxx > maxx) else maxx
        miny = localminy if (localminy < miny) else miny
        maxy = localmaxy if (localmaxy > maxy) else maxy

    newminy = 1.1*miny if miny<0 else 0.9*miny
    newmaxy = 1.1*maxy if maxy>0 else 0.9*maxy

    if ranges :
        if ranges[0] : minx = ranges[0][0]
        if ranges[0] : maxx = ranges[0][1]
        if ranges[1] : newminy = ranges[1][0]
        if ranges[1] : newmaxy = ranges[1][1]

    if log and (newminy <= 0.) and (newmaxy >= 0.) :
        #print 'Trying to fix!'
        newminy = min(0.5,0.01*newmaxy)

    #print 'miny,maxy:',newminy,newmaxy

    if type(plots[0]) in graphtypes :
        plots[0].GetXaxis().SetLimits(minx,maxx)
    elif type(plots[0]) in h1types :
        plots[0].GetXaxis().SetRangeUser(minx,maxx)
    plots[0].GetYaxis().SetRangeUser(newminy,newmaxy)
    return [minx,maxx,newminy,newmaxy]

def writeCan(file,dir,can,name) :
    file.cd(dir)
    can.Write(name)

class SmartPlot :
    def __init__(self,file,dir,name,plots,drawopt='',ranges=0,legendpos='topright',markersize=1
                 ,normalized=False,writecan=False,log=False) :

        # ranges : [[xmin,xmax],[ymin,ymax]]
        # i.e. [None,[.84,1.02]]
        
        self.dir = dir
        self.name = name
        self.can = TCanvas(name,name,500,500)
        self.log = log
        self.normalized = normalized
        self.markersize = markersize
        self.nplots = 0
        self.legendpos = legendpos
        self.normplots = []
        self.ranges = ranges
        self.drawopt = drawopt
        self.plots = []
        self.plotLegNames = []
        self.plotLegSizes = []
        for p in range(len(plots)) :
            self.plots.append(0)
            self.plots[p] = plots[p]
            self.plotLegNames.append(self.plots[p].GetName())
            self.plotLegSizes.append(len(self.plots[p].GetName()))
            
        plots[0].GetYaxis().SetTitleOffset(1.35)

        if 'colz' in drawopt :
            self.can.SetRightMargin(0.18)
        self.can.cd()

        legHeight = 0.06*len(plots)
        legWidth = 0.010*max(self.plotLegSizes)

        # 'topright'
        x1 = .55-legWidth # extra 10% for image
        if x1 < 0 : x1 = 0.15
        y1 = .85-legHeight
        if y1 < 0 : y1 = 0.05
        x2 = 0.90
        y2 = 0.85
        if 'bottom' in legendpos :
            y1 = .2+legHeight
            if y1 > 1 : y1 = 0.90
            y2 = 0.2
        if 'left' in legendpos :
            x1 = 0.15
            x2 = .50+legWidth # extra 10% for image
            if x2 > 1 : x2 = 0.90

        self.leg = TLegend(x1,y1,x2,y2)
        self.leg.SetTextFont(42)
        self.leg.SetBorderSize(0)
        self.leg.SetFillStyle(0)
        if type(plots[0]) != type(TH2F()) :
            ranges = GetReasonableRanges(plots,ranges,log=self.log)
            self.xmin,self.xmax,self.ymin,self.ymax = ranges[0],ranges[1],ranges[2],ranges[3]
        else :
            self.xmin = plots[0].GetXaxis().GetBinLowEdge(1)
            self.xmax = plots[0].GetXaxis().GetBinLowEdge(plots[0].GetNbinsX()+1)
            self.ymin = plots[0].GetYaxis().GetBinLowEdge(1)
            self.ymax = plots[0].GetYaxis().GetBinLowEdge(plots[0].GetNbinsY()+1)

        if type(plots[0]) == type(TH2F()) :
            self.can.SetLogz(self.log)

        # Set up plots
        for pl in range(len(plots)) :
        
            self.nplots += 1
            plots[pl].SetMarkerColor(color[pl])
            plots[pl].SetLineColor(color[pl])
            #plots[pl].SetFillColor(color[pl])
            #plots[pl].SetFillStyle(3001)
            if (plots[pl].GetMarkerStyle() == 1) :
                plots[pl].SetMarkerStyle(20)
            plots[pl].SetMarkerSize(markersize)
        
            name = plots[pl].GetName()
            #if name.find('pp') != -1 :
            #    plots[pl].SetMarkerStyle(25)
            #    plots[pl].SetMarkerSize(2)
        
            self.leg.AddEntry(plots[pl],plots[pl].GetName(),'le')

        # print plots
        for pl in range(len(plots)) : # Don't do 'for plot in plots!'
            if (not pl) :
                same_str = ''
                if (type(plots[0]) in graphtypes) : same_str = 'ap'
                if self.normalized :
                    self.normplots.append(plots[0].DrawNormalized(same_str+drawopt))
                else :
                    plots[0].Draw(same_str+drawopt)
                if 'colz' in self.drawopt : plots[0].SetMarkerSize(1.4)
                continue

            same_str = ''
            if (type(plots[pl]) in histtypes) : same_str = 'same'
            if (type(plots[pl]) in graphtypes) : same_str = 'p'
            if self.normalized :
                self.normplots.append(plots[pl].DrawNormalized(same_str+drawopt))
            else :
                plots[pl].Draw(same_str+drawopt)
                
        if 'colz' not in self.drawopt :
            self.leg.Draw()
        t=TLatex()
        t.SetTextSize(0.038)
        t.SetTextFont(42)
        t.DrawTextNDC(0.1,0.93,self.name)
        self.can.SetLogy(self.log)
        #print 'setting logy to',self.log
        if writecan : self.writeCan(file)
        return

    def writeCan(self,file) :
        if self.normalized :
            ranges = GetReasonableRanges(self.normplots,self.ranges,self.log)
        file.cd(self.dir)
        self.can.SetLogy(self.log)
        #print 'setting logy to',self.log
        self.can.Write(self.name)

    def DrawHorizontal(self,yval,color=1,pct=[0.,1.]) :
        self.can.cd()
        a = TLine()
        a.SetLineColor(color)
        a.DrawLine((self.xmax-xelf.xmin)*pct[0],yval,(self.xmax-xelf.xmin)*pct,yval)

    def DrawVertical(self,xval,color=1,pct=[0.,1.]) :
        self.can.cd()
        a = TLine()
        a.SetLineColor(color)
        a.DrawLine(xval,(self.ymax-self.ymin)*pct[0],xval,(self.ymax-self.ymin)*pct[1])

    def AddPlots(self,plots,drawopt='') :
        self.can.cd()
        for pl in range(len(plots)) : # Don't do 'for plot in plots!'
            self.leg.AddEntry(plots[pl],plots[pl].GetName(),'le')
            plots[pl].SetMarkerSize(self.markersize)
            plots[pl].SetLineWidth(2)
            plots[pl].SetLineColor(color[self.nplots])
            plots[pl].SetMarkerColor(color[self.nplots])
            #plots[pl].SetFillColor(color[pl])
            #plots[pl].SetFillStyle(3001)
            same_str = ''
            if (type(plots[pl]) in histtypes) : same_str = 'same'
            if (type(plots[pl]) in graphtypes) : same_str = 'p'
            if self.normalized :
                self.normplots.append(plots[pl].DrawNormalized(same_str+drawopt))
            else :
                plots[pl].Draw(same_str+drawopt)
            self.nplots += 1
        self.can.Update()
            
    def DrawText(self,x,y,text,angle=0,align='',size=0.035) :
        self.can.cd()
        t = TLatex()
        t.SetTextSize(0.035)
        if align == 'R': t.SetTextAlign(31)
        if angle : t.SetTextAngle(angle)
        t.DrawText(x,y,text)



