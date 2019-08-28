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

#include "TEntryList.h"
#include <string.h>

//
// This function makes a PicoXaod with arbitrary branch names (separated by ",")
//
void makePicoXaod(TFile* oldfile,TTree* oldtree,const char* name,const char* cuts,char* branches,const char* outdir,const char* filename_nodotroot) {

  oldtree->SetBranchStatus("*",1);
  std::cout << Form("tree.Draw(\">>%s\",\"%s\")",name,cuts) << std::endl;
  oldtree->Draw(Form(">>%s",name),cuts,"entrylist");
  TEntryList* elist = (TEntryList*)gDirectory->Get(name);
  Long64_t listEntries = elist->GetN();
  std::cout << "number in TEntryList: " << listEntries << std::endl;
  oldtree->SetEntryList(elist);
  oldtree->SetBranchStatus("*",0);

  // Iterate over branches and set branch status of particular ones
  char* tok;
  tok = strtok(branches,",");
  while (tok != NULL) {
    oldtree->SetBranchStatus(tok,1);
    tok = strtok(NULL,",");
  }

  //Create a new file + a clone of old tree in new file
  TFile *newfile = new TFile(Form("%s/%s.root",outdir,filename_nodotroot),"recreate");
  TTree* newtree = oldtree->CopyTree("");
  
  oldtree->SetEntryList(0);
  newtree->AutoSave();

  // Copy any 0th-level histograms to the file too
  TIter next(oldfile->GetListOfKeys());
  TKey *key;
  while ( (key = (TKey*)next()) ) {
    TClass *cl = gROOT->GetClass(key->GetClassName());
    if (!cl->InheritsFrom("TH1")) continue;
    TH1 *h = (TH1*)key->ReadObj();
    newfile->cd();
    h->Write();
  }

  newfile->Close();
  delete elist;
  delete newfile;
}

//
// This function makes a PicoXaod for every category of the 2015+2016 Couplings analysis.
//
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

//
// To fix Z pileup (pdgId == 0) issue
//
void makePicoXaod_Zpileup(TFile* oldfile,TTree* oldtree,const char* name,const char* cuts,char* branches,const char* outdir,const char* filename_nodotroot) {

  oldtree->SetBranchStatus("*",1);
  std::cout << Form("tree.Draw(\">>%s\",\"%s\")",name,cuts) << std::endl;
  oldtree->Draw(Form(">>%s",name),cuts,"entrylist");
  TEntryList* elist = (TEntryList*)gDirectory->Get(name);
  Long64_t listEntries = elist->GetN();
  std::cout << "number in TEntryList: " << listEntries << std::endl;
  oldtree->SetBranchStatus("*",0);
/*   oldtree->SetBranchStatus("HGamMuon*",0); */

  std::vector<float> * eta_s2 = 0;
  std::vector<float> * pt = 0;
  std::vector<float> * phi = 0;

  oldtree->SetBranchStatus ("HGamPhotonsAuxDyn.eta_s2",1);
  oldtree->SetBranchAddress("HGamPhotonsAuxDyn.eta_s2",&eta_s2);

  oldtree->SetBranchStatus ("HGamPhotonsAuxDyn.pt"    ,1);
  oldtree->SetBranchAddress("HGamPhotonsAuxDyn.pt"    ,&pt);

  oldtree->SetBranchStatus ("HGamPhotonsAuxDyn.phi",1);
  oldtree->SetBranchAddress("HGamPhotonsAuxDyn.phi",&phi);


  int nKept = 0;

  // Iterate over branches and set branch status of particular ones
  char* tok;
  tok = strtok(branches,",");
  while (tok != NULL) {
    oldtree->SetBranchStatus(tok,1);
    tok = strtok(NULL,",");
  }

  //Create a new file + a clone of old tree in new file
  TFile *newfile = new TFile(Form("%s/%s.root",outdir,filename_nodotroot),"recreate");
  TTree* newtree = oldtree->CloneTree(0);

  float pileupFixWeight = 0;
  newtree->Branch("pileupFixWeight", &pileupFixWeight, "pileupFixWeight/F");

  TH2F* hist = new TH2F("hist","hist",500/*eta_s2*/,-2.5,2.5,630/*phi*/,-3.15,3.15);
  TH2F* histall = new TH2F("histall","histall",500/*eta_s2*/,-2.5,2.5,630/*phi*/,-3.15,3.15);
  TH1F* dupeList = new TH1F("dupes","dupes",100,0,100);

  for (Long64_t el = 0; el < listEntries; el++) {
    Long64_t entryNumber = elist->GetEntry(el);

    oldtree->GetEntry(entryNumber);

    float tmp_eta = (*eta_s2)[0];
    float tmp_phi = (*phi)[0];
    float tmp_pt = (*pt)[0]/1000.;
    int bin = hist->FindBin(tmp_eta,tmp_phi);

    histall->Fill(tmp_eta,tmp_phi);
    if (hist->GetBinContent(bin) > 0)
      continue;

    hist->Fill(tmp_eta,tmp_phi);
    nKept ++;

    pileupFixWeight = 1 + 1.04*TMath::Exp(-0.00770*(tmp_pt-15)*(tmp_pt-15));
    newtree->Fill();
  }

  for (int x = 0; x < histall->GetNbinsX(); x++) {
    for (int y = 0; y < histall->GetNbinsX(); y++) {
      dupeList->Fill(histall->GetBinContent(x,y));
    }
  }

  std::cout << "nKept: " << nKept << std::endl;

  // Copy any 0th-level histograms to the file too
  TIter next(oldfile->GetListOfKeys());
  TKey *key;
  while ( (key = (TKey*)next()) ) {
    TClass *cl = gROOT->GetClass(key->GetClassName());
    if (!cl->InheritsFrom("TH1")) continue;
    TH1 *h = (TH1*)key->ReadObj();
    newfile->cd();
    h->Write();
  }

  newfile->cd();
  hist->Write();
  dupeList->Write();
  newtree->AutoSave();

  newfile->Close();
  delete elist;
  delete newfile;
}

enum BitDefPhoton {
  /** @brief cluster eta range */
  ClusterEtaRange_Photon        =  0,
  /** @brief energy fraction in the third layer */
  ClusterBackEnergyFraction_Photon = 7,
  /** @brief cluster leakage into the hadronic calorimeter */
  ClusterHadronicLeakage_Photon =  10,
  /** @brief energy in 2nd sampling (e277) */
  ClusterMiddleEnergy_Photon    =  11,
  /** @brief energy ratio in 2nd sampling */
  ClusterMiddleEratio37_Photon  =  12,
  /** @brief energy ratio in 2nd sampling for photons */
  ClusterMiddleEratio33_Photon  =  13,
  /** @brief width in the second sampling */
  ClusterMiddleWidth_Photon     =  14,
  /** @brief fraction of energy found in 1st sampling */
  ClusterStripsEratio_Photon    =  15,
  /** @brief energy of 2nd maximum in 1st sampling ~e2tsts1/(1000+const_lumi*et) */
  ClusterStripsDeltaEmax2_Photon =  16,
  /** @brief difference between 2nd maximum and 1st minimum in strips (e2tsts1-emins1) */
  ClusterStripsDeltaE_Photon    = 17,
  /** @brief shower width in 1st sampling */
  ClusterStripsWtot_Photon      = 18,
  /** @brief shower shape in shower core 1st sampling */
  ClusterStripsFracm_Photon     = 19,
  /** @brief shower width weighted by distance from the maximum one */
  ClusterStripsWeta1c_Photon    = 20,
  /** @brief difference between max and 2nd max in strips */
  ClusterStripsDEmaxs1_Photon  = 21,
  /** @brief energy-momentum match for photon selection*/
  TrackMatchEoverP_Photon       = 22,
  /** @brief ambiguity resolution for photon (vs electron) */
  AmbiguityResolution_Photon    = 23,
  /** @brief isolation */
  Isolation_Photon              = 29,
  /** @brief calorimetric isolation for photon selection */
  ClusterIsolation_Photon       = 30,
  /** @brief tracker isolation for photon selection */
 TrackIsolation_Photon         = 31
};

const unsigned int HADLEAK_PHOTON =
  0x1 << ClusterHadronicLeakage_Photon;

const unsigned int CALOSTRIPS_PHOTONTIGHT =
  0x1 << ClusterStripsEratio_Photon     |
  0x1 << ClusterStripsDeltaEmax2_Photon |
  0x1 << ClusterStripsDeltaE_Photon     |
  0x1 << ClusterStripsWtot_Photon       |
  0x1 << ClusterStripsFracm_Photon      |
  0x1 << ClusterStripsWeta1c_Photon     |
  0x1 << ClusterStripsDEmaxs1_Photon    ;

const unsigned int CALOMIDDLE_PHOTON =
  0x1 << ClusterMiddleEnergy_Photon     |
  0x1 << ClusterMiddleEratio37_Photon   |
  0x1 << ClusterMiddleEratio33_Photon   |
  0x1 << ClusterMiddleWidth_Photon     ;

/* Just for reference... */
/** @brief Tight photon selection, minus the eta range */
const unsigned int PhotonTight = HADLEAK_PHOTON | CALOMIDDLE_PHOTON | CALOSTRIPS_PHOTONTIGHT;

//
// To add Fail-two-tight variable
//
void makePicoXaod_addFail2Tight(TFile* oldfile,TTree* oldtree,const char* name,const char* cuts,char* branches,const char* outdir,const char* filename_nodotroot) {

  oldtree->SetBranchStatus("*",1);
  std::cout << Form("tree.Draw(\">>%s\",\"%s\")",name,cuts) << std::endl;
  oldtree->Draw(Form(">>%s",name),cuts,"entrylist");
  TEntryList* elist = (TEntryList*)gDirectory->Get(name);
  Long64_t listEntries = elist->GetN();
  std::cout << "number in TEntryList: " << listEntries << std::endl;
  oldtree->SetBranchStatus("*",0);

  std::vector<unsigned int> * isEMTight = 0;
  oldtree->SetBranchStatus ("HGamPhotonsAuxDyn.isEMTight",1);
  oldtree->SetBranchAddress("HGamPhotonsAuxDyn.isEMTight",&isEMTight);

  // Iterate over branches and set branch status of particular ones
  char* tok;
  tok = strtok(branches,",");
  while (tok != NULL) {
    oldtree->SetBranchStatus(tok,1);
    tok = strtok(NULL,",");
  }

  //Create a new file + a clone of old tree in new file
  TFile *newfile = new TFile(Form("%s/%s.root",outdir,filename_nodotroot),"recreate");
  TTree* newtree = oldtree->CloneTree(0);

  std::vector<int> * failTwoTight = new std::vector<int>();
  newtree->Branch("HGamPhotonsAuxDyn.failTwoTight","vector<int>",&failTwoTight);

  for (Long64_t el = 0; el < listEntries; el++) {
    Long64_t entryNumber = elist->GetEntry(el);

    oldtree->GetEntry(entryNumber);

    failTwoTight->clear();

    // Check for failing 2 tight cuts
    for (int iel = 0;iel < (*isEMTight).size(); iel++) {
      int nFailTight = 0;

      // std::cout << "isEMTight: " << std::hex << (*isEMTight)[iel] << std::endl;
      if ( (*isEMTight)[iel] & (0x1 << ClusterHadronicLeakage_Photon ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterStripsEratio_Photon    ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterStripsDeltaEmax2_Photon) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterStripsDeltaE_Photon    ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterStripsWtot_Photon      ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterStripsFracm_Photon     ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterStripsWeta1c_Photon    ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterStripsDEmaxs1_Photon   ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterHadronicLeakage_Photon ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterMiddleEnergy_Photon    ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterMiddleEratio37_Photon  ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterMiddleEratio33_Photon  ) ) nFailTight++;
      if ( (*isEMTight)[iel] & (0x1 << ClusterMiddleWidth_Photon     ) ) nFailTight++;

      if (nFailTight >= 2) failTwoTight->push_back(1);
      else failTwoTight->push_back(0);

    }

    newtree->Fill();
  }

  // Copy any 0th-level histograms to the file too
  TIter next(oldfile->GetListOfKeys());
  TKey *key;
  while ( (key = (TKey*)next()) ) {
    TClass *cl = gROOT->GetClass(key->GetClassName());
    if (!cl->InheritsFrom("TH1")) continue;
    TH1 *h = (TH1*)key->ReadObj();
    newfile->cd();
    h->Write();
  }

  newtree->AutoSave();
  newfile->Close();

  delete elist;
  delete newfile;
}
