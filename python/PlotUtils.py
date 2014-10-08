from ROOT import TCanvas,TLegend,TGraph,TGraphErrors,TGraphAsymmErrors,TH1F,gROOT,TF1,TH1
from ROOT import TLine,TMath,TPad,gStyle,TROOT,TText,TProfile,TH2F,TH1D,TH3F
from ROOT import kRed,kMagenta,kBlue,kCyan,kGreen,kGray,kBlack,kOrange,kYellow,kAzure
from ROOT import TLatex,TAxis,TASImage,kTRUE
#import AtlasStyle
from array import array
#gROOT.SetBatch(True)

#
# TH1.SetDefaultSumw2(kTRUE) - very important for correctly plotting
# and calculating errors. For instance "Scale" will mess up your
# errors if this is not set to True.
#
# Comment out for now since it is incompatible with some
# jobs (too much memory)
#
#TH1.SetDefaultSumw2(kTRUE)

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
color = [kBlack+0,kRed+1,kAzure-2,kGreen+1,kMagenta+1,kCyan+1,kOrange+1
         ,kBlack+2,kRed+3,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3
         ,kGray,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7
         ,kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5
         ,21,22,23,24,25,26,27,28,29,30
         ,21,22,23,24,25,26,27,28,29,30
         ,21,22,23,24,25,26,27,28,29,30
         ]
color += color
color += color

markerstyles = [20,21,22,23,24,25,26,27]

graphtypes = [type(TGraph()),type(TGraphErrors()),type(TGraphAsymmErrors())]
histtypes = [type(TH1F()),type(TH2F()),type(TProfile()),type(TH1D()),type(TH3F())]
formulatypes = [type(TF1())]
h1types = [type(TH1F()),type(TH1D()),type(TProfile()),type(TH1D())]
#listtypes = [type(TList),type(THashList())]

# def AddWatermark(can,x0=0.,y0=0.,x1=.1,y1=.1) :
#     from ROOT import TASImage
#     #a = TASImage('shield.color.png')
#     #a = TASImage('penn_fulllogo_black.pdf')
#     a = TASImage('penn_notitle_20.png')
#     #p = TPad('watermark','watermark',x0,y0,x1,y1)
#     #p.SetFillColor(42)
#     #p.SetFillColor(0)
#     #p.SetFillStyle(4050)
#     #p.SetFillStyle(0)
#     #p.cd()
#     can.cd()
#     a.Draw()
#     can.cd()
#     p.Draw("sames")
#     return a,p

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

def SmartPlot(file,dir,name,plots
              ,drawopt='E1',ranges=0,legendpos='topright',markersize=1.0
              ,markerstyle=20,drawtitle=True
              ,normalized=False,writecan=False,log=False,drawleg=True
              ,canw=500,canh=500) :
    return PlotObject(name,plots,file=file,dir=dir
                      ,drawopt=drawopt,ranges=ranges,legendpos=legendpos,markersize=markersize
                      ,markerstyle=markerstyle,drawtitle=drawtitle
                      ,normalized=normalized,writecan=writecan,log=log,drawleg=drawleg
                      ,canw=canw,canh=canh)

class PlotObject :
    def __init__(self,name,plots,file=0,dir=''
                 ,drawopt='E1',ranges=0,legendpos='topright',markersize=1.0
                 ,markerstyle=20,drawtitle=True
                 ,normalized=False,writecan=False,log=False,drawleg=True
                 ,canw=500,canh=500
                 ,watermark=False) :

        # ranges : [[xmin,xmax],[ymin,ymax]]
        # i.e. [None,[.84,1.02]]
        
        self.file = file
        self.dir = dir
        self.name = name
        self.can = TCanvas(name,name,canw,canh)
        self.canw = canw
        self.canh = canh
        self.log = log
        self.normalized = normalized
        self.normfac = 1.
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
        self.watermark = watermark
        self.drawopts = []
        self.text = []

        if self.watermark :
            #self.wmimage = TASImage('penn_notitle_10.pdf')
            #self.wmimage = TASImage('penn_notitle_20.pdf')
            #self.wmimage = TASImage('penn_notitle_20_topleft.pdf')
            #self.wmimage = TASImage('penn_notitle_20_botleft.pdf')
            #self.wmimage = TASImage('penn_notitle_20_topright.pdf')
            self.wmimage = TASImage('penn_notitle_20_botright.pdf')
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

        if type(self.plots[0]) in histtypes :
            self.plots[0].GetZaxis().SetTitleOffset(0.85)
            self.plots[0].GetZaxis().SetTitleSize(0.05)
            self.plots[0].GetZaxis().SetTitleFont(42)        

            self.plots[0].GetZaxis().SetLabelSize(0.04)
            self.plots[0].GetZaxis().SetLabelFont(42)

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

        self.CreateLegend(x1,y1,x2,y2)
        self.SetLegend()

        # print plots
        for pl in range(len(self.plots)) : # Don't do 'for plot in plots!'
            if (not pl) :
                same_str = ''
                if (type(self.plots[0]) in graphtypes) : same_str = 'a'
                if self.normalized :
                    #self.normfac = self.plots[0].Integral()
                    self.plots[0].Scale(1/float(self.plots[0].Integral()))
                    #self.normplots.append(self.plots[0].DrawNormalized(same_str+drawopt))
                    #if not self.normplots[-1] : self.normplots[-1] = TH1F()
                if True :
                    self.drawopts.append(same_str+drawopt)
                    self.plots[0].Draw(same_str+drawopt)
                    if self.watermark :
                        self.wmimage.Draw('sames')
                        self.plots[0].Draw('sames'+drawopt)
                        self.can.SetTickx(1)
                        self.can.SetTicky(1)
                        self.can.RedrawAxis()
                if 'colz' in self.drawopt : self.plots[0].SetMarkerSize(1.4)
                continue

            same_str = ''
            if (type(self.plots[pl]) in histtypes) : same_str = 'same'
            if (type(self.plots[pl]) in graphtypes) : same_str = ''
            if (type(self.plots[pl]) in formulatypes) : 
                same_str = 'same'
            if self.normalized :
                self.plots[pl].Scale(1/float(self.plots[pl].Integral()))
                #self.normplots.append(self.plots[pl].DrawNormalized(same_str+drawopt))
                #if not self.normplots[-1] : self.normplots[-1] = TH1F()
            if True :
                self.plots[pl].Draw(same_str+drawopt)
        
        #if self.normalized :
        #    GetReasonableRanges(self.normplots,self.ranges,log=self.log)

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

        self.DrawTitle()

        self.can.SetLogy(self.log)
        if writecan : self.writeCan(file)
        return

    def DrawTitle(self,title='',textsize=0.050,x=0.1,y=0.93) :
        if self.can.GetPrimitive('title') :
            self.can.GetPrimitive('title').Delete()
        if not title :
            title = self.name
        self.title=TLatex(x,y,title)
        self.title.SetName('title')
        if self.drawtitle :
            self.title.SetNDC()
            self.title.SetTextSize(textsize)
            self.title.SetTextFont(42)
            self.can.cd()
            self.title.Draw()
            self.can.SetTopMargin(0.1)

    def SetColors(self,these_colors=color) :

        if not these_colors : return
        for pl in range(len(self.plots)) :
            self.plots[pl].SetMarkerColor(these_colors[pl])
            self.plots[pl].SetLineColor(these_colors[pl])
            self.plots[pl].SetMarkerSize(self.markersize)
            # self.plots[pl].SetFillColor(these_colors[pl])
            if (self.plots[pl].GetFillStyle() != 1001) :
                self.plots[pl].SetFillColor(these_colors[pl])

#         for pl in range(len(self.normplots)) :
#             if not self.normplots[pl] : continue
#             self.normplots[pl].SetMarkerColor(these_colors[pl])
#             self.normplots[pl].SetLineColor(these_colors[pl])
#             self.normplots[pl].SetMarkerSize(self.markersize)
#             #self.normplots[pl].SetFillColor(these_colors[pl])
#             #self.normplots[pl].SetFillColor(these_colors[pl])
#             if (self.normplots[pl].GetFillStyle() != 1001) :
#                 self.normplots[pl].SetFillColor(these_colors[pl])
        return

    def SetStyles(self,these_styles=[]) :
        if not these_styles : return
        for pl in range(len(self.plots)) :
            if type(these_styles) == type([]) :
                self.plots[pl].SetFillStyle(these_styles[pl])
            else :
                self.plots[pl].SetFillStyle(these_styles)
#         for pl in range(len(self.normplots)) :
#             if not self.normplots[pl] : continue
#             if type(these_styles) == type([]) :
#                 self.normplots[pl].SetFillStyle(these_styles[pl])
#             else :
#                 self.normplots[pl].SetFillStyle(these_styles)
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

#         for pl in range(len(self.normplots)) :
#             if not self.normplots[pl] : continue
#             if these_marker_sizes :
#                 if type(these_marker_sizes) == type([]) :
#                     self.normplots[pl].SetMarkerSize(these_marker_sizes[pl])
#                 else :
#                     self.normplots[pl].SetMarkerSize(these_marker_sizes)
#             if these_styles :
#                 if type(these_styles) == type([]) :
#                     self.normplots[pl].SetMarkerStyle(these_styles[pl])
#                 else :
#                     self.normplots[pl].SetMarkerStyle(these_styles)

        return

    def SetLegend(self,skip=[]) :
        for pl in range(len(self.plots)) :
            if pl in skip : continue
            # print 'adding entry',self.plots[pl].GetName()
            self.leg.AddEntry(self.plots[pl],self.plots[pl].GetName(),'ple')
        return

    def writeCan(self,can='') :
        #if self.normalized :
        #    ranges = GetReasonableRanges(self.normplots,self.ranges,self.log)
        self.file.cd(self.dir)
        
        if can == 'ratio' :
            self.ratiocan.Write(self.name)
            return
        self.can.SetLogy(self.log)
        self.can.Write(self.name)
        return

    def CreateLegend(self,x1,y1,x2,y2,can='') :
        #print x1,y1,x2,y2
        if can == 'RatioPadTop' :
            if self.RatioPadTop.GetPrimitive('mylegend') :
                self.RatioPadTop.GetPrimitive('mylegend').Delete()
            self.RatioPadTop.cd()
        else :
            if self.can.GetPrimitive('mylegend') :
                self.can.GetPrimitive('mylegend').Delete()
            self.can.cd()
        self.leg = TLegend(x1,y1,x2,y2)
        self.leg.SetName('mylegend')
        self.leg.SetTextFont(42)
        self.leg.SetBorderSize(0)
        self.leg.SetFillStyle(0)
        
    def RecreateLegend(self,x1,y1,x2,y2,can='',skip=[]) :

        self.CreateLegend(x1,y1,x2,y2,can=can)
        self.SetLegend(skip=skip)
        if ('colz' not in self.drawopt) and self.drawleg :
            self.can.cd()
            if can == 'RatioPadTop' :
                self.RatioPadTop.cd()
            self.leg.Draw()
        return

    def DrawHorizontal(self,yval,color=1,pct=[0.,1.],style=1,can='') :
        self.can.cd()
        if can == 'RatioPadBot' :
            self.RatioPadBot.cd()
        a = TLine()
        a.SetLineColor(color)
        a.SetLineStyle(style)
        a.SetLineWidth(2)
        a.DrawLine((self.xmax-self.xmin)*pct[0]+self.xmin,yval,(self.xmax-self.xmin)*pct[1]+self.xmin,yval)

    def DrawVertical(self,xval,color=1,pct=[0.,1.],style=1,can='') :
        self.can.cd()
        if can == 'RatioPadTop' :
            self.RatioPadTop.cd()
        a = TLine()
        a.SetLineColor(color)
        a.SetLineStyle(style)
        a.SetLineWidth(2)
        a.DrawLine(xval,(self.ymax-self.ymin)*pct[0]+self.ymin,xval,(self.ymax-self.ymin)*pct[1]+self.ymin)

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
            #if self.normalized :
            #    self.normplots.append(plots[pl].DrawNormalized(same_str+drawopt))
            #    if not self.normplots[-1] : self.normplots[-1] = TH1F()
            #    GetReasonableRanges(self.normplots,self.ranges,log=self.log)
            if True :
                plots[pl].Draw(same_str+drawopt)
            self.nplots += 1
        self.can.Update()

    def DrawAtlasPreliminary(self,x,y,angle=0,align='',size=0.035,can='',color=1,internal=True) :
        self.can.cd()
        if can == 'RatioPadTop' : self.RatioPadTop.cd()
        t = TLatex()
        t.SetNDC()
        t.SetTextSize(size)
        if can == 'RatioPadTop' :
            t.SetTextSize(0.05)
        t.SetTextFont(72)
        t.SetTextColor(color)
        if align == 'R': t.SetTextAlign(31)
        if angle : t.SetTextAngle(angle)
        t.DrawLatex(x,y,'ATLAS #font[42]{Internal}')

    def DrawLuminosity(self,x,y,angle=0,align='',size=0.035,can='',color=1,internal=True,lumi=20.3,sqrts=8) :
        self.can.cd()
        if can == 'RatioPadTop' : self.RatioPadTop.cd()
        t = TLatex()
        t.SetNDC()
        t.SetTextSize(size)
        if can == 'RatioPadTop' :
            t.SetTextSize(0.05)
        t.SetTextFont(42)
        t.SetTextColor(color)
        if align == 'R': t.SetTextAlign(31)
        if angle : t.SetTextAngle(angle)
        t.DrawLatex(x,y,'#sqrt{s} = %d TeV, #lower[-0.2]{#scale[0.60]{#int}}Ldt = %1.1f fb^{-1}'%(sqrts,lumi))

#     def DrawLuminosity(self,x,y,angle=0,align='',size=0.035,can='',color=1) :
#         self.can.cd()
#         if can == 'ratio' : self.RatioPadTop.cd()
#         self.lumiLabel = TLegend(.2,.87-.1,.2,.87-.1)#, "#int L dt = %1.1f fb^{-1}"%20.3)
#         self.lumiLabel.SetFillColor(0)
#         self.lumiLabel.SetTextFont(42)
#         self.lumiLabel.SetHeader("#sqrt{s} = 8 TeV, #scale[0.8]{#int} L dt = %1.1f fb^{-1}"%20.3)
#         self.lumiLabel.SetTextSize(0.04)
#         if can == 'ratio' :
#             self.lumiLabel.SetTextSize(0.05)
#         self.lumiLabel.Draw()
            
    def DrawText(self,x,y,text,angle=0,align='',size=0.035,can='') :
        self.can.cd()
        if can == 'RatioPadTop' : self.RatioPadTop.cd()
        self.text.append(TLatex())
        self.text[-1].SetTextSize(size)
        if align == 'R': self.text[-1].SetTextAlign(31)
        if angle : self.text[-1].SetTextAngle(angle)
        self.text[-1].DrawLatex(x,y,text)

    def DrawTextNDC(self,x,y,text,angle=0,align='',size=0.035,can='',color=1) :
        self.can.cd()
        if can == 'RatioPadTop' : self.RatioPadTop.cd()
        self.text.append(TLatex())
        self.text[-1].SetNDC()
        self.text[-1].SetTextSize(size)
        self.text[-1].SetTextFont(42)
        self.text[-1].SetTextColor(color)
        if align == 'R': self.text[-1].SetTextAlign(31)
        if angle : self.text[-1].SetTextAngle(angle)
        self.text[-1].DrawLatex(x,y,text)

    def SetAxisLabels(self,xlabel,ylabel) :
        if len(self.plots) :
            self.plots[0].GetXaxis().SetTitle(xlabel)
            self.plots[0].GetYaxis().SetTitle(ylabel)

    def CleanNameForMacro(self,nm) :
        for i in range(10) :
            nm = nm.replace('-%d'%i,'n%d'%i)
        nm = nm.replace(' ','_')
        nm = nm.replace('_','PUPPIES')
        nm = ''.join(ch for ch in nm if ch.isalnum())
        nm = nm.replace('PUPPIES','_')
        nm = nm.replace('___','_')
        nm = nm.replace('__','_')
        return nm

    def SetYaxisRange(self,lo,hi) :
        self.plots[0].GetYaxis().SetRangeUser(lo,hi)
        return

    # for ratio top axis
    def SetTopYaxisRange(self,lo,hi) :
        self.RatioTopPlot0.GetYaxis().SetRangeUser(lo,hi)
        return

    # for ratio bot axis
    def SetBotYaxisRange(self,lo,hi) :
        self.ratioplots[0].GetYaxis().SetRangeUser(lo,hi)

    def SetPlotLabels(self,name_list) :
        for p in range(len(name_list)) :
            if p >= len(self.plots) : continue
            self.plots[p].SetNameTitle(name_list[p],name_list[p])

    def MakeRatioPlot(self,den,nums,style='',divide='') :
        #
        # You can use self.ratioplots[0].GetYaxis().SetNdivisions(5,5,0)
        # to change the ticks.
        #
        #
        # RatioPadTop
        # - RatioTopPlot0 ( need a clone so I can manipulate ratio plot and regular plot separately)
        # RatioPadBot
        # - ratioplots (a list)
        #
        x = {'div'              :0.3
             ,'canw'            :self.canw
             ,'canh'            :self.canh+100
             ,'1BottomMargin'   :0.020
             ,'1TopMargin'      :0.05
             ,'2BottomMargin'   :0.30
             ,'2TopMargin'      :0.30

             ,'TopXTitleSize'   :0.06
             ,'TopXTitleOffset' :0.85
             ,'TopXTitleFont'   :42
             ,'TopXLabelSize'   :1.
             ,'TopXLabelOffset' :5.5
             ,'TopXLabelFont'   :42

             ,'TopYTitleSize'   :0.06
             ,'TopYTitleOffset' :1.27
             ,'TopYTitleFont'   :42
             ,'TopYLabelSize'   :0.05
             # TopYLabelOffset?
             ,'TopYLabelFont'   :42
             ,'TopNDiv'         :[5,5,0]

             ,'BotXTitleSize'  :0.14
             ,'BotXTitleOffset':1.0 
             ,'BotXTitleFont'  :42
             ,'BotXLabelSize'  :0.12
             ,'BotXLabelOffset':0.02
             ,'BotXLabelFont'  :42
             ,'BotXTickLength' :.08

             ,'BotYTitleSize'  :0.14
             ,'BotYTitleOffset':0.55 
             ,'BotYTitleFont'  :42
             ,'BotYLabelSize'  :0.12
             # BotYLabelOffset?
             ,'BotYLabelFont'  :42
             ,'BotNDiv'        :[5,5,0]
                                 
             }
        if style == 'DiffXsec' :
            #print 'Using DiffXsec style'
            x['div']  = 0.35
            x['canw'] = 500
            x['canh'] = 365+100
            x['1BottomMargin'] = 0.055
            x['1TopMargin']    = 0.065
            x['2BottomMargin'] = 0.33
            x['2TopMargin']    = 0.1

            x['TopYTitleSize'] = 0.09
            x['TopYTitleOffset'] = 0.86
            x['TopYLabelSize'] = 0.07
            x['TopYLabelOffset'] = 0.01
            x['TopNDiv']       = [5,5,0]

            x['BotXTitleSize'] = 0.15
            x['BotXTitleOffset'] = 0.97
            x['BotXLabelSize'] = 0.14
            x['BotXLabelOffset'] = 0.02

            x['BotYTitleSize']   = 0.17
            x['BotYTitleOffset'] = 0.46
            x['BotYLabelSize']   = 0.14
            x['BotYLabelOffset'] = 0.01

            x['BotNDiv']        = [2,5,0]
            
        if style == 'MoreRatio' :
            #print 'Using MoreRatio style'
            x['div']  = 0.5
            x['canw'] = 500
            x['canh'] = 365+100
            x['1BottomMargin'] = 0.05
            x['1TopMargin']    = .1
            x['2BottomMargin'] = 0.23

            x['TopYTitleSize'] = 0.11
            x['TopYTitleOffset'] = 0.70
            x['TopYLabelSize'] = 0.09 
            x['TopNDiv']       = [5,5,0]
            
            x['BotXTitleSize'] = 0.11
            x['BotXTitleOffset'] = 0.90
            x['BotXLabelSize'] = 0.08
            x['BotXLabelOffset'] = 0.01

            x['BotYTitleSize'] = 0.11
            x['BotYTitleOffset'] = 0.70
            x['BotYLabelSize'] = 0.09
            
        self.ratiocan = TCanvas(self.name+'_r',self.name+'_r',x['canw'],x['canh'])
        self.RatioPadTop = TPad("pad1", "This is the top pad",0.0,x['div'],1.0,1.0,21)
        self.RatioPadTop.SetBottomMargin(x['1BottomMargin'])
        self.RatioPadTop.SetTopMargin(x['1TopMargin'])
        self.RatioPadBot = TPad("pad2", "This is the bottom pad",0.0,0.0,1.0,x['div'],22)
        self.RatioPadBot.SetBottomMargin(x['2BottomMargin'])
        self.RatioPadTop.SetFillColor(0)
        self.RatioPadBot.SetFillColor(0)
        self.RatioPadTop.Draw()
        self.RatioPadBot.Draw()
        self.ratioplots = []
        self.RatioPadTop.cd()
        self.RatioTopPlot0 = self.plots[0].Clone()
        self.RatioTopPlot0.Draw(self.drawopt)
        #
        #
        #
        self.RatioTopPlot0.GetXaxis().SetTitleSize  (x['TopXTitleSize'  ])
        self.RatioTopPlot0.GetXaxis().SetTitleOffset(x['TopXTitleOffset'])
        self.RatioTopPlot0.GetXaxis().SetTitleFont  (x['TopXTitleFont'  ])
        self.RatioTopPlot0.GetXaxis().SetLabelSize  (x['TopXLabelSize'  ])
        self.RatioTopPlot0.GetXaxis().SetLabelOffset(x['TopXLabelOffset'])
        self.RatioTopPlot0.GetXaxis().SetLabelFont  (x['TopXLabelFont'  ])    

        self.RatioTopPlot0.GetYaxis().SetTitleSize  (x['TopYTitleSize'  ])
        self.RatioTopPlot0.GetYaxis().SetTitleOffset(x['TopYTitleOffset'])
        self.RatioTopPlot0.GetYaxis().SetTitleFont  (x['TopYTitleFont'  ])
        self.RatioTopPlot0.GetYaxis().SetLabelSize  (x['TopYLabelSize'  ])
        self.RatioTopPlot0.GetYaxis().SetLabelOffset(x['TopYLabelOffset'])
        self.RatioTopPlot0.GetYaxis().SetLabelFont(x['TopYLabelFont'])
        self.RatioTopPlot0.GetYaxis().SetNdivisions (x['TopNDiv'][0],x['TopNDiv'][1],x['TopNDiv'][2])

        sames = 'sames'
        for p in range(1,len(self.plots)) :
            self.plots[p].Draw(sames+self.drawopt)
            sames = 'sames'
        sames = ''
        for p in nums :
            if p >= len(self.plots) : continue
            if p == den : continue
            self.ratioplots.append(self.plots[p].Clone())
            key = self.ratioplots[-1].GetName()+'_Ratio'
            self.ratioplots[-1].SetNameTitle(key,key)
            #
            # Division options: '' (regular), 'B' (binomial)
            #
            self.ratioplots[-1].Divide(self.ratioplots[-1],self.plots[den],1.,1.,'B' if divide == 'NoErr' else divide)
            if divide == 'NoErr' :
                for i in range(self.ratioplots[-1].GetNbinsX()) :
                    self.ratioplots[-1].SetBinError(i+1,0)
            self.RatioPadBot.cd()
            self.ratioplots[-1].Draw(sames+self.drawopt)

            self.ratioplots[-1].GetXaxis().SetTitleSize  (x['BotXTitleSize'  ])
            self.ratioplots[-1].GetXaxis().SetTitleOffset(x['BotXTitleOffset'])
            self.ratioplots[-1].GetXaxis().SetLabelSize  (x['BotXLabelSize'  ])
            self.ratioplots[-1].GetXaxis().SetLabelOffset(x['BotXLabelOffset'])
            self.ratioplots[-1].GetXaxis().SetTickSize   (x['BotXTickLength' ])

            self.ratioplots[-1].GetYaxis().SetTitleSize  (x['BotYTitleSize'  ])
            self.ratioplots[-1].GetYaxis().SetTitleOffset(x['BotYTitleOffset'])
            self.ratioplots[-1].GetYaxis().SetLabelSize  (x['BotYLabelSize'  ])
            self.ratioplots[-1].GetYaxis().SetLabelOffset(x['BotYLabelOffset'])
            self.ratioplots[-1].GetYaxis().SetNdivisions (x['BotNDiv'][0],x['BotNDiv'][1],x['BotNDiv'][2])

            self.ratioplots[-1].GetYaxis().SetTitle('Ratio')
            self.ratioplots[-1].GetXaxis().SetTitle(self.RatioTopPlot0.GetXaxis().GetTitle())
            sames = 'sames'
            
        self.RatioPadTop.cd()
        self.leg.Draw()
        return

    def SaveAll(self,name='',dir='',can='') :
        if not name : name = self.name
        self.SaveMacro(name=name,can=can,dir=dir)
        self.SavePDF(name=name,can=can,dir=dir)
        self.SavePDF(name=name,can=can,extension='eps',dir=dir)

    def CleanObjectNameForMacro(self,obj) :
        obj.SetName(self.CleanNameForMacro(obj.GetName()))
        obj.SetTitle(self.CleanNameForMacro(obj.GetTitle()))
        return

    def SaveMacro(self,name= '',dir='',can='') :
        if not name : name = self.name
        if name : name = self.CleanNameForMacro(name)
        for p in range(len(self.plots)) :
            self.CleanObjectNameForMacro(self.plots[p])
        self.CleanObjectNameForMacro(self.can)
        if not name : name = self.can.GetName()
        if dir : dir = dir+'/'
        if can == 'ratio' :
            self.CleanObjectNameForMacro(self.ratiocan)
            self.CleanObjectNameForMacro(self.RatioTopPlot0)
            for p in range(len(self.ratioplots)) :
                self.CleanObjectNameForMacro(self.ratioplots[p])
            self.RatioPadTop.Update()
            self.RatioPadBot.Update()
            self.ratiocan.Update()
            self.ratiocan.SaveAs(dir+name+'.C')
            return        
        self.can.Update()
        self.can.SaveAs(dir+name+'.C')
        ##
        ## Things that the macro thing gets wrong:
        ##  - Bottom plot: GetXaxis()->SetTitleOffset()
        return

    def SavePDF(self,name='',extension='pdf',dir='',can='') :
        if not name : name = self.name
        if name : name = self.CleanNameForMacro(name)
        do_epstopdf = (extension == 'pdf' and self.watermark)
        if not name : name = self.CleanNameForMacro(self.can.GetName())
        if do_epstopdf :
            extension = 'eps'
            self.can.SaveAs('%s.%s'%(name,extension))
            import os
            os.system('epstopdf %s.%s'%(name,extension))
            return
        if dir : dir = dir+'/'
        if can == 'ratio' :
            self.ratiocan.SaveAs('%s%s.%s'%(dir,name,extension))
            return
        self.can.SaveAs('%s%s.%s'%(dir,name,extension))
        return

def SmartPlotify(can,name='') :
    return PlotObjectify(can,name=name)

def PlotObjectify(can,name='',drawtitle=True) :
    plots = []
    for i in list(a.GetName() for a in can.GetListOfPrimitives()) :
        if type(can.GetPrimitive(i)) in histtypes :
            plots.append(can.GetPrimitive(i).Clone())
            #print i,'added'
        if type(can.GetPrimitive(i)) == type(TLatex()) :
            name1 = can.GetPrimitive(i).GetTitle()+'_new'

    return PlotObject(name if name else name1,plots,drawopt='',drawtitle=drawtitle)

