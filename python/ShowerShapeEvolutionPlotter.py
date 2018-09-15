import ROOT
import PlotFunctions as plotfunc

#
# Given a list of histograms (e.g. binned vs Pt), plot each on top of one another.
# The first histogram is plotted on the bottom. Given multiple lists of histograms, a histogram from
# each list will be plotted on top of one another.

def ShowerShapeEvolutionPlot(can,labels,plotset1,
                             plotset2=None,plotset3=None,plotset4=None,plotset5=None,plotset6=None) :

    all_plotsets = []
    for others in [plotset1,plotset2,plotset3,plotset4,plotset5,plotset6] :
        if others :
            all_plotsets.append(others)

    # Check that everything is the same length
    for plotset in all_plotsets :
        if len(plotset) != len(labels) :
            print 'Error in ShowerShapeEvolutionPlot: Mismatched lengths!'
            return

    #
    # make the background 2d plot for labeling of the y-axis
    #
    sample_plot = all_plotsets[0][0]
    plot2d_for_ylabels = ROOT.TH2F('plot2d_for_ylabels','remove',
                                   sample_plot.GetNbinsX(),
                                   sample_plot.GetXaxis().GetBinLowEdge(1),
                                   sample_plot.GetXaxis().GetBinLowEdge(sample_plot.GetNbinsX()+1),
                                   len(all_plotsets[0]),0,len(all_plotsets[0]))

    for i in range(plot2d_for_ylabels.GetNbinsY()) :
        plot2d_for_ylabels.GetYaxis().SetBinLabel(i+1,labels[i])

    plotfunc.AddHistogram(can,plot2d_for_ylabels,drawopt='colz')
    plotfunc.FormatCanvasAxes(can)

    #
    # Find the histogram with the largest peak relative to its integral
    #
    integral_lp       = [-1]*len(all_plotsets[0])
    index_lp          = [-1]*len(all_plotsets[0])
    max_over_integral = [ 0]*len(all_plotsets[0])
    for j,plotset in enumerate(all_plotsets) :
        for i,plot in enumerate(plotset) :
            if not plot.Integral() or not plot.GetMaximum() :
                continue
            tmp_max_over_integral = plot.GetMaximum()/float(plot.Integral(0,plot.GetNbinsX()+1))
            if tmp_max_over_integral > max_over_integral[i] :
                max_over_integral[i] = tmp_max_over_integral
                tmp_scale = 0.9/float(plot.GetMaximum())
                integral_lp[i] = plot.Integral(0,plot.GetNbinsX()+1)*tmp_scale
                index_lp[i] = j

    #
    # Add the histograms
    # Scale the histograms and offset them by 1
    #
    for j,plotset in enumerate(all_plotsets) :
        for i,plot in enumerate(plotset) :
            if not plot.Integral() or not plot.GetMaximum() :
                continue
            drawopt = 'hist'
            if plot.GetOption() :
                drawopt = plot.GetOption()
            plot_copy = plotfunc.AddHistogram(can,plot,drawopt)

            # Scale either to 0.9 of maximum, or to
            # the integral of the hist with the highest maximum relative to its integral
            if index_lp[i] == j :
                plot_copy.Scale(0.9/float(plot_copy.GetMaximum()))
            else :
                plot_copy.Scale(integral_lp[i]/float(plot_copy.Integral(0,plot_copy.GetNbinsX()+1)))

            # Y-axis offset
            for bin in range(plot_copy.GetNbinsX()) :
                plot_copy.SetBinContent(bin+1,i + plot_copy.GetBinContent(bin+1))

    #
    # Remove duplicate plot titles (= legend entries)
    #
    plottitles = []
    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetTitle') and i.GetTitle() in plottitles :
            i.SetTitle('remove')
        else :
            plottitles.append(i.GetTitle())

    #
    # Final details
    #
    can.SetTopMargin(0.13)
    plotfunc.SetLeftMargin(can,0.27)
    plotfunc.SetAxisLabels(can,sample_plot.GetXaxis().GetTitle(),'')
    can.SetGridy()
    plotfunc.MakeLegend(can,0.7,0.88,0.9,0.99,totalentries=2)

    can.Modified()
    can.Update()

    return
