Contact: kurt.brendlinger@cern.ch

Usage for the plotting script plottrees.py:

plottrees.py is a generic script for making stack histograms from MC and data. The general idea is
that you make a simple steering file to control the basic content and style of the plot, and
all the formatting is done in the background.

The main two files are:
 - macros/plottrees.py
 - python/PyAnalysisPlotting.py

These reference files that manipulate histogram cosmetics:
 - PlotFunctions.py
 - TAxisFunctions.py

Usage: Say you have a data file data1.root and background files (files that you want to stack) wz and
ww. Then (note that ".root" is not required):

python plottrees.py --data data1 --bkgs wz,ww --variable ph_pt --treename HZG_Tree

The plot labels are controlled by the names of the files. If you have huge file names, you can
use "ln -s my_long_filename.root blah.root" to make a soft link to a smaller name.

Now add a cut:

python plottrees.py --data data1 --bkgs wz,ww --variable ph_pt --cuts 'ph_eta < 2.47'

Say you want control over the histogram bins / ranges. Specify --limits 100,0,200 for 100 bins and
a histogram range [0,100].

Now imagine you want to add a signal sample, but you don't want to stack it. Do --signal ggF.root

For a ratio plot of stacked background to data, use --ratio.

For log scale, use --log.

To save to a .pdf and .C file, do --save.

You may have noticed that your MC needs to be normalized somehow. Typically this is pretty specific
to what ntuple you are using. There are two types of weights: an event weight, and a scalar associated
with the sample (xsec, feff, etc) -- here called the weightscale. The weight is a branch or product
of branches from the tree (e.g. --weight mc_weight_final), whereas the weightscale info is usually
stored in histograms in the file or something. To get the weight scale, you can write a small python
function that takes the file as an input, and spits out the scale. (For an example see
the implementation "weightscaleHZY(tfile)" in PyAnalysisPlotting.py.) Then you would specify
"--weightscale HZY" to point to that function. Finally, use --fb to indicate the integrated luminosity.

Finally, you might want to plot lots of variables quickly, and store the parameters of the plot
somewhere. For this you make config file (called e.g. UserInput.py), and point to it using
--config UserInput.py . In that file, you can specify the following parameters:
 - histformat (dict) entries e.g. 'pt':[100,0,200,'p_{T}'] -- this is basically --limits, plus the x-axis title.
 - rebin (dict) entries e.g. 'pt':[0,50,100,200] -- if you want non-fixed bin widths.
 - cuts (list) -- specify a list of cuts.
 - colors (dict) entries e.g. 'wz':ROOT.kGreen -- a dictionary of colors for your backgrounds.
 - blindcut (list) for blinding the data - same format as cuts
 - treename (string)
 - fb (float)
 - weight (string) applied on the tree
 - weightscale (function, with TFile as input) - for getting sample normalization like sumw from histos

There's another option, if you want to group (merge) samples into a larger sample (say, merge
4 sliced eegamma samples into one eeg sample. You can do this using a "mergesamples" dict in the 
config file: 
 - mergesamples -- a dictionary for merging sub-samples into larger samples, e.g.
   'eeg':['eeg1','eeg2','eeg3','eeg4']

