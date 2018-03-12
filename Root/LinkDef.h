#include <genericUtils/PlotFunctions.h>

#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;
#pragma link C++ nestedclass;

#pragma link C++ namespace GU;

#pragma link C++ function GU::GetGlobalHistoCollector();
#pragma link C++ function GU::AddHistogram (TCanvas&, TH1&   , std::string, bool);
#pragma link C++ function GU::AddHistogram (TCanvas&, TGraph&, std::string, bool);
#pragma link C++ function GU::AddHistogram (TCanvas&, TF1&   , std::string, bool);

#endif
