#ifndef GENERICUTILS_PLOTFUNCTIONS_H
#define GENERICUTILS_PLOTFUNCTIONS_H

#include <iostream>
#include <string>

#include "TH1.h"
#include "TGraph.h"
#include "TCanvas.h"
#include "TF1.h"
#include "TList.h"

namespace GU {

  TList* GetGlobalHistoCollector();

  // Add a histogram to a canvas.
  TH1*    AddHistogram(TPad& can, TH1&    hist, std::string drawopt="pE1", bool keepname=false);
  TGraph* AddHistogram(TPad& can, TGraph& hist, std::string drawopt="pE1", bool keepname=false);
  TF1*    AddHistogram(TPad& can, TF1&    hist, std::string drawopt="pE1", bool keepname=false);

  void SetupStyle(void);
  void FormatCanvasAxes(TPad& can);
  void FullFormatCanvasDefault(TPad& can,double lumi=36.1,double sqrts=13,
                               std::string additionaltext="",std::string status="Internal");

  std::vector<int> KurtColorPalate(void);

  // Set x- and y-axis labels. Do only *after* you have added your first histogram to the canvas.
  void SetAxisLabels(TPad& can,std::string xlabel,std::string ylabel,std::string yratiolabel="ratio");

  void SetColors(TPad& can,const std::vector<int>& colors=std::vector<int>(),bool fill=false,bool line=false);

  std::string GetLuminosityText(double lumi_fb=20.3);
  std::string GetSqrtsText(int sqrts=13);
  std::string GetAtlasInternalText(std::string status="Internal");

  void MakeLegend(TPad& can,double x1=-1,double y1=-1,double x2=-1,double y2=-1,
                  int ncolumns=1,int totalentries=0,
                  const std::vector<std::string>& options=std::vector<std::string>(),
                  const std::vector<std::string>& skip=std::vector<std::string>(),
                  int textsize=18);

  void DrawText(TPad& can,const std::vector<std::string> text,
                double x1=-1,double y1=-1,double x2=-1,double y2=-1,int totalentries=1,
                double angle=0,std::string align="",int textsize=18);

  void DrawText(TPad& can,const std::string text,
                double x1=-1,double y1=-1,double x2=-1,double y2=-1,int totalentries=1,
                double angle=0,std::string align="",int textsize=18);

  TCanvas* RatioCanvas(const char *name,const char *title,
                       Int_t canw=500,Int_t canh=600,double ratio_size_as_fraction=0.35);

  std::pair<TH1*   ,TH1*   > AddRatio(TPad& can,TH1&    hist,TH1&    ref_hist,
                                      std::string divide="",std::string drawopt="pE1");

  std::pair<TGraph*,TGraph*> AddRatio(TPad& can,TGraph& hist,TGraph& ref_hist,
                                      std::string divide="",std::string drawopt="pE1");

  std::pair<TH1*   ,TH1*   > AddRatioManual(TPad& can,TH1&    hist,TH1&    ratioplot,
                                            std::string drawopt1="pE1",std::string drawopt2="pE1");
  std::pair<TGraph*,TGraph*> AddRatioManual(TPad& can,TGraph& hist,TGraph& ratioplot,
                                            std::string drawopt1="pE1",std::string drawopt2="pE1");

  void Stack(TPad& can, bool reverse=false);

  TPad* GetBotPad(TPad& can);
  TPad* GetTopPad(TPad& can);

} // namespace GU

#endif // GENERICUTILS_PLOTFUNCTIONS_H
