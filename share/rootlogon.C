#include <iostream>
#include "TROOT.h"
#include "TInterpreter.h"
#include "AtlasStyleColor.h"
#include "Extras.h"


void rootlogon()
{
//   return;

  std::cout << "# rootlogon.C rootlogon()" << std::endl;

  // Load ATLAS style
  //gROOT->LoadMacro("AtlasStyleColor.C");
  //gROOT->LoadMacro("Extras.C");
  SetAtlasStyle();
  set_plot_style_kurt();

  gROOT->SetBatch(false);

  //std::cout << "# rootlogon.C: SetDefaultSumw2(kTRUE); // Thanks Rene Brun" << std::endl;
  //TH1::SetDefaultSumw2(kTRUE);

//   std::cout << "# rootlogon.C: " << "gStyle->SetPaintTextFormat(\"4.3f \")" << std::endl;
//   std::cout << "# rootlogon.C: " << "To turn off title: gStyle->SetOptTitle(0);" << std::endl;
//   std::cout << "# rootlogon.C: " << "For Z axis: gStyle->SetPadRightMargin(0.16);" << std::endl;
  std::cout << "Type ListExtras() to see extra macros." << std::endl;
}
