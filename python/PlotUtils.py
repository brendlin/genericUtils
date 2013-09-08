from ROOT import TCanvas,TLegend,TGraph,TGraphErrors,TH1F,gROOT,TF1,TH1
from ROOT import TLine,TMath,TPad,gStyle,TROOT,TText,TProfile,TH2F,TH1D
from ROOT import kRed,kMagenta,kBlue,kCyan,kGreen,kGray,kBlack,kOrange,kYellow,kAzure
from ROOT import TLatex,TAxis,TASImage,kTRUE
#import AtlasStyle
from array import array
gROOT.SetBatch(True)

#
# TH1.SetDefaultSumw2(kTRUE) - very important for correctly plotting
# and calculating errors. For instance "Scale" will mess up your
# errors if this is not set to True.
#
TH1.SetDefaultSumw2(kTRUE)

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

markerstyles = [20,21,22,23,24,25,26,27]

graphtypes = [type(TGraph()),type(TGraphErrors())]
histtypes = [type(TH1F()),type(TH1D()),type(TProfile()),type(TH2F())]
formulatypes = [type(TF1())]
h1types = [type(TH1F()),type(TH1D()),type(TProfile())]
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
              ,normalized=False,writecan=False,log=False,drawleg=True) :
    return PlotObject(name,plots,file=file,dir=dir
                      ,drawopt=drawopt,ranges=ranges,legendpos=legendpos,markersize=markersize
                      ,markerstyle=markerstyle,drawtitle=drawtitle
                      ,normalized=normalized,writecan=writecan,log=log,drawleg=drawleg)

class PlotObject :
    def __init__(self,name,plots,file=0,dir=''
                 ,drawopt='E1',ranges=0,legendpos='topright',markersize=1.0
                 ,markerstyle=20,drawtitle=True
                 ,normalized=False,writecan=False,log=False,drawleg=True
                 ,canw=500,canh=500
                 ,watermark=False) :

        # ranges : [[xmin,xmax],[ymin,ymax]]
        # i.e. [None,[.84,1.02]]
        
        self.dir = dir
        self.name = name
        self.can = TCanvas(name,name,canw,canh)
        self.canw = canw
        self.canh = canh
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
        self.watermark = watermark
        self.drawopts = []

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

    def createLegend(self,x1,y1,x2,y2,can='') :
        #print x1,y1,x2,y2
        if can == 'ratio' :
            if self.ratiopad1.GetPrimitive('mylegend') :
                self.ratiopad1.GetPrimitive('mylegend').Delete()
        else :
            if self.can.GetPrimitive('mylegend') :
                self.can.GetPrimitive('mylegend').Delete()
        self.leg = TLegend(x1,y1,x2,y2)
        self.leg.SetName('mylegend')
        self.leg.SetTextFont(42)
        self.leg.SetBorderSize(0)
        self.leg.SetFillStyle(0)
        
    def recreateLegend(self,x1,y1,x2,y2,can='') :

        self.createLegend(x1,y1,x2,y2,can=can)
        self.SetLegend()
        if ('colz' not in self.drawopt) and self.drawleg :
            self.can.cd()
            if can == 'ratio' :
                self.ratiopad1.cd()
            self.leg.Draw()
        return

    def DrawHorizontal(self,yval,color=1,pct=[0.,1.],style=1) :
        self.can.cd()
        a = TLine()
        a.SetLineColor(color)
        a.SetLineStyle(style)
        a.SetLineWidth(2)
        a.DrawLine((self.xmax-self.xmin)*pct[0]+self.xmin,yval,(self.xmax-self.xmin)*pct[1]+self.xmin,yval)

    def DrawVertical(self,xval,color=1,pct=[0.,1.],style=1) :
        self.can.cd()
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
        t.DrawLatex(x,y,text)

    def DrawTextNDC(self,x,y,text,angle=0,align='',size=0.035) :
        self.can.cd()
        t = TLatex()
        t.SetNDC()
        t.SetTextSize(0.04)
        t.SetTextFont(42)
        if align == 'R': t.SetTextAlign(31)
        if angle : t.SetTextAngle(angle)
        t.DrawLatex(x,y,text)

    def SetAxisLabels(self,xlabel,ylabel) :
        if len(self.plots) :
            self.plots[0].GetXaxis().SetTitle(xlabel)
            self.plots[0].GetYaxis().SetTitle(ylabel)

    def CleanNameForMacro(self,nm) :
        return ''.join(ch for ch in nm if ch.isalnum())

    def MakeRatioPlot(self,den,nums) :
        #
        # You can use self.ratioplots[0].GetYaxis().SetNdivisions(5,5,0)
        # to change the ticks.
        #

        self.ratiocan = TCanvas(self.name+'_r',self.name+'_r',self.canw,self.canh+100)
        self.ratiopad1 = TPad("pad1", "The pad 80% of the height",0.0,0.3,1.0,1.0,21)
        self.ratiopad1.SetBottomMargin(.020)
        self.ratiopad1.SetFillColor(0)
        self.ratiopad2 = TPad("pad2", "The pad 20% of the height",0.0,0.0,1.0,0.3,22)
        self.ratiopad2.SetBottomMargin(0.30)
        self.ratiopad2.SetFillColor(0)
        self.ratiopad1.Draw()
        self.ratiopad2.Draw()
        self.ratioplots = []
        self.ratiopad1.cd()
        self.ratioplot0 = self.plots[0].Clone()
        self.ratioplot0.Draw(self.drawopt)
        #
        #
        #
        self.ratioplot0.GetXaxis().SetLabelOffset(1.5)

        self.ratioplot0.GetYaxis().SetTitleOffset(1.27)
        self.ratioplot0.GetYaxis().SetTitleSize(0.06)
        self.ratioplot0.GetYaxis().SetTitleFont(42)
        self.ratioplot0.GetYaxis().SetLabelSize(0.05)
        self.ratioplot0.GetYaxis().SetLabelFont(42)

        self.ratioplot0.GetXaxis().SetTitleOffset(0.85)
        self.ratioplot0.GetXaxis().SetTitleSize(0.06)
        self.ratioplot0.GetXaxis().SetTitleFont(42)
        self.ratioplot0.GetXaxis().SetLabelSize(0.05)
        self.ratioplot0.GetXaxis().SetLabelFont(42)


        sames = 'sames'
        for p in range(1,len(self.plots)) :
            self.plots[p].Draw(sames+self.drawopt)
            sames = 'sames'
        sames = ''
        for p in nums :
            self.ratioplots.append(self.plots[p].Clone())
            key = self.ratioplots[-1].GetName()
            self.ratioplots[-1].SetNameTitle(key,key)
            self.ratioplots[-1].Divide(self.plots[den])
            self.ratiopad2.cd()
            self.ratioplots[-1].Draw(sames+self.drawopt)
            self.ratioplots[-1].GetYaxis().SetTitle('Ratio')
            self.ratioplots[-1].GetYaxis().SetLabelSize(0.12)
            self.ratioplots[-1].GetYaxis().SetTitleSize(0.14)
            self.ratioplots[-1].GetYaxis().SetTitleOffset(.55)
            self.ratioplots[-1].GetXaxis().SetTitle(self.ratioplot0.GetXaxis().GetTitle())
            self.ratioplots[-1].GetXaxis().SetLabelSize(0.12)
            self.ratioplots[-1].GetXaxis().SetLabelOffset(0.02)
            self.ratioplots[-1].GetXaxis().SetTitleSize(0.14)
            self.ratioplots[-1].GetXaxis().SetTitleOffset(1.0)
            sames = 'sames'

        self.ratiopad1.cd()
        self.leg.Draw()
        return

    def SaveMacro(self,name= '',dir='',can='') :
        for p in range(len(self.plots)) :
            key = self.CleanNameForMacro(self.plots[p].GetName())
            self.plots[p].SetName(key)
            key = self.CleanNameForMacro(self.plots[p].GetTitle())
            self.plots[p].SetTitle(key)
        self.can.SetName(self.CleanNameForMacro(self.can.GetName()))
        self.can.SetTitle(self.CleanNameForMacro(self.can.GetTitle()))
        if not name : name = self.can.GetName()
        if dir : dir = dir+'/'
        if can == 'ratio' :
            self.ratiocan.SaveAs(dir+name+'.C')
            return        
        self.can.SaveAs(dir+name+'.C')
        return

    def SavePDF(self,name='',extension='pdf',dir='',can='') :
        do_epstopdf = (extension == 'pdf' and self.watermark)
        print name
        if not name : name = self.CleanNameForMacro(self.can.GetName())
        if do_epstopdf :
            extension = 'eps'
            print 'saving as %s.%s'%(name,extension)
            self.can.SaveAs('%s.%s'%(name,extension))
            import os
            os.system('epstopdf %s.%s'%(name,extension))
            return
        if dir : dir = dir+'/'
        print 'saving as %s%s.%s'%(dir,name,extension)
        if can == 'ratio' :
            self.ratiocan.SaveAs('%s%s.%s'%(dir,name,extension))
            return
        self.can.SaveAs('%s%s.%s'%(dir,name,extension))
        return

def SmartPlotify(can,name='') :
    return PlotObjectify(can,name=name)

def PlotObjectify(can,name='') :
    plots = []
    for i in list(a.GetName() for a in can.GetListOfPrimitives()) :
        if type(can.GetPrimitive(i)) in histtypes :
            plots.append(can.GetPrimitive(i).Clone())
        if type(can.GetPrimitive(i)) == type(TLatex()) :
            name1 = can.GetPrimitive(i).GetTitle()+'_new'

    return PlotObject(name if name else name1,plots,drawopt='')

