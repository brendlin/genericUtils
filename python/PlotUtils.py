from ROOT import TCanvas,TLegend,TGraph,TGraphErrors,TH1F,gROOT,TF1
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
gStyle.SetOptStat(0)
gStyle.SetStatH(0.3)
gStyle.SetStatW(0.3)
gStyle.SetTitleColor(1)
gStyle.SetTitleFillColor(0)
gStyle.SetTitleY(1.)
gStyle.SetTitleX(.1)
gStyle.SetTitleBorderSize(0)
gStyle.SetHistLineWidth(2)
gStyle.SetLineWidth(1)
gStyle.SetFrameFillColor(0)
gStyle.SetOptTitle(0)
#
gStyle.SetTitleFontSize(0.4)
gStyle.SetTitleYOffset(1.75)
gStyle.SetPaintTextFormat('4.1f ')
gStyle.SetEndErrorSize(3)

#gStyle.SetOptStat(1110)

#color = [1,3,2,4,6,9,11,46,49,12,13,14,15,16,5,7,8,10,17,18,19,20,21,22,23,24,25,26]
color = [kBlack+0,kRed+1,kBlue+1,kGreen+1,kMagenta+1,kCyan+1,kOrange+1
         ,kBlack+2,kRed+3,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3
         ,kGray,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7
         ,kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5
         ,21,22,23,24,25,26,27,28,29,30
         ,21,22,23,24,25,26,27,28,29,30
         ,21,22,23,24,25,26,27,28,29,30
         ]

markerstyles = [20,21,22,23,24,25,26,27]

graphtypes = [type(TGraph()),type(TGraphErrors())]
histtypes = [type(TH1F()),type(TH1D()),type(TProfile()),type(TH2F())]
formulatypes = [type(TF1())]
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
        if type(plots[pl]) in formulatypes :
            pass
            localminx = plots[pl].GetXmin()
            localmaxx = plots[pl].GetXmax()
            localminy = plots[pl].GetMinimum()
            localmaxy = plots[pl].GetMaximum()
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
    def __init__(self,file,dir,name,plots,drawopt='E1',ranges=0,legendpos='topright',markersize=1.0
                 ,markerstyle=20,drawtitle=True
                 ,normalized=False,writecan=False,log=False,drawleg=True) :

        # ranges : [[xmin,xmax],[ymin,ymax]]
        # i.e. [None,[.84,1.02]]
        
        self.dir = dir
        self.name = name
        self.can = TCanvas(name,name,500,500)
        self.log = log
        self.normalized = normalized
        self.markersize = markersize
        self.markerstyle = markerstyle
        self.drawtitle = drawtitle
        self.nplots = 0
        self.legendpos = legendpos
        self.normplots = []
        self.ranges = ranges
        self.drawopt = drawopt
        self.plots = []
        self.plotLegNames = []
        self.plotLegSizes = []
        self.drawleg = drawleg

        for p in range(len(plots)) :
            self.plots.append(0)
            self.plots[p] = plots[p]
            self.plotLegNames.append(self.plots[p].GetName())
            self.plotLegSizes.append(len(self.plots[p].GetName()))
            
        self.plots[0].GetYaxis().SetTitleOffset(1.45)
        self.plots[0].GetYaxis().SetTitleSize(0.05)
        self.plots[0].GetYaxis().SetTitleFont(42)

        self.plots[0].GetYaxis().SetLabelSize(0.04)
        self.plots[0].GetYaxis().SetLabelFont(42)

        self.plots[0].GetXaxis().SetTitleOffset(0.85)
        self.plots[0].GetXaxis().SetTitleSize(0.05)
        self.plots[0].GetXaxis().SetTitleFont(42)

        self.plots[0].GetXaxis().SetLabelSize(0.04)
        self.plots[0].GetXaxis().SetLabelFont(42)

        self.can.cd()

        legHeight = 0.06*len(self.plots)
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

        if type(self.plots[0]) != type(TH2F()) :
            ranges = GetReasonableRanges(self.plots,ranges,log=self.log)
            self.xmin,self.xmax,self.ymin,self.ymax = ranges[0],ranges[1],ranges[2],ranges[3]
        else :
            self.xmin = self.plots[0].GetXaxis().GetBinLowEdge(1)
            self.xmax = self.plots[0].GetXaxis().GetBinLowEdge(self.plots[0].GetNbinsX()+1)
            self.ymin = self.plots[0].GetYaxis().GetBinLowEdge(1)
            self.ymax = self.plots[0].GetYaxis().GetBinLowEdge(self.plots[0].GetNbinsY()+1)

        if type(self.plots[0]) == type(TH2F()) :
            self.can.SetLogz(self.log)

        self.createLegend(x1,y1,x2,y2)
        self.SetLegend()

        # print plots
        for pl in range(len(self.plots)) : # Don't do 'for plot in plots!'
            if (not pl) :
                same_str = ''
                if (type(self.plots[0]) in graphtypes) : same_str = 'a'
                if self.normalized :
                    self.normplots.append(self.plots[0].DrawNormalized(same_str+drawopt))
                    if not self.normplots[-1] : self.normplots[-1] = TH1F()
                else :
                    self.plots[0].Draw(same_str+drawopt)
                if 'colz' in self.drawopt : self.plots[0].SetMarkerSize(1.4)
                continue

            same_str = ''
            if (type(self.plots[pl]) in histtypes) : same_str = 'same'
            if (type(self.plots[pl]) in graphtypes) : same_str = ''
            if (type(self.plots[pl]) in formulatypes) : 
                same_str = 'same'
            if self.normalized :
                self.normplots.append(self.plots[pl].DrawNormalized(same_str+drawopt))
                if not self.normplots[-1] : self.normplots[-1] = TH1F()
            else :
                self.plots[pl].Draw(same_str+drawopt)
        
        if self.normalized :
            GetReasonableRanges(self.normplots,self.ranges,log=self.log)

        # Set up plots
        self.SetColors()
        self.SetStyles()
        self.SetMarkers(these_marker_sizes=0,these_styles=0)

        if ('colz' not in self.drawopt) and self.drawleg :
            self.leg.Draw()

        self.can.SetBottomMargin(0.10) # equivalent to Style.SetPadBottomMargin(0.10)
        self.can.SetLeftMargin  (0.16) # equivalent to Style.SetPadLeftMargin  (0.16)
        self.can.SetTopMargin   (0.05) # equivalent to Style.SetPadTopMargin   (0.05)
        self.can.SetRightMargin (0.05) # equivalent to Style.SetPadRightMargin (0.05)

        if 'colz' in drawopt :
            self.can.SetRightMargin(0.18)

        t=TLatex()
        if self.drawtitle :
            t.SetNDC()
            t.SetTextSize(0.050)
            t.SetTextFont(42)
            #t.DrawTextNDC(0.1,0.93,self.name)
            t.DrawLatex(0.1,0.93,self.name)
            self.can.SetTopMargin(0.1)

        self.can.SetLogy(self.log)
        if writecan : self.writeCan(file)
        return

    def SetColors(self,these_colors=color) :

        if not these_colors : return
        for pl in range(len(self.plots)) :
            self.plots[pl].SetMarkerColor(these_colors[pl])
            self.plots[pl].SetLineColor(these_colors[pl])
            self.plots[pl].SetMarkerSize(self.markersize)
            # self.plots[pl].SetFillColor(these_colors[pl])
            if (self.plots[pl].GetFillStyle() != 1001) :
                self.plots[pl].SetFillColor(these_colors[pl])

        for pl in range(len(self.normplots)) :
            if not self.normplots[pl] : continue
            self.normplots[pl].SetMarkerColor(these_colors[pl])
            self.normplots[pl].SetLineColor(these_colors[pl])
            self.normplots[pl].SetMarkerSize(self.markersize)
            #self.normplots[pl].SetFillColor(these_colors[pl])
            #self.normplots[pl].SetFillColor(these_colors[pl])
            if (self.normplots[pl].GetFillStyle() != 1001) :
                self.normplots[pl].SetFillColor(these_colors[pl])
        return

    def SetStyles(self,these_styles=[]) :
        if not these_styles : return
        for pl in range(len(self.plots)) :
            if type(these_styles) == type([]) :
                self.plots[pl].SetFillStyle(these_styles[pl])
            else :
                self.plots[pl].SetFillStyle(these_styles)
        return

    def SetMarkers(self,these_marker_sizes=0,these_styles=0) :
        if not these_marker_sizes : these_marker_sizes = self.markersize
        if not these_styles : these_styles = self.markerstyle
        if not these_marker_sizes and not these_styles : return
        for pl in range(len(self.plots)) :
            if these_marker_sizes :
                if type(these_marker_sizes) == type([]) :
                    self.plots[pl].SetMarkerSize(these_marker_sizes[pl])
                else :
                    self.plots[pl].SetMarkerSize(these_marker_sizes)
            if these_styles :
                if type(these_styles) == type([]) :
                    self.plots[pl].SetMarkerStyle(these_styles[pl])
                else :
                    self.plots[pl].SetMarkerStyle(these_styles)

        return

    def SetLegend(self,skip=[]) :
        for pl in range(len(self.plots)) :
            if pl in skip : continue
            # print 'adding entry',self.plots[pl].GetName()
            self.leg.AddEntry(self.plots[pl],self.plots[pl].GetName(),'ple')
        return

    def writeCan(self,file) :
        if self.normalized :
            ranges = GetReasonableRanges(self.normplots,self.ranges,self.log)
        file.cd(self.dir)
        self.can.SetLogy(self.log)
        #print 'setting logy to',self.log
        self.can.Write(self.name)

    def createLegend(self,x1,y1,x2,y2) :
        #print x1,y1,x2,y2
        if self.can.GetPrimitive('mylegend') :
            self.can.GetPrimitive('mylegend').Delete()
        self.leg = TLegend(x1,y1,x2,y2)
        self.leg.SetName('mylegend')
        self.leg.SetTextFont(42)
        self.leg.SetBorderSize(0)
        self.leg.SetFillStyle(0)
        
    def recreateLegend(self,x1,y1,x2,y2) :
        self.can.cd()
        self.createLegend(x1,y1,x2,y2)
        self.SetLegend()
        if ('colz' not in self.drawopt) and self.drawleg :
            self.can.cd()
            self.leg.Draw()
        return

    def DrawHorizontal(self,yval,color=1,pct=[0.,1.],style=1) :
        self.can.cd()
        a = TLine()
        a.SetLineColor(color)
        a.SetLineStyle(style)
        a.DrawLine((self.xmax-self.xmin)*pct[0],yval,(self.xmax-self.xmin)*pct[1],yval)

    def DrawVertical(self,xval,color=1,pct=[0.,1.]) :
        self.can.cd()
        a = TLine()
        a.SetLineColor(color)
        a.SetLineStyle(style)
        a.DrawLine(xval,(self.ymax-self.ymin)*pct[0],xval,(self.ymax-self.ymin)*pct[1])

    def AddPlots(self,plots,drawopt='') :
        for pl in range(len(plots)) :
            self.plots.append(plots[pl])
        self.can.cd()
        for pl in range(len(plots)) : # Don't do 'for plot in plots!'
            self.leg.AddEntry(plots[pl],plots[pl].GetName(),'le')
            # plots[pl].SetMarkerSize(self.markersize)
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
                if not self.normplots[-1] : self.normplots[-1] = TH1F()
                GetReasonableRanges(self.normplots,self.ranges,log=self.log)
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

    def DrawTextNDC(self,x,y,text,angle=0,align='',size=0.035) :
        self.can.cd()
        t = TLatex()
        t.SetTextSize(0.04)
        t.SetTextFont(42)
        if align == 'R': t.SetTextAlign(31)
        if angle : t.SetTextAngle(angle)
        t.DrawTextNDC(x,y,text)

    def CleanNameForMacro(self,nm) :
        return ''.join(ch for ch in nm if ch.isalnum())

    def SaveMacro(self,name= '') :
        for p in range(len(self.plots)) :
            key = self.CleanNameForMacro(self.plots[p].GetName())
            self.plots[p].SetName(key)
            key = self.CleanNameForMacro(self.plots[p].GetTitle())
            self.plots[p].SetTitle(key)
        self.can.SetName(self.CleanNameForMacro(self.can.GetName()))
        self.can.SetTitle(self.CleanNameForMacro(self.can.GetTitle()))
        if not name : name = self.can.GetName()
        self.can.SaveAs(name+'.C')
        return

    def SavePDF(self,name='') :
        if not name : name = self.CleanNameForMacro(self.can.GetName())
        self.can.SaveAs(name+'.pdf')
        return
