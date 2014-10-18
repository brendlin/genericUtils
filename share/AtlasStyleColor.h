//
// ATLAS Style, based on a style file from BaBar
//

#include <iostream>
//#include "AtlasStyle.h"
#include "TROOT.h"

using namespace std;


void SetAtlasStyle ()
{
  cout << "# AtlasStyleColor.h SetAtlasStyle" << endl;
  
  static TStyle* atlasStyle = 0;
  if ( atlasStyle==0 ) atlasStyle = AtlasStyle();
  gROOT->SetStyle("ATLAS");
  //gROOT->ForceStyle();
}

TStyle* AtlasStyle() 
{
  
  TStyle *atlasStyle = new TStyle("ATLAS","Atlas style");

  // use plain black on white colors
  Int_t icol=0; // WHITE
  atlasStyle->SetFrameBorderMode(icol);
  atlasStyle->SetFrameFillColor(icol);
  atlasStyle->SetCanvasBorderMode(icol);
  atlasStyle->SetCanvasColor(icol);
  atlasStyle->SetPadBorderMode(icol);
  atlasStyle->SetPadColor(icol);
  atlasStyle->SetStatColor(icol);
  //atlasStyle->SetFillColor(icol); // don't use: white fill color for *all* objects

  // set the paper & margin sizes
  atlasStyle->SetPaperSize(20,26);

  // set margin sizes
  atlasStyle->SetPadTopMargin(0.05); // 0.05 // k
  atlasStyle->SetPadRightMargin(0.05); // 0.05 // k
  atlasStyle->SetPadBottomMargin(0.11);
  atlasStyle->SetPadLeftMargin(0.16); // 0.16 // k

  // set title offsets (for axis label)
  atlasStyle->SetTitleXOffset(1.4);
  atlasStyle->SetTitleYOffset(1.4);

  // use large fonts
  //Int_t font=72; // Helvetica italics
  Int_t font=43; // Helvetica
  Double_t tsize = 24; // 0.05 // k
  atlasStyle->SetTextFont(font);

  //atlasStyle->SetTextSize(tsize);
  atlasStyle->SetLabelFont(font,"x");
  atlasStyle->SetTitleFont(font,"x");
  atlasStyle->SetLabelFont(font,"y");
  atlasStyle->SetTitleFont(font,"y");
  atlasStyle->SetLabelFont(font,"z");
  atlasStyle->SetTitleFont(font,"z");
  
  atlasStyle->SetLabelSize(tsize,"x");
  atlasStyle->SetTitleSize(tsize,"x");
  atlasStyle->SetLabelSize(tsize,"y");
  atlasStyle->SetTitleSize(tsize,"y");
  atlasStyle->SetLabelSize(tsize,"z");
  atlasStyle->SetTitleSize(tsize,"z");

  // use bold lines and markers
  atlasStyle->SetMarkerStyle(20);
  atlasStyle->SetMarkerSize(1.2); // 1.2 // k
  atlasStyle->SetHistLineWidth(2.);
  atlasStyle->SetLineStyleString(2,"[12 12]"); // postscript dashes

  // get rid of X error bars 
  //atlasStyle->SetErrorX(0.001);
  // get rid of error bar caps
  atlasStyle->SetEndErrorSize(3.); // 0 // k

  // do not display any of the standard histogram decorations
  atlasStyle->SetOptTitle(0);
  //atlasStyle->SetOptStat(1111);
  atlasStyle->SetOptStat(0);
  //atlasStyle->SetOptFit(1111);
  atlasStyle->SetOptFit(0);

  // put tick marks on top and RHS of plots
  //atlasStyle->SetPadTickX(1);
  //atlasStyle->SetPadTickY(1);

  return atlasStyle;

}
