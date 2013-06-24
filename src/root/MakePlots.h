#ifndef MakePlots_h
#define MakePlots_h

/** \class MakePlots
 *
 * Analyze ROOT files produced by analyzer and create plots
 *
 * \author Francisco Yumiceva, Fermilab (yumiceva@fnal.gov)
 * \author Victor E. Bazterra, UIC
 *
 * \version $Id: MakePlots.h,v 1.8 2008/04/03 16:28:30 bazterra Exp $
 *
 */

#include "TCanvas.h"
#include "TDirectory.h"
#include "TH1.h"
#include "TLatex.h"
#include "TString.h"

//! Create plots from a given root file.
class MakePlots {

 public:

  //! Void constructor
  MakePlots();
  
  //! Draw the plots
  void Draw(
    const TString & comparisonFileName,
    const TString & referenceFileName = TString()
  );

  //! Set path  
  void SetPath(const TString & name) { path = name; }

  //! Set the file extension  
  void SetExtension(const TString & name) { extension = name; }

  //! Set the log axis flag
  void SetLogAxis(bool option) { logaxis = option; }
  	
 private:

  int dirlevel;
  bool logaxis;
  TString path, extension;

  void Draw(const TString &, TDirectory *, TDirectory * referenceDirectory = 0);
  void Draw(const TString &, TH1 *, TH1 * reference = 0);  
};

#endif
