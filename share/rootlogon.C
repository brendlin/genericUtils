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
  std::cout << "Setting plot style to RB \n" << std::endl;
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
  std::cout << "Setting plot style to KURT \n" << std::endl;
}

void rootlogon()
{
  // Load ATLAS style
  gROOT->LoadMacro("AtlasStyleColor.C");
  SetAtlasStyle();

  gStyle->SetPaintTextFormat("4.1f ");
  std::cout << "gStyle->SetPaintTextFormat(\"4.1f \")" << std::endl << std::endl;
  std::cout << "Plot options:" << std::endl;
  std::cout << "    set_plot_style()" << std::endl;
  std::cout << "    set_plot_style_gr()" << std::endl;
  std::cout << "    set_plot_style_kurt()" << std::endl;
  gStyle->SetOptTitle(0);
  gStyle->SetTitleFillColor(0);
  gStyle->SetTitleBorderSize(0);
  gStyle->SetTitleFont(42);
  gStyle->SetPadRightMargin(0.30);

  //TROOT->ForceStyle()
  
  set_plot_style_kurt();
}
