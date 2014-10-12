#include "TH1.h"
#include "TCanvas.h"
#include "TColor.h"
#include <string>
#include <stdlib.h>

void ListExtras(void){
  std::cout << "# Extras.C: " << "Plot options:"             << std::endl;
  std::cout << "# Extras.C: " << "    set_plot_style()"      << std::endl;
  std::cout << "# Extras.C: " << "    set_plot_style_gr()"   << std::endl;
  std::cout << "# Extras.C: " << "    set_plot_style_kurt()" << std::endl;
  std::cout << "# Extras.C: " << "    set_plot_style_sth()" << std::endl;
  std::cout << "# Extras.C: " << "Functions:"            << std::endl;
  std::cout << "# Extras.C: " << "    h = hist(\"h\",c)" << std::endl;
  std::cout << "# Extras.C: " << "    i = integral(TH1F* h,double binedge1, double binedge2)" << std::endl;
  std::cout << "# Extras.C: " << "    h = SF(TH2F* h,TH2F* err,int bin)" << std::endl;
}

TH1F* SF(TH2* h,TH2* err,int bin){
  TH1F* hist;
  TH1F* error;
  stringstream name1,name2;
  name1 << h->GetName() << bin;
  name2 << err->GetName() << bin;
  string name1s = name1.str();
  string name2s = name2.str();
  hist   = (TH1F*)h->ProjectionY(name1s.c_str(),bin,bin);
  error  = (TH1F*)err->ProjectionY(name2s.c_str(),bin,bin);
  for(int i=0;i<hist->GetNbinsX();i++){
    hist->SetBinError(i+1,error->GetBinContent(i+1));
  }
  return hist;
}

TH1F* hist(const char* name,TCanvas* c){
  std::cout << "##################################" << std::endl;
  std::cout << "#" << std::endl;
  std::cout << "# Extras.C hist" << std::endl;
  std::cout << "#" << std::endl;
  std::cout << "##################################" << std::endl;
  return (TH1F*)c->GetPrimitive(name);
}

double integral(TH1F* h,double f,double l){
  std::cout << "##################################" << std::endl;
  std::cout << "#" << std::endl;
  std::cout << "# Extras.C integral" << std::endl;
  std::cout << "#" << std::endl;
  std::cout << "##################################" << std::endl;

  return h->Integral(h->FindBin(f+0.00000001),h->FindBin(l+0.00000001));
}

void set_plot_style()
{
  const Int_t NRGBs = 5;
  const Int_t NCont = 255;

  Double_t stops[NRGBs] = { 0.00, 0.34, 0.61, 0.84, 1.00 };
  Double_t red[NRGBs]   = { 0.00, 0.00, 0.87, 1.00, 0.51 };
  Double_t green[NRGBs] = { 0.00, 0.81, 1.00, 0.20, 0.00 };
  Double_t blue[NRGBs]  = { 0.51, 1.00, 0.12, 0.00, 0.00 };
  TColor::CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont);
  gStyle->SetNumberContours(NCont);
  std::cout << "# Extras.C: " << "Setting plot style to ... something." << std::endl;
}

void set_plot_style_gr()
{
  const Int_t NRGBs = 2;
  const Int_t NCont = 255;

  Double_t stops[NRGBs] = { 0.00,1.00 };
  Double_t red[NRGBs]   = { 0.50,1.00 };
  Double_t green[NRGBs] = { 1.00,0.00 };
  Double_t blue[NRGBs]  = { 0.50,0.00 };
  TColor::CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont);
  gStyle->SetNumberContours(NCont);
  std::cout << "# Extras.C: Setting plot style to RB" << std::endl;
}

void set_plot_style_kurt()
{
  const Int_t NRGBs = 3;
  const Int_t NCont = 255;

  Double_t stops[NRGBs] = { 0.00, 0.50, 1.00 };
  Double_t red[NRGBs]   = { 0.00, 0.50, 1.00 };
  Double_t green[NRGBs] = { 0.00, 1.00, 0.00 };
  Double_t blue[NRGBs]  = { 1.00, 0.50, 0.00 };
  TColor::CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont);
  gStyle->SetNumberContours(NCont);
  std::cout << "# Extras.C: Setting plot style to KURT" << std::endl;
}

void set_plot_style_higgs()
{
  const Int_t NRGBs = 2;
  const Int_t NCont = 255;

  Double_t stops[NRGBs] = { 0.00,1.00 };
  Double_t red[NRGBs]   = { 1.00,0.50 };
  Double_t green[NRGBs] = { 1.00,0.50 };
  Double_t blue[NRGBs]  = { 1.00,1.00 };
  TColor::CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont);
  gStyle->SetNumberContours(NCont);
  std::cout << "# Extras.C: Setting plot style to ?" << std::endl;
}

void set_plot_style_gray()
{
  const Int_t NRGBs = 2;
  const Int_t NCont = 255;

  Double_t stops[NRGBs] = { 0.00,1.00 };
  Double_t red[NRGBs]   = { 1.00,0.40 };
  Double_t green[NRGBs] = { 1.00,0.40 };
  Double_t blue[NRGBs]  = { 1.00,0.40 };
  TColor::CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont);
  gStyle->SetNumberContours(NCont);
  std::cout << "# Extras.C: Setting plot style to ?" << std::endl;
}
