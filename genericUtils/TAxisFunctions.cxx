#include "TAxisFunctions.h"

#include <algorithm>
#include <math.h>
#include <iostream>

#include "TF1.h"
#include "TH1.h"
#include "TGraph.h"
#include "THStack.h"
#include "TPave.h"
#include "TText.h"
#include "TGraphErrors.h"
#include "TGraphAsymmErrors.h"

namespace GU {

  //
  // This function will fit all of the histgram bin content, or TGraph points on a plot.
  // If a text or legend has been added to the plot it will force the plot content to appear BELOW
  // the text.
  //
  void AutoFixAxes(TPad& can, bool symmetrize, bool ignorelegend) {
    if (can.GetPrimitive("pad_top")) {
      TPad * pad_top = (TPad*)can.GetPrimitive("pad_top");
      TPad * pad_bot = (TPad*)can.GetPrimitive("pad_bot");
      AutoFixAxes(*pad_top,symmetrize,ignorelegend);
      AutoFixAxes(*pad_bot,symmetrize,ignorelegend);
      return;
    }
    FixXaxisRanges(can);
    AutoFixYaxis(can,ignorelegend=ignorelegend);
    return;
  }

  std::pair<double,double> AutoFixYaxis(TPad& can, bool ignorelegend,float forcemin,bool minzero)
  {
    //
    // Makes space for text as well!
    //
    can.Update();

    std::pair<double,double> yranges = GetYaxisRanges(can,true);

    // maxy_frac is the fractional maximum of the y-axis stuff.
    double maxy_frac = 1;

    if (!CanvasHasPlot(can)) {
      std::cout << Form("Your plot %s has nothing in it. AutoFixYaxis() is Doing nothing.",can.GetName())
                << std::endl;
      return yranges;
    }

    //
    // Now we make space for any text we drew on the canvas, and
    // also the Legend
    //
    double tframe_height = 1 - can.GetTopMargin() - can.GetBottomMargin();

    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next()))
    {
      if (ignorelegend && prim->InheritsFrom("TLegend")) continue;
      if (ignorelegend && prim->InheritsFrom("TFrame")) continue;

      if (prim->InheritsFrom("TPave")) {
        maxy_frac = std::min( maxy_frac, ((TPave*)prim)->GetY1NDC() );
      }
      if (prim->InheritsFrom("TText")) {
        maxy_frac = std::min( maxy_frac, ((TText*)prim)->GetY() );
      }
    }

    if (yranges.first == FLT_MAX && yranges.second == -FLT_MAX) {
      return yranges;
    }

    yranges.first  = ((yranges.first  > 0) ? 0.95 : 1.05) * yranges.first ;
    yranges.second = ((yranges.second > 0) ? 1.05 : 0.95) * yranges.second;

    maxy_frac = maxy_frac - can.GetBottomMargin();

    if (maxy_frac < 0) {
      std::cout << "Error in AutoFixAxes - somehow there is no more room for your plot."
                << "(Bad legend placement?)" << std::endl;
      return yranges;
    }

    if (can.GetLogy()) {

      // special treatment for log plots
      yranges.first = 0.85*MinimumForLog(can);

      // some orders of magnitude *above* yranges.first, making room for text
      double orderofmagnitude_span = log( yranges.second/yranges.first ) / log(10);
      orderofmagnitude_span = 1.1*orderofmagnitude_span*tframe_height/maxy_frac;
      yranges.second = yranges.first * pow(10,orderofmagnitude_span);

    } else {

      // scale to make space for text
      maxy_frac = maxy_frac - 0.02;
      yranges.second = tframe_height*(yranges.second-yranges.first)/float(maxy_frac) + yranges.first;

      // round y axis to nice round numbers
      yranges = NearestNiceNumber(yranges);

    }

    if (minzero) yranges.first = 0;
    if (forcemin > 2*FLT_MIN) yranges.first = forcemin;

    SetYaxisRanges(can,yranges.first,yranges.second);
    return yranges;

  }

  //
  // Snap to base-ten-centric numbers
  //
  std::pair<double,double> NearestNiceNumber(std::pair<double,double> ranges_in) {

    std::pair<double,double> ranges_out;

    double round_number = 10; // or 5 perhaps
    double smallest_increment = pow(10, floor(log((ranges_in.second-ranges_in.first))/log(10))-2 );

    ranges_out.first  = round_number*smallest_increment*floor(ranges_in.first /(round_number*smallest_increment));
    ranges_out.second = round_number*smallest_increment*ceil (ranges_in.second/(round_number*smallest_increment));

    return ranges_out;
  }

  //
  // Find the non-zero y-axis minimum of plot content.
  //
  double MinimumForLog(TPad& can) {

    double ymin = FLT_MAX;

    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next()))
    {
      if (prim->InheritsFrom("TGraph")) {
        for (int i=0;i<((TGraph*)prim)->GetN();++i) {
          double y = ((TGraph*)prim)->GetY()[i];
          if (y <= 0) continue;
          ymin = std::min(ymin,y);
        }
      }
      if (prim->InheritsFrom("TH1")) {
        TH1* hist = (TH1*)prim;
        for (int i=0;i<hist->GetNbinsX();i++) {
          double y = hist->GetBinContent(i+1);
          if (y <= 0) continue;
          ymin = std::min(ymin,y);
        }
      }
      if (prim->InheritsFrom("THStack")) {
        TH1* hist = (TH1*)((THStack*)prim)->GetHists()->First();
        if (!hist) continue;
        for (int i=0;i<hist->GetNbinsX();i++) {
          double y = hist->GetBinContent(i+1);
          if (y <= 0) continue;
          ymin = std::min(ymin,y);
        }
      }
    }

    return ymin;
  }

  //
  // Fit all the data into the canvas (for the y-axis)
  //
  void FixYaxisRanges(TPad& can) {
    std::pair<double,double> ranges = GetYaxisRanges(can,true);
    SetYaxisRanges(can,ranges.first,ranges.second);
    return;
  }

  //
  // Set the x-axis ranges of a canvas
  //
  void SetYaxisRanges(TPad& can,double ymin,double ymax)
  {
    if (can.GetPrimitive("pad_top")) {
      TPad * pad_top = (TPad*)can.GetPrimitive("pad_top");
      return SetYaxisRanges(*pad_top,ymin,ymax);
    }

    TAxis* yaxis = NULL;

    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next()))
    {
      if (prim->InheritsFrom("TGraph")) {
        ((TGraph*)prim)->SetMinimum(ymin);
        ((TGraph*)prim)->SetMaximum(ymax);
        if (!yaxis) yaxis = (TAxis*) ((TGraph*)prim)->GetHistogram()->GetYaxis();
      }
      if (prim->InheritsFrom("TH1")) {
        ((TH1*)prim)->SetMinimum(ymin);
        ((TH1*)prim)->SetMaximum(ymax);
        if (!yaxis) yaxis = (TAxis*) ((TH1*)prim)->GetYaxis();
      }
      if (prim->InheritsFrom("THStack")) {
        ((THStack*)prim)->SetMinimum(ymin);
        ((THStack*)prim)->SetMaximum(ymax);
        if (!yaxis) yaxis = (TAxis*) ((THStack*)prim)->GetHistogram()->GetYaxis();
      }
    }

    if (!yaxis) {
      std::cout << "Warning: SetYaxisRange had no effect. Check that your canvas has plots in it."
                << std::endl;
      return;
    }

    yaxis->SetRangeUser(ymin,ymax);
    can.Modified();
    can.Update();
    return;
  }

  //
  // Returns the y-range of the first plotted histogram.
  // If you specify "check_all=True", returns the maximal y-range of all the plots in the canvas
  //
  std::pair<double,double> GetYaxisRanges(TPad& can,bool check_all){

    std::pair<double,double> yranges(FLT_MAX,-FLT_MAX);

    TList* tmp_list = new TList();
    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next())) {
      if (prim->InheritsFrom("TFrame")) continue;
      tmp_list->Add(prim);
    }

    // Also iterate over THStack hists
    if (can.GetPrimitive("stack")) {
      next = ((THStack*)can.GetPrimitive("stack"))->GetHists();
      while ((prim = next())) {
        tmp_list->Add(prim);
      }
    }

    next = tmp_list;
    while ((prim = next())) {
      if (prim->InheritsFrom("TGraph")) {

        for (int i=0;i<((TGraph*)prim)->GetN();++i) {
          double eyl = 0;
          double eyh = 0;
          if (prim->InheritsFrom("TGraphAsymmErrors")) {
            eyl = ((TGraphAsymmErrors*)prim)->GetEYlow() [i];
            eyh = ((TGraphAsymmErrors*)prim)->GetEYhigh()[i];
          }
          else if (prim->InheritsFrom("TGraphAsymmErrors")) {
            eyl = ((TGraphErrors*)prim)->GetEY()[i];
            eyh = ((TGraphErrors*)prim)->GetEY()[i];
          }

          yranges.first  = std::min( ((TGraph*)prim)->GetY()[i] - eyl, yranges.first );
          yranges.second = std::max( ((TGraph*)prim)->GetY()[i] + eyh, yranges.second);

        }

        if (!check_all) return yranges;

      }

      if (prim->InheritsFrom("TH1")) {
        TH1* hist = (TH1*)prim;
        for (int i=0;i<hist->GetNbinsX();i++) {
          if ( i+1 < hist->GetXaxis()->GetFirst() ) continue; // X-axis SetRange should be done first
          if ( i+1 > hist->GetXaxis()->GetLast()  ) continue; // X-axis SetRange should be done first
          yranges.first  = std::min( yranges.first , hist->GetBinContent(i+1) - hist->GetBinErrorLow(i+1) );
          yranges.second = std::max( yranges.second, hist->GetBinContent(i+1) + hist->GetBinErrorUp (i+1) );
        }
        if (!check_all) return yranges;
      }

      if (prim->InheritsFrom("TF1")) {
        yranges.first  = std::min( yranges.first , ((TF1*)prim)->GetMinimum() );
        yranges.second = std::max( yranges.second, ((TF1*)prim)->GetMaximum() );
        if (!check_all) return yranges;
      }

      if (prim->InheritsFrom("THStack")) {
        yranges.first  = std::min( yranges.first , ((THStack*)prim)->GetMinimum() );
        yranges.second = std::max( yranges.second, ((THStack*)prim)->GetMaximum() );
        if (!check_all) return yranges;
      }

    }

    return yranges;

  }

  //
  // Fit all the data into the canvas (for the x-axis)
  //
  void FixXaxisRanges(TPad& can) {
    std::pair<double,double> ranges = GetXaxisRanges(can,true);
    SetXaxisRanges(can,ranges.first,ranges.second);
    return;
  }

  //
  // Set the x-axis ranges of a canvas
  //
  void SetXaxisRanges(TPad& can,double xmin,double xmax) {
    if (can.GetPrimitive("pad_top")) {
      TPad * pad_top = (TPad*)can.GetPrimitive("pad_top");
      TPad * pad_bot = (TPad*)can.GetPrimitive("pad_bot");
      SetXaxisRanges(*pad_top,xmin,xmax);
      SetXaxisRanges(*pad_bot,xmin,xmax);
      return;
    }

    TAxis* xaxis = NULL;

    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next()))
    {
      if (prim->InheritsFrom("TH1")) {
        xaxis = ((TH1*)prim)->GetXaxis();
        xaxis->SetRangeUser(xmin,xmax);
      }
      if (prim->InheritsFrom("TGraph")) {
        xaxis = ((TGraph*)prim)->GetXaxis();
        xaxis->SetLimits(xmin,xmax);
      }
      if (prim->InheritsFrom("THStack")) {
        xaxis = ((THStack*)prim)->GetXaxis();
        xaxis->SetRangeUser(xmin,xmax);
      }
    }

    if (!xaxis) {
      std::cout << "Warning: SetXaxisRange had no effect. Check that your canvas has plots in it."
                << std::endl;
      return;
    }

    can.Modified();
    can.Update();
    return;
  }

  //
  // Returns the x-range of the first plotted histogram.
  // If you specify "check_all=True", returns the maximal x-range of all the plots in the canvas
  //
  std::pair<double,double> GetXaxisRanges(TPad& can,bool check_all){

    std::pair<double,double> xranges(FLT_MAX,-FLT_MAX);

    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next()))
    {
      if (prim->InheritsFrom("TGraph"))
      {
        TAxis* xaxis = (TAxis*) (((TGraph*)prim)->GetHistogram())->GetXaxis();
        xranges.first  = std::min(xranges.first ,xaxis->GetXmin());
        xranges.second = std::max(xranges.second,xaxis->GetXmax());
        if (!check_all) return xranges;
      }
      if (prim->InheritsFrom("TH1"))
      {
        TAxis* xaxis = (TAxis*) ((TH1*)prim)->GetXaxis();
        xranges.first  = std::min(xranges.first ,xaxis->GetXmin());
        xranges.second = std::max(xranges.second,xaxis->GetXmax());
        if (!check_all) return xranges;        
      }
    }
    return xranges;
  }

  void SetXaxisNdivisions(TPad& can,int a,int b,int c)
  {
    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next()))
    {
      if (prim->InheritsFrom("TH1"))
        ((TH1*)prim)->GetXaxis()->SetNdivisions(a,b,c);
      if (prim->InheritsFrom("TGraph"))
        ((TGraph*)prim)->GetXaxis()->SetNdivisions(a,b,c);
      if (prim->InheritsFrom("THStack"))
        ((THStack*)prim)->GetXaxis()->SetNdivisions(a,b,c);
      if (prim->InheritsFrom("TF1"))
        ((TF1*)prim)->GetXaxis()->SetNdivisions(a,b,c);
    }

    can.Modified();
    can.Update();
    return;
  }

  void SetYaxisNdivisions(TPad& can,int a,int b,int c)
  {
    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next()))
    {
      if (prim->InheritsFrom("TH1"))
        ((TH1*)prim)->GetYaxis()->SetNdivisions(a,b,c);
      if (prim->InheritsFrom("TGraph"))
        ((TGraph*)prim)->GetYaxis()->SetNdivisions(a,b,c);
      if (prim->InheritsFrom("THStack"))
        ((THStack*)prim)->GetYaxis()->SetNdivisions(a,b,c);
      if (prim->InheritsFrom("TF1"))
        ((TF1*)prim)->GetYaxis()->SetNdivisions(a,b,c);
    }

    can.Modified();
    can.Update();
    return;
  }

  bool CanvasHasPlot(TPad& can){
    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next()))
    {
      if (prim->InheritsFrom("TH1")) return true;
      if (prim->InheritsFrom("TGraph")) return true;
      if (prim->InheritsFrom("TF1")) return true;
    }
    return false;
  }

} // namespace GU
