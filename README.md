genericUtils - An Introduction to the Package
================

Contact: kurt.brendlinger@cern.ch

This package contains the following scripts:

 - **macros/plottrees.py**
   - A generic script for making stacked histograms comparing MC and data.
 - **macros/makePicoXaod.py**
   - This script allows you to make a smaller version of an existing flat ntuple.


**plottrees.py** - Description and Instructions
==================

### What is it

plottrees.py is a generic script for making stacked histograms from MC and data. The general idea is
that you make a simple steering file to control the basic content and style of the plot, and
all the formatting is done in the background.

The main two files are:
 - macros/plottrees.py
 - python/PyAnalysisPlotting.py

These reference files that manipulate histogram cosmetics:
 - PlotFunctions.py
 - TAxisFunctions.py

### How to run it

Say you have a data file `data1.root` and background files (files that you want to stack) `wz.root` and
`ww.root`. Then (note that ".root" is not required):

    python plottrees.py --data data1 --bkgs wz,ww --variable ph_pt --treename HZG_Tree

The plot labels are controlled by the names of the files. If you have huge file names, you can
use "ln -s my_long_filename.root blah.root" to make a soft link to a smaller name.

Now add a cut:

    python plottrees.py --data data1 --bkgs wz,ww --variable ph_pt --cuts 'ph_eta < 2.47'

More command-line options:

 - **--limits 100,0,200**: If you want control over the histogram bins / ranges. Specify 100,0,200 for 100 bins and a histogram range [0,200].
 - **--signal ggF.root**: For if you want to add a signal sample, but you don't want to stack it with the rest of the MC.
 - **--ratio**: Use this to create a ratio pad of data divided by the stacked background, underneath the main pad.
 - **--log**: Use this to specify a log scale.
 - **--save**: Use this to save to a .pdf and .C file.
 - **--plottext**: (list of strings) - to add some text to the plot, underneath ATLAS Internal

### Normalizing MC

You may have noticed that your MC needs to be normalized somehow. Typically this is pretty specific
to what ntuple you are using. There are two types of weights: an event weight, and a scalar associated
with the sample (xsec, feff, etc) -- here called the **weightscale**. The **weight** is a branch or product
of branches from the tree (e.g. --weight mc_weight_final), whereas the **weightscale** info is usually
stored in histograms in the file or something. To get the weight scale, you can write a small python
function that takes the file as an input, and spits out the scale. (For an example see
the implementation `weightscaleHZY(tfile)` in PyAnalysisPlotting.py.) Then you would specify
`--weightscale HZY` to point to that function. Finally, use `--fb 3.2` to indicate the integrated luminosity
that you want to normalize the MC to.

### Storing plottrees details in a config file

Finally, you might want to plot lots of variables quickly, and store the parameters of the plot
somewhere. For this you make config file (called e.g. UserInput.py), and point to it using
`--config UserInput.py`. In that file, you can specify the following parameters:
 - **histformat** (dict) entries e.g. 'pt':[100,0,200,'p_{T}'] -- this is basically --limits, plus the x-axis title.
 - **rebin** (dict) entries e.g. 'pt':[0,50,100,200] -- if you want non-fixed bin widths.
 - **cuts** (list) -- specify a list of cuts.
 - **colors** (dict) entries e.g. 'wz':ROOT.kGreen -- a dictionary of colors for your backgrounds.
 - **blindcut** (list) for blinding the data - same format as cuts
 - **treename** (string): the name of the tree
 - **fb** (float): the integrated luminosity
 - **weight** (string): the location of weight branches in the tree
 - **weightscale** (function, with TFile as input) - for getting sample normalization like sumw from histos
 - **plottext** (list of strings) - to add some text to the plot, underneath ATLAS Internal

There's another option, if you want to group (merge) samples into a larger sample (say, merge
4 sliced eegamma samples into one eegamma sample. You can do this using a "mergesamples" dict in the 
config file: 
 - **mergesamples** -- a dictionary for merging sub-samples into larger samples, e.g.
   'eeg':['eeg1','eeg2','eeg3','eeg4']

### New! Regular expressions

Now you can specify certain command-line (or config) options using regular expressions (use "%" instead of ".*"):
 - **--bkgs**, **--signal** and **--data**
 - **labels** (the dict in the conf file - the key can use regexp. Works for bkg, signal and data)
 - **mergesamples** (the dict in the conf file - specify a regexp string instead of a list of strings)

**makePicoXaod.py** - Description and Instructions
==================

### What is it

This script, which lives inside genericUtils,
allows you to skim a generic flat ntuple
into much smaller ntuples that can e.g. be saved on your computer. The script can be
steered using a combination of command-line options (or these options can be stored
in a config file and specified using the **--config** option). The options are:

 - **--bkgs**: a string of comma-separated file names for your MC
 - **--data**: a string of comma-separated file names for your data
 - **--treename**: The name of the tree that you want to skim
 - **--cuts**: Any cuts that you want to apply. In the command prompt, specify as a string. In the conf, specify as a list of strings (one for each cut).
 - **--blindcut**: Events that you want to *exclude* because they're in your blinded SR.
 - **--truthcuts**: Cuts on truth-level quantities (e.g. only applied to MC)
 - **--outdir**: The output directory to save the picoXaod files in.
 - **--variables**: Comma-separated list of variables you want to save.

### How to run it

The following command is an example of how to run this script:

    makePicoXaod.py --config conf.py --bkgs eeg.root,mmg.root,ttg.root --outdir MyOutputDir

The output files will have the same name as the input files, with "_pico.root" at the end, and stored
in the directory specified by **--outdir**.

**cutcomparisons.py** - Description and Instructions
==================

This macro offers a way to compare different cut selection. Right now it only works for --signal MC.
To use it, make a config file and define inside a list called "cutcomparisons", e.g. to compare
different channels:

    cutcomparisons = [
        ['#mu#mu#gamma'      ,'HGamEventInfoAuxDyn.yyStarChannel == 1']
        ['ee#gamma resolved' ,'HGamEventInfoAuxDyn.yyStarChannel == 2']
        ['ee#gamma merged'   ,'HGamEventInfoAuxDyn.yyStarChannel == 3']
        ['ee#gamma ambiguous','HGamEventInfoAuxDyn.yyStarChannel == 4']
        ]

Note that the first element of the list corresponds to the name of the selection, and the subsequent
cuts are applied as usual.
Then run e.g. the following:

    cutcomparisons.py --signal %gamstargam%r9364%.root --config cutcomparisons_Channels.py

The cuts defined in the "cuts" option can/will still be applied on top, as a preselection to the
cuts specified in "cutcomparisons".

**PlotFunctions** and **TAxisFunctions** - Description and Instructions
==================

### What is it

The functions in `Plotfunctions` and `TAxisFunctions` are meant to be helpers to construct
a nice-looking canvas. They are also *functions*, meaning that you can pick and choose which
functions you want to use, and if you want to do something else with your TCanvas then you
can still use it like a regular TCanvas. The functions are meant to be short, so that you can
look inside the code to see what they are doing. (This way you will see what other options there
are too.)

### How to use it in your code (python or C++)

Note that there are examples of how to use these tools - see `python/UnitTestPlot.py` for a
python version and `util/UnitTestPlotCpp.C` for a C++ version.

If you want to start out with decent defaults, then before you do anything, do (note: this is python. If using c++, see the c++ setup below):

 - **SetupStyle**()

Then make your TCanvas as usual. You can also make a `RatioCanvas`
(a TCanvas with a 'pad_top' and a 'pad_bot' which will be useful for ratio canvases).
RatioCanvases have custom functions in this package (for instance you can use `AddRatio` to add a histogram plus its ratio to another histogram).
 
 - c = TCanvas(name,title,canw,canh)
 - c = RatioCanvas(name,title,canw,canh,ratio_size_as_fraction)

Tools to add histograms to a normal canvas:

 - **AddHistogram**(can,hist)

If you have a RatioCanvas, you can use:

 - **AddHistogramTop**(can,hist)
 - **AddHistogramBot**(can,hist)
 - **AddRatio**(can,hist,ref_hist)
 - **AddRatioManual**(can,hist,ratioplot,drawopt1='pE1',drawopt2='pE1')

**Once you have added all the histograms**, you can use the following to manipulate the content in the canvas:

 - **FullFormatCanvasDefault**(can,lumi=36.1,sqrts=13,additionaltext=,preliminary=False)
 - **ConvertToDifferential**(hist)
 - **SetAxisLabels**(can,xlabel,ylabel)
 - **SetColors**(can,[color1,color2,color3...])
 - **SetMarkerStyles**(can,these_styles=[],these_sizes=[])
 - **MakeLegend**(can,x1,x2,y1,y2,...)
 - **FormatCanvasAxes**(can,options...) - must be run AFTER the first histograms are added!
 - **SetLeftMargin**(can,margin), SetRightMargin(can,margin)
 - **GetTopPad**(can), **GetBotPad**(can)
 - **Stack**(can,reverse=False)
 - **ColorGradient**(i,ntotal)
 - **SetColorGradient**(name='MyThermometer')

Tools for adding text:

 - **DrawText**(can,text,x1,y1,x2,y2,...)
 - **GetLuminosityText**(lumi)
 - **GetSqrtsText**(sqrts)
 - **GetAtlasInternalText**(status='Internal')

### C++ Setup

You first need to compile the macros:

```
cd genericUtils/genericUtils
root -l
.L TAxisFunctions.cxx++
.L PlotFunctions.cxx++
.q
```

Then instead of calling `root -l myScript.C`, you must do (you must change the file path to the correct one):

```
gSystem->Load("$HOME/genericUtils/genericUtils/TAxisFunctions_cxx.so");
gSystem->Load("$HOME/genericUtils/genericUtils/PlotFunctions_cxx.so");
.L myScript.C
myScript()
```

Or, if that's too much to type every time, you can load them by default when you start root.
Do this by first creating a "$HOME/.rootrc" file, or (if it exists) make sure it has the following line in it:

```
Rint.Logon:          $(HOME)/rootlogon.C
```

Then make a "$HOME/rootlogon.C" file that looks like this:

```
void rootlogon()
{
  gSystem->Load("$HOME/genericUtils/genericUtils/TAxisFunctions_cxx.so");
  gSystem->Load("$HOME/genericUtils/genericUtils/PlotFunctions_cxx.so");
}
```

Then you can simply call `root -l myScript.C` like before.

### Use with AnalysisBase

You should also be able to use genericUtils with AnalysisBase. 
It should be compatible with nearly every AnalysisBase release, since it's relatively vanilla ROOT code.
Here there is no special instruction -- simply check
out the package where you have checked out your other packages, and compile! Then you can do:

```
#include "genericUtils/PlotFunctions.h"
#include "genericUtils/TAxisFunctions.h"
```

