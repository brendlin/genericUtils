#ifndef GENERICUTILS_TAXISFUNCTIONS_H
#define GENERICUTILS_TAXISFUNCTIONS_H

#include "TPad.h"
#include "float.h"

namespace GU {

  void AutoFixAxes(TPad& can, bool symmetrize=false, bool ignorelegend=false);

  std::pair<double,double> AutoFixYaxis(TPad& can, bool ignorelegend=false,float forcemin=FLT_MIN,bool minzero=false);
  void FixYaxisRanges(TPad& can);
  void SetYaxisRanges(TPad& can,double ymin,double ymax);
  std::pair<double,double> GetYaxisRanges(TPad& can,bool check_all=false);

  void FixXaxisRanges(TPad& can);
  void SetXaxisRanges(TPad& can,double xmin,double xmax);
  std::pair<double,double> GetXaxisRanges(TPad& can,bool check_all=false);

  double MinimumForLog(TPad& can);
  std::pair<double,double> NearestNiceNumber(std::pair<double,double> ranges_in);

  void SetXaxisNdivisions(TPad& can, int a,int b,int c);
  void SetYaxisNdivisions(TPad& can, int a,int b,int c);

  bool CanvasHasPlot(TPad& can);

} // namespace GU

#endif // GENERICUTILS_TAXISFUNCTIONS_H
