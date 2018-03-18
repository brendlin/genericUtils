#include "PlotFunctions.h"
#include "TAxisFunctions.h"

#include <iostream>
#include <string>
#include <tgmath.h>

#include "TString.h"
#include "TObject.h"
#include "TStyle.h"
#include "TColor.h"
#include "TLegend.h"
#include "TROOT.h"
#include "THStack.h"

namespace GU {

  TList* m_ptr = nullptr;

  TList *GetGlobalHistoCollector()
  {
    if (m_ptr == nullptr)
    { m_ptr = new TList(); }

    return m_ptr;
  }

  std::string GetLuminosityText(double lumi_fb)
  {
    double tmp_lumi = lumi_fb;
    std::string unit = "fb";
    if (tmp_lumi < 1) {
      unit = "pb";
      tmp_lumi = tmp_lumi * 1000.;
    }
    return Form("#lower[-0.2]{#scale[0.60]{#int}}Ldt = %1.1f %s^{-1}",tmp_lumi,unit.c_str());
  }

  std::string GetSqrtsText(int sqrts) { return Form("#sqrt{s} = %d TeV",sqrts); }

  std::string GetAtlasInternalText(std::string status)
  {
    return Form("#font[72]{ATLAS} #font[42]{%s}",status.c_str());
  }

//
// Add a TH1 or a TGraph to a canvas.
// If a RatioCanvas is specified as the canvas, then the histogram will be added to the top pad
// by default. (To specifically add a canvas to the bottom, do AddHistogram(GetBotPad(can),hist)
// This will *make a copy* of the histogram or graph, so that when you further manipulate the histogram
// in its canvas it will only affect the appearance in this one canvas. This way you
// can add the same histogram to multiple canvases and be able to manipulate the appearance of each
// instance separately.
//
  TH1* AddHistogram(TPad& can,TH1& hist,std::string drawopt,bool keepname) {

    // If the canvas has a sub-pad called "pad_top" then put the histogram there.
    TPad* pad_top = (TPad*)can.GetPrimitive("pad_top");
    if (pad_top) return AddHistogram(*pad_top,hist,drawopt,keepname);

    TH1* tmp = (TH1*)hist.Clone();
    tmp->SetDirectory(0);
    if (!keepname) tmp->SetName(Form("%s_%s",can.GetName(),hist.GetName()));
    GetGlobalHistoCollector()->Add(tmp);

    if (CanvasHasPlot(can)) drawopt += "same";
    can.cd();
    tmp->Draw(drawopt.c_str());
    can.Modified();

    return tmp;
  }

  TGraph* AddHistogram(TPad& can,TGraph& hist,std::string drawopt,bool keepname) {

    // If the canvas has a sub-pad called "pad_top" then put the histogram there.
    TPad* pad_top = (TPad*)can.GetPrimitive("pad_top");
    if (pad_top) return AddHistogram(*pad_top,hist,drawopt,keepname);

    TGraph* tmp = (TGraph*)hist.Clone();
    if (!keepname) tmp->SetName(Form("%s_%s",can.GetName(),hist.GetName()));
    GetGlobalHistoCollector()->Add(tmp);

    if (!CanvasHasPlot(can)) drawopt += "a";
    can.cd();
    tmp->Draw(drawopt.c_str());
    can.Modified();

    return tmp;
  }

  TF1* AddHistogram(TPad& can,TF1& hist,std::string drawopt,bool keepname) {

    // If the canvas has a sub-pad called "pad_top" then put the histogram there.
    TPad* pad_top = (TPad*)can.GetPrimitive("pad_top");
    if (pad_top) return AddHistogram(*pad_top,hist,drawopt,keepname);

    TF1* tmp = (TF1*)hist.Clone();
    if (!keepname) tmp->SetName(Form("%s_%s",can.GetName(),hist.GetName()));
    GetGlobalHistoCollector()->Add(tmp);

    if (CanvasHasPlot(can)) drawopt += "same";
    can.cd();
    tmp->Draw(drawopt.c_str());
    can.Modified();

    return tmp;
  }

  //
  // FullFormatCanvasDefault is a collection of functions for easy "1-step" plotting.
  //
  void FullFormatCanvasDefault(TPad& can,double lumi,double sqrts,
                               std::string additionaltext,std::string status)
  {
    FormatCanvasAxes(can);
    if (!can.GetPrimitive("stack")) {
      SetColors(can);
    }

    std::vector<std::string> text;
    text.push_back(GU::GetAtlasInternalText(status));
    if (lumi > 0 && sqrts > 0) text.push_back(Form("%s, %s",GU::GetSqrtsText(sqrts).c_str(),
                                                   GU::GetLuminosityText(lumi).c_str()));
    else if (lumi > 0) text.push_back(GU::GetLuminosityText(lumi));
    else if (sqrts > 0) text.push_back(GU::GetSqrtsText(sqrts));

    if (additionaltext != "") text.push_back(additionaltext);

    if (can.GetPrimitive("pad_top")) {
      DrawText(*GetTopPad(can),text,.2,.73,.5,.93,3);
      MakeLegend(can,.6,.73,.8,.93,1,3);
    } else {
      DrawText(can,text,0.2,0.78,0.5,0.94,3);
      MakeLegend(can,0.6,0.78,0.8,0.94,1,3);
    }

    AutoFixAxes(can);
    return;
  }

  //
  // Draw some additional text on your plot, in the form of a TLegend (easier to manage)
  // The x and y coordinates are the fractional distances, with the origin at the bottom left.
  // Specify multi-lines by specifing a list ["line1","line2","line3"] instead of a string "single line".
  //
  void DrawText(TPad& can,const std::string text,
                double x1,double y1,double x2,double y2,int totalentries,
                double angle,std::string align,int textsize){
    std::vector<std::string> text_vec;
    text_vec.push_back(text);
    return DrawText(can,text,x1,y1,x2,y2,totalentries,angle,align,textsize);
  }

  void DrawText(TPad& can,const std::vector<std::string> text,
                double x1,double y1,double x2,double y2,int totalentries,
                double angle,std::string align,int textsize){

    (void)align;
    (void)angle;

    if (x1 < 0) x1 = 0.2;
    if (x2 < 0) x2 = 0.5;

    if (y1 < 0) y1 = ( can.GetPrimitive("pad_top") ? 0.73 : 0.78);
    if (y2 < 0) y2 = ( can.GetPrimitive("pad_top") ? 0.93 : 0.94);

    can.cd();
    if (can.GetPrimitive("pad_top")) ((TPad*)can.GetPrimitive("pad_top"))->cd();

    TLegend* leg = new TLegend(x1,y1,x2,y2);
    GetGlobalHistoCollector()->Add(leg);
    leg->SetName(TString(can.GetName())+"_text");

    leg->SetMargin(0);
    leg->SetFillStyle(0);
    leg->SetTextSize(textsize);

    int total = 0;
    for (unsigned int i=0;i<text.size();++i) {
      leg->AddEntry("",text[i].c_str(),"");
      total++;
    }

    while (total < totalentries) {
      leg->AddEntry("","","");
      total++;
    }

    leg->Draw();
    can.Modified();
    return;

  }

//
// The MakeLegend function looks for any TH1 or TGraph you added to your canvas, and puts them
// in a legend in the order that you added them to a canvas.
// The entry label is taken from the title of the TH1 or TGraph. *Be sure to set the title
// of your TH1 or TGraph *before* you add it to the canvas.*
// The x and y coordinates are the fractional distances, with the origin at the bottom left.
//
  void MakeLegend(TPad& can,double x1,double y1,double x2,double y2,
                  int ncolumns,int totalentries,
                  const std::vector<std::string>& options,
                  const std::vector<std::string>& skip,
                  int textsize) {

    if (x1 < 0) x1 = 0.6;
    if (x2 < 0) x2 = 0.8;

    if (y1 < 0) y1 = ( can.GetPrimitive("pad_top") ? 0.73 : 0.78);
    if (y2 < 0) y2 = ( can.GetPrimitive("pad_top") ? 0.93 : 0.94);

    if (can.GetPrimitive("pad_top")) {
      TPad * pad_top = (TPad*)can.GetPrimitive("pad_top");
      MakeLegend(*pad_top,x1,y1,x2,y2,ncolumns,totalentries,options,skip,textsize);
      return;
    }

    if (!CanvasHasPlot(can)) {
      std::cout << "Error: trying to make legend from canvas with 0 plots. Will do nothing."
                << std::endl;
      return;
    }

    //
    // if a previous version exists from this function, delete it
    //
    if (can.GetPrimitive("legend")) {
      TObject* old_leg = can.GetPrimitive("legend");
      can.GetListOfPrimitives()->Remove(old_leg);
    }

    TLegend* leg = new TLegend(x1,y1,x2,y2);
    leg->SetName("legend");
    GetGlobalHistoCollector()->Add(leg);

    leg->SetTextSize(textsize);
    leg->SetFillStyle(0);
    leg->SetNColumns(ncolumns);

    //
    // Add by TH1 GetTitle()
    //
    TList* tmp_list = new TList();
    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;

    // Also iterate over THStack hists (put the stack first
    if (can.GetPrimitive("stack")) {
      next = ((THStack*)can.GetPrimitive("stack"))->GetHists();
      while ((prim = next())) {
        tmp_list->Add(prim);
      }
    }

    // Add the rest of the primitives
    next = can.GetListOfPrimitives();
    while ((prim = next())) {
      tmp_list->Add(prim);
    }

    int total = 0;

    next = tmp_list;
    while ((prim = next()))
    {
      if (TString(prim->GetTitle()).EqualTo("stack")) continue;
      if (TString(prim->GetTitle()).EqualTo("remove")) continue;
      if (!prim->InheritsFrom("TH1") &&
          !prim->InheritsFrom("TGraph") &&
          !prim->InheritsFrom("TF1")) continue;
      bool do_skip = false;
      for (unsigned int i=0;i<skip.size();i++) {
        if (TString(prim->GetName()).EqualTo(skip[i].c_str())) do_skip = true;
      }
      if (do_skip) continue;

      TString drawopt = prim->GetDrawOption();
      drawopt.ReplaceAll("same","");
      drawopt.ReplaceAll("hist","l");
      if (int(options.size()) > total) drawopt = options[total];
      if (options.size() == 1) drawopt = options[0];
      if (drawopt.IsNull()) drawopt = "f";

      leg->AddEntry(prim,"^{ }"+TString(prim->GetTitle()),drawopt);
      total++;
    }

    // Add empty entries to ensure a standard layout
    while (total < totalentries) {
      leg->AddEntry("","","");
      total++;
    }

    // recipe for making roughly square boxes
    double h = leg->GetY2() - leg->GetY1();
    double w = leg->GetX2() - leg->GetX1();
    double h_can = can.GetWh();
    double w_can = can.GetWw();
    double h_pad = can.GetAbsHNDC();
    double w_pad = can.GetAbsWNDC();
    leg->SetMargin(leg->GetNColumns()*h*h_can*h_pad/float(leg->GetNRows()*w*w_can*w_pad));

    can.cd();
    if (can.GetPrimitive("pad_top"))
      ((TPad*)can.GetPrimitive("pad_top"))->cd();
    leg->Draw();
    can.Modified();
    can.Update();

    return;
  }

  //
  // Setup general style.
  //
  void SetupStyle(void) {

    TStyle* mystyle = new TStyle("mystyle","mystyle");
    mystyle->SetStatColor(0);
    mystyle->SetTitleColor(0);
    mystyle->SetCanvasColor(0);
    mystyle->SetPadColor(0);
    mystyle->SetPadBorderMode(0);
    mystyle->SetCanvasBorderMode(0);
    mystyle->SetFrameBorderMode(0);
    mystyle->SetOptStat(0);
    mystyle->SetStatH(0.3);
    mystyle->SetStatW(0.3);
    mystyle->SetTitleColor(1);
    mystyle->SetTitleFillColor(0);
    mystyle->SetTitleBorderSize(0);
    mystyle->SetHistLineWidth(2);
    //mystyle->SetLineWidth(2); // no
    mystyle->SetFrameFillColor(0);
    mystyle->SetOptTitle(0);
    mystyle->SetPaintTextFormat("4.1f ");
    mystyle->SetEndErrorSize(3);

    mystyle->SetPadTickX(1);
    mystyle->SetPadTickY(1);

    mystyle->SetPadTopMargin(0.05);
    mystyle->SetPadRightMargin(0.05);
    mystyle->SetPadBottomMargin(0.11);
    mystyle->SetPadLeftMargin(0.16);

    mystyle->SetMarkerStyle(20);
    mystyle->SetMarkerSize(1.2);

    //
    // NOTE that in ROOT rendering the font size is slightly smaller than in pdf viewers!
    // The effect is about 2 points (i.e. 18 vs 20 font)
    //
    // all axes
    mystyle->SetTitleSize  (22   ,"xyz");
    mystyle->SetTitleFont  (43   ,"xyz");
    mystyle->SetLabelSize  (22   ,"xyz");
    mystyle->SetLabelFont  (43   ,"xyz");

    // x axis
    mystyle->SetTitleXOffset(1.0);
    mystyle->SetLabelOffset(0.002,"x");

    // y axis
    mystyle->SetTitleOffset(1.75 ,"y");
    mystyle->SetLabelOffset(0.006,"y");
    mystyle->SetNdivisions(510,"y"); // n1 = 10, n2 = 5, n3 = 0 -> 00 05 10 = 510

    // z axis
    mystyle->SetTitleOffset(0.85,"z");
    mystyle->SetLabelOffset(0.004,"z");

    // Legend
    mystyle->SetLegendTextSize(18);
    mystyle->SetLegendFont(43);
    mystyle->SetLegendFillColor(0);
    mystyle->SetLegendBorderSize(0);

    // Gradient colors
    const Int_t ncont = 255;

    // http://ultrahigh.org/2007/08/making-pretty-root-color-palettes/
    const Int_t NRGBs = 5;
    Double_t stops[NRGBs] = { 0.00, 0.34, 0.61, 0.84, 1.00 };
    Double_t red  [NRGBs] = { 0.00, 0.00, 0.87, 1.00, 0.51 };
    Double_t green[NRGBs] = { 0.00, 0.81, 1.00, 0.20, 0.00 };
    Double_t blue [NRGBs] = { 0.51, 1.00, 0.12, 0.00, 0.00 };

    TColor::CreateGradientColorTable(NRGBs,stops,red,green,blue,ncont);
    mystyle->SetNumberContours(ncont);

    gROOT->SetStyle("mystyle");

    return;

  }


//
// Format the axes of your canvas or RatioCanvas, including axis labels, sizes, offsets.
// Call this *after* one or more histograms have been added to the canvas.
//
  void FormatCanvasAxes(TPad& can)
  {

    double XTitleOffset = 0.98;
    double XLabelOffset = 0.002;
    double XTickLength  = 0.02;

    if (can.GetPrimitive("pad_top"))
    {
      TPad* pad_top = GetTopPad(can);

      TIter next(pad_top->GetListOfPrimitives());
      TObject* prim = NULL;
      while ((prim = next()))
      {
        if (prim->InheritsFrom("TH1")) {
          ((TH1*)prim)->GetXaxis()->SetTitleOffset(XTitleOffset/float(pad_top->GetHNDC()));
          ((TH1*)prim)->GetXaxis()->SetLabelOffset(XLabelOffset/float(pad_top->GetHNDC()));
          ((TH1*)prim)->GetXaxis()->SetTickLength (XTickLength /float(pad_top->GetHNDC()));
        }
        if (prim->InheritsFrom("TGraph")) {
          TGraph* tmp = (TGraph*)prim;
          tmp->GetHistogram()->GetXaxis()->SetTitleOffset(XTitleOffset/float(pad_top->GetHNDC()));
          tmp->GetHistogram()->GetXaxis()->SetLabelOffset(XLabelOffset/float(pad_top->GetHNDC()));
          tmp->GetHistogram()->GetXaxis()->SetTickLength (XTickLength /float(pad_top->GetHNDC()));
        }
        if (prim->InheritsFrom("TF1")) {
          ((TF1*)prim)->GetXaxis()->SetTitleOffset(XTitleOffset/float(pad_top->GetHNDC()));
          ((TF1*)prim)->GetXaxis()->SetLabelOffset(XLabelOffset/float(pad_top->GetHNDC()));
          ((TF1*)prim)->GetXaxis()->SetTickLength (XTickLength /float(pad_top->GetHNDC()));
        }
      }
      pad_top->Modified();
    }

    if (can.GetPrimitive("pad_bot"))
    {
      TPad* pad_bot = GetBotPad(can);

      TIter next(pad_bot->GetListOfPrimitives());
      TObject* prim = NULL;
      while ((prim = next()))
      {

       if (prim->InheritsFrom("TH1")) {
          ((TH1*)prim)->GetXaxis()->SetTitleOffset(XTitleOffset/float(pad_bot->GetHNDC()));
          ((TH1*)prim)->GetXaxis()->SetLabelOffset(XLabelOffset/float(pad_bot->GetHNDC()));
          ((TH1*)prim)->GetXaxis()->SetTickLength (XTickLength /float(pad_bot->GetHNDC()));
          ((TH1*)prim)->GetYaxis()->SetNdivisions (505);
        }
        if (prim->InheritsFrom("TGraph")) {
          TGraph* tmp = (TGraph*)prim;
          tmp->GetXaxis()->SetTitleOffset(XTitleOffset/float(pad_bot->GetHNDC()));
          tmp->GetXaxis()->SetLabelOffset(XLabelOffset/float(pad_bot->GetHNDC()));
          tmp->GetXaxis()->SetTickLength (XTickLength /float(pad_bot->GetHNDC()));
          tmp->GetYaxis()->SetNdivisions (505);
        }
        if (prim->InheritsFrom("TF1")) {
          ((TF1*)prim)->GetXaxis()->SetTitleOffset(XTitleOffset/float(pad_bot->GetHNDC()));
          ((TF1*)prim)->GetXaxis()->SetLabelOffset(XLabelOffset/float(pad_bot->GetHNDC()));
          ((TF1*)prim)->GetXaxis()->SetTickLength (XTickLength /float(pad_bot->GetHNDC()));
          ((TF1*)prim)->GetYaxis()->SetNdivisions (505);
        }
      }
      pad_bot->Modified();
    }

    can.Modified();
    return;
  }



  //
  // Set x- and y-axis labels. Do this *after* you have added your first histogram to the canvas.
  //
  void SetAxisLabels(TPad& can,std::string xlabel,std::string ylabel,std::string yratiolabel) {
    if (can.GetPrimitive("pad_top")) {
      TPad * pad_top = (TPad*)can.GetPrimitive("pad_top");
      TPad * pad_bot = (TPad*)can.GetPrimitive("pad_bot");
      SetAxisLabels(*pad_top,"",ylabel);
      SetAxisLabels(*pad_bot,xlabel,yratiolabel);
    }

    TIter next(can.GetListOfPrimitives());
    TObject* prim = NULL;
    while ((prim = next()))
    {
      if (prim->InheritsFrom("TH1")) {
        ((TH1*)prim)->GetXaxis()->SetTitle(xlabel.c_str());
        ((TH1*)prim)->GetYaxis()->SetTitle(ylabel.c_str());
      }
      if (prim->InheritsFrom("TGraph")) {
        ((TGraph*)prim)->GetXaxis()->SetTitle(xlabel.c_str());
        ((TGraph*)prim)->GetYaxis()->SetTitle(ylabel.c_str());
      }
      if (prim->InheritsFrom("TF1")) {
        ((TF1*)prim)->GetXaxis()->SetTitle(xlabel.c_str());
        ((TF1*)prim)->GetYaxis()->SetTitle(ylabel.c_str());
      }
      if (prim->InheritsFrom("THStack")) {
        ((THStack*)prim)->GetXaxis()->SetTitle(xlabel.c_str());
        ((THStack*)prim)->GetYaxis()->SetTitle(ylabel.c_str());
      }

    }

    can.Modified();
    return;
  }

  std::vector<int> KurtColorPalate(void)
  {
    Int_t colors[58] = {kBlack+0,kRed+1,kAzure-2,kGreen+1,kMagenta+1,kCyan+1,kOrange+1,
                        kBlack+2,kRed+3,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3,
                        kGray,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7,
                        kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5,
                        21,22,23,24,25,26,27,28,29,30,
                        21,22,23,24,25,26,27,28,29,30,
                        21,22,23,24,25,26,27,28,29,30};

    std::vector<int> ret;

    for (unsigned int i=0;i< sizeof(colors)/sizeof(colors[0]); ++i) {
      ret.push_back(colors[i]);
    }

    return ret;

  }

  void SetColors(TPad& can,const std::vector<int>& colors_in,bool fill,bool line) {

    if (can.GetPrimitive("stack")) {
      std::cout << "WARNING in PlotFunctions.cxx SetColors: canvas has a THStack, but colors must be"
                << " set before adding to the THStack. Please call SetColors() before calling Stack()."
                << "Doing nothing." << std::endl;
      return;
    }

    std::vector<int> colors = colors_in;
    if (!colors.size()) colors = KurtColorPalate();

    TIter next(can.GetListOfPrimitives());
    if (can.GetPrimitive("pad_top")) {
      next = ((TPad*)can.GetPrimitive("pad_top"))->GetListOfPrimitives();
    }

    unsigned int color_count = 0;

    TObject* prim = NULL;
    while ((prim = next()))
    {
      // TH1 case
      if (prim->InheritsFrom("TH1")) {
        ((TH1*)prim)->SetLineColor(colors[color_count]);
        ((TH1*)prim)->SetMarkerColor(colors[color_count]);
        ((TH1*)prim)->SetFillColor(fill ? colors[color_count] : 0);
        if (fill && !line) ((TH1*)prim)->SetLineColor(1);

        // Check if there is a bottom pad, with ratios. Make them the same color.
        if (can.GetPrimitive("pad_bot")) {
          TString ratio_name = TString(prim->GetName()) + "_ratio";
          ratio_name.ReplaceAll("pad_top_","pad_bot_");
          TH1* ratio = (TH1*)((TPad*)can.GetPrimitive("pad_bot"))->GetPrimitive(ratio_name);
          if (ratio) {
            ratio->SetLineColor(colors[color_count]);
            ratio->SetMarkerColor(colors[color_count]);
            ratio->SetFillColor(0);
          }
        }

        color_count++;
      }

      // TGraph case
      if (prim->InheritsFrom("TGraph")) {

        ((TGraph*)prim)->SetLineColor(colors[color_count]);
        ((TGraph*)prim)->SetMarkerColor(colors[color_count]);
        ((TGraph*)prim)->SetFillColor(fill ? colors[color_count] : 0);
        if (fill && !line) ((TGraph*)prim)->SetLineColor(1);

        // Check if there is a bottom pad, with ratios. Make them the same color.
        if (can.GetPrimitive("pad_bot")) {
          TString ratio_name = TString(prim->GetName()) + "_ratio";
          ratio_name.ReplaceAll("pad_top_","pad_bot_");
          TGraph* ratio = (TGraph*)((TPad*)can.GetPrimitive("pad_bot"))->GetPrimitive(ratio_name);
          if (ratio) {
            ratio->SetLineColor(colors[color_count]);
            ratio->SetMarkerColor(colors[color_count]);
            ratio->SetFillColor(0);
          }
        }

        color_count++;
      }

      // TF1 case
      if (prim->InheritsFrom("TF1")) {

        ((TF1*)prim)->SetLineColor(colors[color_count]);
        ((TF1*)prim)->SetMarkerColor(colors[color_count]);
        ((TF1*)prim)->SetFillColor(fill ? colors[color_count] : 0);
        if (fill && !line) ((TF1*)prim)->SetLineColor(1);

        // assuming that you did not take a ratio of TF1 objects.

        color_count++;
      }

      if (color_count >= colors.size())
      {
        break;
      }

    }

    can.Modified();
    can.Update();

    TPad* pad_bot = (TPad*)can.GetPrimitive("pad_bot");
    if (pad_bot)
    {
      pad_bot->Modified();
      pad_bot->Update();
    }

    return;
  }


  //
  // Call this if you want a TCanvas especially prepared for ratio plots. It creates two
  // sub-pads, "pad_top" and "pad_bot", and the rest of the functions in this file will
  // specifically look for this type of configuration and act accordingly. See also the special
  // functions GetTopPad(can) and GetBotPad(can) if you want to manipulate the sub-pads yourself.
  // To add histograms to the top pad, do AddHistogram(can,hist) or AddHistogramTop(can,hist)
  // To add histograms to the bot pad, do AddHistogramBot(can,hist).
  // To add a histogram to the top pad, and its ratio with a reference histogram to the bottom pad,
  // do AddRatio(can,hist,ref_hist,"B") (the B is for binomial errors).
  //
  TCanvas* RatioCanvas(const char *name,const char *title,
                       Int_t canw,Int_t canh,double ratio_size_as_fraction)
  {
    TCanvas* c = new TCanvas(name,title,canw,canh);
    c->cd();

    TPad* top = new TPad("pad_top", "This is the top pad",0.0,ratio_size_as_fraction,1.0,1.0);
    top->SetBottomMargin(0.02/float(top->GetHNDC()));
    top->SetTopMargin   (0.04/float(top->GetHNDC()));
    top->SetRightMargin (0.05 );
    top->SetLeftMargin  (0.16 );
    top->SetFillColor(0);
    top->Draw();
    GetGlobalHistoCollector()->Add(top);

    c->cd();
    TPad* bot = new TPad("pad_bot", "This is the bottom pad",0.0,0.0,1.0,ratio_size_as_fraction);
    bot->SetBottomMargin(0.11/float(bot->GetHNDC()));
    bot->SetTopMargin   (0.02/float(bot->GetHNDC()));
    bot->SetRightMargin (0.05);
    bot->SetLeftMargin  (0.16);
    bot->SetFillColor(0);
    bot->Draw();
    GetGlobalHistoCollector()->Add(bot);

    return c;
  }

  //
  // Adds a histogram to the top pad of a RatioCanvas, and a ratio (dividing by some reference
  // histogram ref_hist) to the bottom pad of the RatioCanvas. Specify the division type
  // by the "divide" option ("B" for binomial, "" for uncorrelated histograms)
  //
  std::pair<TH1*,TH1*> AddRatio(TPad& can,TH1& hist,TH1& ref_hist,std::string divide,std::string drawopt)
  {

    TH1::SetDefaultSumw2(true);
    TH1* ratioplot = (TH1*)hist.Clone();
    ratioplot->SetName(TString(hist.GetName())+"_ratio");

    if (divide == "pull") {
      ratioplot->GetYaxis()->SetTitle("pull");
      for (int i=0; i<ratioplot->GetNbinsX()+2; i++)
      {
        double bc1 = hist.GetBinContent(i);
        double bc2 = ref_hist.GetBinContent(i);
        double be1 = (bc1 > bc2) ? hist    .GetBinErrorLow(i) : hist    .GetBinErrorUp(i);
        double be2 = (bc2 > bc1) ? ref_hist.GetBinErrorLow(i) : ref_hist.GetBinErrorUp(i);

        if ( pow(be1,2) + pow(be2,2) ) {
          ratioplot->SetBinContent(i,(bc1-bc2)/sqrt( pow(be1,2)+pow(be2,2) ));
        }
        ratioplot->SetBinError(i,1);
      }
    } else {
      // Divide = "B" or otherwise
      ratioplot->GetYaxis()->SetTitle("ratio");
      ratioplot->Divide(&hist,&ref_hist,1.,1.,divide.c_str());
    }

    TH1* return_hist = AddHistogram(*GetTopPad(can),hist,drawopt);
    TH1* return_ratio = AddHistogram(*GetBotPad(can),*ratioplot,drawopt);

    std::pair<TH1*,TH1*> ret(return_hist,return_ratio);
    return ret;
  }

  std::pair<TGraph*,TGraph*> AddRatio(TPad& can,TGraph& hist,TGraph& ref_hist,std::string divide,std::string drawopt)
  {
    // TODO: Add error bars to TGraph treatment.
    (void)divide;

    TGraph* ratioplot = (TGraph*)hist.Clone();
    ratioplot->SetName(TString(hist.GetName())+"_ratio");

    ratioplot->GetYaxis()->SetTitle("ratio");
    for (int i=0; i<ratioplot->GetN(); i++) {
      if (ref_hist.GetY()[i] == 0) continue;
      ratioplot->SetPoint(i,hist.GetX()[i],hist.GetY()[i]/float(ref_hist.GetY()[i]));
    }

    TGraph* return_hist  = AddHistogram(*GetTopPad(can),hist,drawopt);
    TGraph* return_ratio = AddHistogram(*GetBotPad(can),*ratioplot,drawopt);
    std::pair<TGraph*,TGraph*> ret(return_hist,return_ratio);
    return ret;
  }

  std::pair<TH1*,TH1*> AddRatioManual(TPad& can,TH1& hist,TH1& ratioplot,
                                      std::string drawopt1,std::string drawopt2)
  {

    TH1* return_hist  = AddHistogram(*GetTopPad(can),hist,drawopt1);
    TH1* return_ratio = AddHistogram(*GetBotPad(can),ratioplot,drawopt2);

    TString ratio_name = TString(return_hist->GetName()) + "_ratio";
    ratio_name.ReplaceAll("pad_top_","pad_bot_");

    return_ratio->SetName(ratio_name);

    std::pair<TH1*,TH1*> ret(return_hist,return_ratio);
    return ret;
  }

  std::pair<TGraph*,TGraph*> AddRatioManual(TPad& can,TGraph& hist,TGraph& ratioplot,
                                            std::string drawopt1,std::string drawopt2)
  {

    TGraph* return_hist  = AddHistogram(*GetTopPad(can),hist,drawopt1);
    TGraph* return_ratio = AddHistogram(*GetBotPad(can),ratioplot,drawopt2);

    TString ratio_name = TString(return_hist->GetName()) + "_ratio";
    ratio_name.ReplaceAll("pad_top_","pad_bot_");

    return_ratio->SetName(ratio_name);

    std::pair<TGraph*,TGraph*> ret(return_hist,return_ratio);
    return ret;
  }


  //
  // Stack plot functionality
  //
  void Stack(TPad& can, bool reverse)
  {
    if (can.GetPrimitive("pad_top")) {
      return Stack(*GetTopPad(can),reverse);
    }

    THStack* stack = new THStack("stack","stack");
    GetGlobalHistoCollector()->Add(stack);

    std::string xaxislabel;
    std::string yaxislabel;
    std::vector<std::string> binlabels;

    TObjLink *lnk = can.GetListOfPrimitives()->FirstLink();
    if (reverse) lnk = can.GetListOfPrimitives()->LastLink();
    while (lnk) {
      TObject* obj = lnk->GetObject();

      if (obj->InheritsFrom("TH1"))
      {
        TH1* hist = (TH1*)obj;
        stack->Add(hist);

        if (xaxislabel == "") xaxislabel = hist->GetXaxis()->GetTitle();
        if (yaxislabel == "") yaxislabel = hist->GetYaxis()->GetTitle();
        if (!binlabels.size() && !TString(hist->GetXaxis()->GetBinLabel(1)).IsNull()) {
          for (int i=0; i<hist->GetNbinsX(); i++) {
            binlabels.push_back(hist->GetXaxis()->GetBinLabel(i+1));
          }
        }

      }

      lnk = ( reverse ? lnk->Prev() : lnk->Next() );
    }

    // The original objects are cleared from the histogram:
    can.Clear();
    can.cd();
    stack->Draw("hist");
    stack->GetXaxis()->SetTitle(xaxislabel.c_str());
    stack->GetYaxis()->SetTitle(yaxislabel.c_str());
    if (binlabels.size()) {
      for (unsigned int i=0; i<binlabels.size(); i++) {
        stack->GetXaxis()->SetBinLabel(i+1,binlabels[i].c_str());
      }
    }

    can.RedrawAxis();
    can.Modified();
    can.Update();

    return;
  }


  TPad* GetBotPad(TPad& can)
  {
    return (TPad*)can.GetPrimitive("pad_bot");
  }

  TPad* GetTopPad(TPad& can)
  {
    return (TPad*)can.GetPrimitive("pad_top");
  }

} // namespace GU
