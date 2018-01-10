#include "TH1.h"
#include "TH2.h"
#include "TCanvas.h"
#include "TColor.h"
#include "TStyle.h"
#include <string>
#include <stdlib.h>
#include <iostream>
#include <sstream>
#include "TBrowser.h"
#include "TTree.h"
#include "TChain.h"
#include "TFile.h"
#include "TDirectory.h"

#include "TPRegexp.h"
#include "RooAbsReal.h"
#include "RooDataHist.h"
#include "RooCmdArg.h"
#include "RooGlobalFunc.h"

#include "TEntryList.h"
#include <string.h>

void chi2FitTo_KB(RooAbsReal& fcn,RooDataHist& data
/*                   ,const RooCmdArg& arg1=RooCmdArg::none(), */
/*                   const RooCmdArg& arg2=RooCmdArg::none(),const RooCmdArg& arg3=RooCmdArg::none(), */
/*                   const RooCmdArg& arg4=RooCmdArg::none(),const RooCmdArg& arg5=RooCmdArg::none() */
                  ){
  fcn.chi2FitTo(data
                ,RooFit::Extended(kTRUE)
                /* ,RooFit::Save() */
                ,RooFit::Minimizer("Minuit2")
                ,RooFit::Strategy(2)
                ,RooFit::Range("lower,upper")
                /* ,RooFit::Range("all") */
                /* ,RooFit::Optimize() */
                /* ,RooFit::DataError(RooAbsData::SumW2) */
                ,RooFit::DataError(RooAbsData::Poisson)
/*                 ,RooFit::Verbose(kTRUE) */
                );
  return;
}

void ListExtras(void){
  std::cout << "# Extras.C: " << "Plot options:"             << std::endl;
  std::cout << "# Extras.C: " << "    set_plot_style()"      << std::endl;
  std::cout << "# Extras.C: " << "    set_plot_style_gr()"   << std::endl;
  std::cout << "# Extras.C: " << "    set_plot_style_kurt()" << std::endl;
  std::cout << "# Extras.C: " << "    set_plot_style_sth()" << std::endl;
  std::cout << "# Extras.C: " << "Functions:"            << std::endl;
  std::cout << "# Extras.C: " << "    h = hist(\"h\",c)" << std::endl;
  std::cout << "# Extras.C: " << "    i = integral(TH1* h,double binedge1, double binedge2)" << std::endl;
  std::cout << "# Extras.C: " << "    h = SF(TH2F* h,TH2F* err,int bin)" << std::endl;
  std::cout << "# rootlogon.C: " << "gStyle->SetPaintTextFormat(\"4.3f \")" << std::endl;
  std::cout << "# rootlogon.C: " << "To turn off title: gStyle->SetOptTitle(0);" << std::endl;
  std::cout << "# rootlogon.C: " << "For Z axis: gStyle->SetPadRightMargin(0.16);" << std::endl;
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

TH1F* SF(TH2* h,TH2* err,TH2* err2,int bin){
  TH1F* hist;
  TH1F* error;
  TH1F* error2;
  stringstream name1,name2,name3;
  name1 << h->GetName() << bin;
  name2 << err->GetName() << bin;
  name3 << err2->GetName() << bin;
  string name1s = name1.str();
  string name2s = name2.str();
  string name3s = name3.str();
  hist   = (TH1F*)h->ProjectionY(name1s.c_str(),bin,bin);
  error  = (TH1F*)err->ProjectionY(name2s.c_str(),bin,bin);
  error2 = (TH1F*)err2->ProjectionY(name3s.c_str(),bin,bin);
  for(int i=0;i<hist->GetNbinsX();i++){
    hist->SetBinError(i+1,sqrt(pow(error->GetBinContent(i+1),2)+pow(error2->GetBinContent(i+1),2)));
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

double integral(TH1* h,double f,double l){
/*   std::cout << "##################################" << std::endl; */
/*   std::cout << "#" << std::endl; */
/*   std::cout << "# Extras.C integral" << std::endl; */
/*   std::cout << "#" << std::endl; */
/*   std::cout << "##################################" << std::endl; */
  // Good to a precision of 1 in 10^6
  return h->Integral(h->FindBin(f*(1+1e-6)),h->FindBin(l*(1-1e-6)));
}

static char DataTypeToChar(EDataType datatype)
{
  // Return the leaflist 'char' for a given datatype.
  switch(datatype) {
  case kChar_t:     return 'B';
  case kUChar_t:    return 'b';
  case kBool_t:     return 'O';
  case kShort_t:    return 'S';
  case kUShort_t:   return 's';
  case kCounter:
  case kInt_t:      return 'I';
  case kUInt_t:     return 'i';
  case kDouble_t:
  case kDouble32_t: return 'D';
  case kFloat_t:
  case kFloat16_t:  return 'F';
  case kLong_t:     return 0; // unsupported
  case kULong_t:    return 0; // unsupported?
  case kchar:       return 0; // unsupported
  case kLong64_t:   return 'L';
  case kULong64_t:  return 'l';

  case kCharStar:   return 'C';
  case kBits:       return 0; //unsupported

  case kOther_t:
  case kNoType_t:
  default:
    return 0;
  }
  return 0;
}

void dump(const char* grep="",const char* name="CollectionTree") {
  // assuming you are in the directory with the tree.
  TTree* t = (TTree*)gDirectory->Get(name);
  if (!t) {
    std::cout << "TTree name " << name << " is wrong!" << std::endl;
    return;
  }
  EDataType type; TClass* cl;
  TPRegexp matchTo(grep);
  for (auto i : *(t->GetListOfBranches()) ) {
    TString asdf = i->GetName();
    if (!asdf(matchTo)) continue;
    dynamic_cast<TBranch*>(i)->GetExpectedType(cl,type);
    std::cout << i->GetName() 
              << " type: \"" << DataTypeToChar(type) << "\""
              << " (" << ((TBranchElement*)i)->GetClassName() << ")" << std::endl;
  }
  return;
}

void set_plot_style() // Some weird default with a bunch of colors
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

void set_plot_style_gr() // Green -> Red
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

void set_plot_style_kurt() // Blue -> Green -> Red
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

TBrowser* b()
{
  //TRootBrowser* BROWSER = new TRootBrowser(0,"b",1265,750);
  //TBrowser* BROWSER = new TBrowser();
  TBrowser* BROWSER = new TBrowser(0,"b",1265,750);
  return BROWSER;
}

void makePicoXaod_Categories(TChain* oldchain,const char* name,const char* cuts,const char* outdir,char* categories) {
  oldchain->SetBranchStatus("*",1);
  std::cout << Form("tree.Draw(\">>selection\",\"%s\",\"entrylist\")",cuts) << std::endl;
  oldchain->Draw(">>selection",cuts,"entrylist");
  TEntryList* elist = (TEntryList*)gDirectory->Get("selection");
  oldchain->SetEntryList(elist);
  oldchain->SetBranchStatus("*",0);
  oldchain->SetBranchStatus("HGamEventInfoAuxDyn.m_yy",1);
  int catCoup_Moriond2017BDT;
  oldchain->SetBranchStatus ("HGamEventInfoAuxDyn.catCoup_Moriond2017BDT",1);
  oldchain->SetBranchAddress("HGamEventInfoAuxDyn.catCoup_Moriond2017BDT",&catCoup_Moriond2017BDT);

  //Create a new file + a clone of old tree in new file
  std::vector<TFile*> files;
  std::vector<TTree*> trees;
  char* tok;
  tok = strtok(categories,".");
  while (tok != NULL) {
    TString filename = Form("%s/%s_%s.root",outdir,name,tok);
    //std::cout << "Making file " << filename << std::endl;
    files.push_back(new TFile(filename.Data(),"recreate"));
    TTree* tmp = oldchain->CloneTree(0);
    trees.push_back(tmp);
    tok = strtok(NULL,".");
  }
  
  Int_t treenum = 0;
  Long64_t listEntries = elist->GetN();
  //std::cout << "number in TEntryList: " << listEntries << std::endl;
  for (Long64_t el = 0; el < listEntries; el++) {
    // From Rene Brun, from TEntryList class def
    Long64_t treeEntry = elist->GetEntryAndTree(el,treenum);
    Long64_t chainEntry = treeEntry+oldchain->GetTreeOffset()[treenum];
    //printf("el=%lld, treeEntry=%lld, chainEntry=%lld, treenum=%d\n", el, treeEntry, chainEntry, treenum);
    oldchain->LoadTree(chainEntry); // this also returns treeEntry
    oldchain->GetEntry(chainEntry); // redundant?
    
    trees[0]->Fill();
    for (unsigned int i=0;i<trees.size();++i) {
      if (catCoup_Moriond2017BDT == i) trees[i]->Fill();
      if (i == 19 && catCoup_Moriond2017BDT == 20) trees[i]->Fill(); // merge VHMET_BSM --> HIGH
      if (i == 23 && catCoup_Moriond2017BDT == 24) trees[i]->Fill(); // merge VHdilep_HIGH --> LOW
    }
  }

  oldchain->SetEntryList(0);
  for (unsigned int i=0;i<trees.size();++i) {
    std::cout << files[i]->GetName() << ": " << trees[i]->GetEntries() << std::endl;
    trees[i]->AutoSave();
    files[i]->Close();
  }

  delete elist;
  return;
}

void makePicoXaod(TTree* oldtree,const char* name,const char* cuts,const char* outdir,const char* filename_nodotroot) {

  oldtree->SetBranchStatus("*",1);
  std::cout << Form("tree.Draw(\">>%s\",\"%s\")",name,cuts) << std::endl;
  oldtree->Draw(Form(">>%s",name),cuts,"entrylist");
  TEntryList* elist = (TEntryList*)gDirectory->Get(name);
  Long64_t listEntries = elist->GetN();
  std::cout << "number in TEntryList: " << listEntries << std::endl;
  oldtree->SetEntryList(elist);
  oldtree->SetBranchStatus("*",0);
  oldtree->SetBranchStatus("HGamEventInfoAuxDyn.m_yy",1);
  
  //Create a new file + a clone of old tree in new file
  TFile *newfile = new TFile(Form("%s/%s.root",outdir,filename_nodotroot),"recreate");
  TTree* newtree = oldtree->CopyTree("");
  
  oldtree->SetEntryList(0);
  newtree->AutoSave();
  newfile->Close();
  delete elist;
  delete newfile;
}
