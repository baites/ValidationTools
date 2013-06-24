## @package Publisher
# \brief StaticWeb and automated email for ValidationTools
#
# Developers:
#   Victor E. Bazterra
#   Kenneth James Smith
#


import os
import commands
import tempfile
import shutil
import smtplib
import Configuration
import ErrorManager
import threading 


## Creates static web with histogram plots 
class StaticWeb:
  
  ## Given a root file plots all the histograms.  
  def run ( self, path, comparison, reference=''):
    # Creates a temporal file for executing root
    rootFile = tempfile.NamedTemporaryFile('w',suffix='.C')
    # rootFile = open ('/tmp/Holanda.C','w')
    # Create string to plot histograms
    string = 'void '
    string = string + rootFile.name.split("/")[-1].split(".")[0].replace('-','_') + '() {\n'  
    string = string + 'gROOT->SetStyle(\"Plain\");\n'    
    string = string + 'gSystem->Load(\"' + Configuration.variables['VTRoot'] + '/src/root/libMakePlots.so\");\n'
    string = string + 'MakePlots maker;\n'
    string = string + "maker.SetPath(\""+path+"\");\n"
    string = string + "maker.Draw(\""+comparison+"\");\n }"
    # Write the string
    rootFile.write( string )
    # Fluch the cache
    rootFile.flush()
    # Run root script 
    status, output = commands.getstatusoutput("root -l -b -q " + rootFile.name ) 
    # print output
    # Close tmp file
    rootFile.close()
    makePlots = open (path+"/MakePlots.log" ,'a')
    makePlots.write(output)
    makePlots.close()
