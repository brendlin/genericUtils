//
// Usage: (You can also set your Macro path in .rootrc
// gROOT->LoadMacro("../genericUtils/PlotFunctions.cxx")
// gROOT->LoadMacro("UnitTestPlotCpp.C")
// UnitTestPlotCpp()
//

#include "genericUtils/PlotFunctions.h"
#include "genericUtils/TAxisFunctions.h"

void UnitTestPlotCpp() {

  GU::SetupStyle();

  TH1F* a = new TH1F("a","Legend text for a",48,-6,6);
  TH1F* b = new TH1F("b","Legend text for b",48,-6,6);

  TH2F* hist_2d = new TH2F("hist_2d","Legend text for 2d hist",48,-6,6,48,-6,6);

  Double_t x[8] = {-5.5,-4.5,-3.5,-2.5,-2.0,0,3.5,4.5};
  Double_t y[8] = {1000,2000,3000,2500,1000,2000,2200,2400};
  TGraph* d = new TGraph(8,x,y);
  d->SetNameTitle("mygraph","Legend text for graph");
  d->SetLineWidth(2);

  TF1* e = new TF1("e","12*sin(x*3)+20",-5,5);

  a->Sumw2();
  b->Sumw2();

  TRandom3* rand = new TRandom3(1);

  for (int i=0;i<100000;++i) {
    a->Fill(rand->Gaus(0,1));
    b->Fill(rand->Gaus(0,1));
    hist_2d->Fill(rand->Gaus(0,1),rand->Gaus(0,1));
  }
  a->Fill(2,2000);



  //
  // The function-based way of making plots
  //
  TCanvas* mycanvas = new TCanvas("mycanvas","blah",600,500);
  GU::AddHistogram(*mycanvas,*a);
  GU::AddHistogram(*mycanvas,*b);
  GU::AddHistogram(*mycanvas,*e,"l");

  GU::SetAxisLabels(*mycanvas,"x axis","y axis");
  mycanvas->SetLogy();

  GU::FormatCanvasAxes(*mycanvas);
  GU::SetColors(*mycanvas);

  std::vector<std::string> text;
  text.push_back(GU::GetAtlasInternalText("Preliminary"));
  text.push_back(Form("%s, %s",GU::GetSqrtsText(13).c_str(),GU::GetLuminosityText().c_str()));
  GU::DrawText(*mycanvas,text,0.20,0.78,0.5,0.92,3);

  GU::MakeLegend(*mycanvas);
  GU::AutoFixAxes(*mycanvas);
  mycanvas->Print("mycanvas.pdf");



  //
  // A ratio canvas from functions
  //
  TCanvas* mycanvas_ratio = GU::RatioCanvas("my_ratiocanvas","blah",600,500);
  GU::AddHistogram(*mycanvas,*a);
  GU::AddRatio(*mycanvas_ratio,*b,*a);
  GU::AddHistogram(*mycanvas_ratio,*d,"pl");
  GU::SetAxisLabels(*mycanvas_ratio,"x axis","y axis");

  GU::FullFormatCanvasDefault(*mycanvas_ratio);
  GU::SetYaxisRanges(*GU::GetBotPad(*mycanvas_ratio),0,2);



  //
  // Stack Histogram
  //
  TCanvas* mycanvas_stack = new TCanvas("my_stackcanvas","blah",600,500);
  GU::AddHistogram(*mycanvas_stack,*a);
  GU::AddHistogram(*mycanvas_stack,*b);

  // SetColors
  int col[] = {kGreen+1, kAzure+2};
  std::vector<int> colors (col, col + sizeof(col) / sizeof(int) );
  GU::SetColors(*mycanvas_stack,colors,true);

  GU::Stack(*mycanvas_stack);
  GU::SetAxisLabels(*mycanvas_stack,"x axis","y axis");
  GU::FullFormatCanvasDefault(*mycanvas_stack);

  return;

}
