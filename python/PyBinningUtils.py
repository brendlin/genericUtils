from itertools import product
from ROOT import TH1F

from genericUtils.PyGenericUtils import MakeListMatrix

#
# Various binning schemes
#
LikelihoodEtaBins = [0.00, 0.60, 0.80, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47]
LikelihoodEtBins         =     [10., 15., 20.,      30.,      40.,      5000.]
LikelihoodEtBins_fine    =     [10., 15., 20., 25., 30., 35., 40., 45., 5000.]
LikelihoodEtBins_7       = [7., 10., 15., 20.,      30.,      40.,      5000.]
LikelihoodEtBins_7_fine  = [7., 10., 15., 20., 25., 30., 35., 40., 45., 5000.]

def binStrToList(the_string) :
    return list(float(a) for a in the_string.split(','))

def getBinName(et,eta,ip=0,iptype='',key='',underscore=True
               ,et_bins=LikelihoodEtBins,eta_bins=LikelihoodEtaBins):
    filestr =  ('_' if underscore else '')+(key+'_' if key else '')
    if not iptype :
        filestr += 'et%deta%2.2f' % (int(et_bins[et]), eta_bins[eta])
    else :
        filestr += '%s%02det%deta%2.2f' % (iptype, ip_bins[ip], int(et_bins[et]), eta_bins[eta])
    return filestr

def getetabin(eta,eta_bins=LikelihoodEtaBins,absval=True) :
    for i in range(len(eta_bins)-1) :
        if absval : eta = abs(eta)
        if eta_bins[i] <= eta and eta <= eta_bins[i+1] :
            return i
    return len(eta_bins)

def getetbin(et,et_bins=LikelihoodEtBins) :
    for i in range(len(et_bins)-1) :
        if et_bins[i] <= et and et <= et_bins[i+1] :
            return i
    return len(et_bins)-2 # NOTE THE SHIFT HERE!

#----------------------------------------------------
def Hists1dBinnedEtEta(title,a,et_bins=LikelihoodEtBins,eta_bins=LikelihoodEtaBins) :
    bins = [range(len(et_bins[:-1])),range(len(eta_bins[:-1]))]
    bins2 = [et_bins[:-1],eta_bins[:-1]]
    hists = MakeListMatrix(*bins2)
    for i in product(*bins) :
        et,eta = i[0],i[1]
        h_name  = title.split(';')[0]+getBinName(et,eta,et_bins=et_bins,eta_bins=eta_bins)
        h_title = ';'.join([h_name]+title.split(';')[1:])
        hists[et][eta] = TH1F(h_name,h_title.replace('_',' '),a[0],a[1],a[2])
    return hists

# --------------------------------------------
def MultiBin2dHistograms(title,a,b,et_bins=LikelihoodEtBins,eta_bins=LikelihoodEtaBins) :
    bins = [range(len(et_bins[:-1])),range(len(eta_bins[:-1]))]
    bins2 = [et_bins[:-1],eta_bins[:-1]]
    hists = MakeListMatrix(*bins2)
    for i in product(*bins) :
        et,eta = i[0],i[1]
        h_name = title.split(';')[0]+getBinName(et,eta,et_bins=et_bins,eta_bins=eta_bins)
        h_title = ';'.join([h_name]+title.split(';')[1:])
        hists[et][eta] = TH2F(h_name,h_title.replace('_',' '),a[0],a[1],a[2],b[0],b[1],b[2])
    return hists

# --------------------------------------------
def MultiBin1dHistograms(title,a,et_bins=LikelihoodEtBins,eta_bins=LikelihoodEtaBins) :
    bins = [range(len(et_bins[:-1])),range(len(eta_bins[:-1]))]
    bins2 = [et_bins[:-1],eta_bins[:-1]]
    hists = MakeListMatrix(*bins2)
    for i in product(*bins) :
        et,eta = i[0],i[1]
        h_name  = title.split(';')[0]+getBinName(et,eta,et_bins=et_bins,eta_bins=eta_bins)
        h_title = ';'.join([h_name]+title.split(';')[1:])
        hists[et][eta] = TH1F(h_name,h_title.replace('_',' '),a[0],a[1],a[2])
    return hists
