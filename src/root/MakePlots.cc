
#include "MakePlots.h"

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <fstream>

#include "TString.h"
#include "TSystem.h"
#include "TFile.h"

#include "TObject.h"

#include "TKey.h"
#include "TImageDump.h"
#include "TLegend.h"


static std::vector<std::string> getAllKeys (const TDirectory *, const std::string &);


MakePlots::MakePlots() 
{
  path = "";
  logaxis = false;
  extension = "png";
}


void MakePlots::Draw(const TString & comparisonFileName, const TString & referenceFileName) 
{
  // Get the comparison file
  TFile * comparisonFile = new TFile(comparisonFileName);

  // Get the comparison directory
  comparisonFile->cd();
  TDirectory * comparisonDirectory = gDirectory;
  
  // Get the reference directory
  TFile * referenceFile = 0;
  TDirectory * referenceDirectory = 0;  
  if (!referenceFileName.IsNull())
  {
    referenceFile = new TFile(referenceFileName);
    referenceFile->cd();
    referenceDirectory = gDirectory;
  }

  // Reset the dirlevel counter
  dirlevel = 0;
	    
  // Draw the directory
  Draw("", comparisonDirectory, referenceDirectory);  
}


void MakePlots::Draw(const TString & prefix, TDirectory * cDirectory, TDirectory * rDirectory)
{
  // Directory level variable
  dirlevel++;
  
  // Subdirectory name containers
  std::vector<std::string> cSubdirectories, rSubdirectories;
  
  // Get the comparison subdirectories
  cSubdirectories = getAllKeys(cDirectory, "TDirectoryFile");
  
  // Get the reference subdirectories if the reference directory exist
  if (rDirectory) rSubdirectories = getAllKeys(rDirectory, "TDirectoryFile");

  // Loop over the subdirectories recursively  
  for (unsigned i = 0; i < cSubdirectories.size(); ++i)
  {
  	// Get the subdirectories names
    TDirectory * cSubdirectory;
    TDirectory * rSubdirectory = 0;
    cDirectory->GetObject(cSubdirectories[i].c_str(), cSubdirectory);
    if (rDirectory) rDirectory->GetObject(cSubdirectories[i].c_str(), rSubdirectory);
    // Set the name of the prefix file 
    TString nprefix;
    if (dirlevel <= 2)
      nprefix = "";
    else if(dirlevel == 3 || dirlevel == 4)
    {
      nprefix = prefix + cSubdirectories[i].c_str(); nprefix += "/";
      gSystem->mkdir(path + "/" + nprefix);
    }
    else 
    {
      nprefix = prefix + cSubdirectories[i].c_str(); nprefix += "__";  	
    }
    Draw(nprefix, cSubdirectory, rSubdirectory);
  }
  
  std::vector<std::string> comparisonKeys, referenceKeys;
  
  // Get the plot keys from comparison directory
  comparisonKeys = getAllKeys(cDirectory, "TH1F");

  // Get the plot keys from reference directory (if it exists)
  if (rDirectory) referenceKeys = getAllKeys(rDirectory, "TH1F");

  // Loop over the plots in the directories
  for (unsigned i = 0; i < comparisonKeys.size (); ++i)
  {
    // Get the plot (TODO: extend this to other objects)
    TH1 * cPlot;
    TH1 * rPlot = 0;
    cDirectory->GetObject (comparisonKeys[i].c_str(), cPlot);
    if(rDirectory) rDirectory->GetObject (comparisonKeys[i].c_str(), rPlot);
    // Draw the plot
    Draw(prefix, cPlot, rPlot); 
  }
  dirlevel--;
}


void MakePlots::Draw(const TString & prefix, TH1 * comparison, TH1 * reference)
{
  // Create a canva for the plot 
  TString plotName(comparison->GetName());
  TCanvas * canvas = new TCanvas("cv_" + TString(plotName), "cv_" + TString(plotName), 400, 400);

  // Create a label
  TLatex *label = new TLatex(0.01, 0.01, plotName);
  label->SetNDC();
  label->SetTextColor(15);
  label->SetTextSize(0.02);
	
  // Plot the comparison
  comparison->Draw();
  label->Draw();

  // Set the logarithmic scale
  if (logaxis)
  {
	gPad->SetLogy();
	gPad->SetGrid();
  }

  // Plot a superposition between reference and comparison
  if (reference)
  {
    // Plot the reference with different color
    reference->SetLineColor(kRed);
    reference->SetMarkerColor(kRed);    
	reference->Draw("same");
  	
  	// Chi2 test between histograms
    char buf[1024];
    double chi2Test = reference->Chi2Test(comparison,"UFOF");
    sprintf (buf, "#chi^{2}= %1.2f", chi2Test);
	    
	TLatex * labelchi2 = new TLatex(0.4, 0.91, buf);
	labelchi2->SetNDC();
	labelchi2->SetTextSize(0.035);
	labelchi2->Draw();
	
    // KG test between histograms
    double KGTest = reference->KolmogorovTest(comparison,"UO");
    sprintf (buf, "KG= %2.2f", KGTest);
    
    // Change the color of the histogram if KGTest fails
    if (KGTest<0.8) gPad->SetFillColor(kYellow);
    
    TLatex * labelkg = new TLatex(0.6,0.91,buf);
    labelkg->SetNDC();
    labelkg->SetTextSize(0.035);
    labelkg->Draw();
  }
  
  // Save the canvas as png
  canvas->cd();

  if (comparison->GetEntries())
    canvas->Print(path + "/" + prefix + TString(plotName) + "." + extension, extension);  
}


static std::vector<std::string> getAllKeys (const TDirectory * fDir, const std::string & fClassName) 
{
  std::vector<std::string> result;
  TIter next (fDir->GetListOfKeys ());
  
  for (TKey* key = 0; (key = (TKey *) next());)
  {
    if (fClassName == key->GetClassName ())
      result.push_back (std::string (key->GetName ()));
  }
  
  return result;
}

