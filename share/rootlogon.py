#from ROOT import gStyle,TColor
from ROOT import gStyle,TColor,ROOT
from array import array
#gStyle.SetStatColor(0)
#gStyle.SetTitleColor(0)
#gStyle.SetCanvasColor(0)
#gStyle.SetPadColor(0)
#gStyle.SetPadBorderMode(0)
#gStyle.SetCanvasBorderMode(0)
#gStyle.SetFrameBorderMode(0)
gStyle.SetOptStat(0)
#gStyle.SetStatH(0.3)
#gStyle.SetStatW(0.3)
gStyle.SetTitleColor(1)
gStyle.SetTitleFillColor(0)
#gStyle.SetTitleY(1.)
#gStyle.SetTitleX(.1)
gStyle.SetTitleBorderSize(0)
#gStyle.SetHistLineWidth(2)
#gStyle.SetLineWidth(2)
#gStyle.SetFillColor(0)
#gStyle.SetFrameFillColor(0)
gStyle.SetOptTitle(0)

def set_palette(name="palette", ncontours=255):
    """Set a color palette from a given RGB list
    stops, red, green and blue should all be lists of the same length
    see set_decent_colors for an example"""
    
    if name == "gray" or name == "grayscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.84, 0.61, 0.34, 0.00]
        green = [1.00, 0.84, 0.61, 0.34, 0.00]
        blue  = [1.00, 0.84, 0.61, 0.34, 0.00]
    elif name == "rgb" :
        print "doing rgb"
        stops = [0.00, 0.50, 1.00]
        red   = [1.00, 0.00, 0.00]
        green = [0.00, 1.00, 0.00]
        blue  = [0.00, 0.00, 1.00]
    elif name == "rb" :
        print "doing rb"
        stops = [0.00, 1.00]
        red   = [1.00, 0.00]
        green = [0.00, 0.00]
        blue  = [0.00, 1.00]
    elif name == "mygray" :
        print "doing mygray"
        stops = [0.00, 1.00]
        red   = [1.00, 0.00]
        green = [1.00, 0.00]
        blue  = [1.00, 0.00]
    elif name == "rwb" :
        print "doing rwb"
        stops = [0.00, 0.50, 1.00]
        red   = [0.00, 1.00, 1.00]
        green = [0.00, 1.00, 0.00]
        blue  = [1.00, 1.00, 0.00]
    elif name == "xgy" :
        print "doing xgy"
        stops = [0.00, 0.50, 1.00]
        red   = [0.00, 0.50, 1.00]
        green = [0.00, 1.00, 0.00]
        blue  = [1.00, 0.50, 0.00]
    else:
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00]
        
    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)
        
    npoints = len(s)
    TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    gStyle.SetNumberContours(ncontours)

set_palette("xgy",100)
gStyle.SetPadTopMargin(0.1)

def doColz():
    gStyle.SetPadRightMargin(0.18)
