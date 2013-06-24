## @package ForkInterface
# \brief Interface for running job by forking subprocesses
#
# Developers:
#   Victor E. Bazterra
#   Kenneth James Smith

import os
import shutil
import time
import commands
import random
import string
import popen2

import Configuration
import ErrorManager
import Publisher

from Tools import Template

## Interface class for implementing fork jobs
class Interface:

  ## Constructor.
  def __init__(self):
    self.__rstring = None
    self.__scratch = ''
    self.__jobid = None
    self.__pollTime = 60
    self.__release_dir = ''
    self.__dataset_dir = ''

  ## Helper function for archival by merging.
  def __archive(self, lock, destination, file):
    lock.acquire()
    archive = destination + '/' + self.__release + '.root'  
    tmpfile = destination + '/' + self.__release + 'T.root'
    logfile = destination + '/' + self.__release + '.log'
    if os.path.isfile( archive ) == False:
      shutil.move(file, archive)
    else:
      shutil.move(archive, tmpfile);
      # Run root script 
      status, output = commands.getstatusoutput( "hadd %s %s %s" % (archive, tmpfile, file) )
      # print output
      archiveLog = open (logfile,'a')
      archiveLog.write(output)
      archiveLog.close()
      os.remove(tmpfile)
    lock.release()    

  ## Set the polling time. 
  def pollTime(self, time = 60):
    self.__pollTime = time

  ## Associated jobid.
  def jobid(self):
    return self.__jobid

  ## Creates a project area.
  def create( self, release, cfgfile):
    # Get the release name
    self.__release = release
    # Get the cfg file name
    self.__package = cfgfile.split('/')[-1].split('.')[0]
    # Generate a random string
    rvector = [random.choice(string.letters) for x in xrange(10)]
    rstring = "".join(rvector)
    # Name of the scrtach area
    self.__scratch = Configuration.variables['DropBox'] + '/Scratch/' + rstring
    # Creates a directory
    os.mkdir( self.__scratch )
    # Copy cfg file to scratch area
    shutil.copy(cfgfile, self.__scratch)
    # Create a CMSRun script
    tfile = open (Configuration.variables['VTRoot'] + '/data/cmsrun.template' ,'r')
    template = Template(tfile.read())
    tfile.close()
    cfile = open ( self.__scratch + '/cmsrun', 'w' ) 
    cmssws = Configuration.variables['WorkAreas'] + '/' + release + '/src'
    cfile.write( template.substitute(scratch=self.__scratch, cfg=cfgfile.split('/')[-1], cmssw=cmssws) )
    cfile.close()
    os.chmod( self.__scratch + '/cmsrun', 0755 )

  ## Archival and cleaning scratch places.
  def clean(self, lock):
    lock.acquire()
    self.__release_dir = Configuration.variables['DropBox'] + '/Releases/' + self.__release 
    if os.path.isdir( self.__release_dir ) == False:
      os.mkdir ( self.__release_dir )
    lock.release()
    self.__dataset_dir = self.__release_dir + '/' + self.__package.split("__")[0]
    os.mkdir(self.__dataset_dir)
    for file in os.listdir(self.__scratch) :
      if file.split('.')[-1] == 'root':
        self.__archive(lock, self.__release_dir, self.__scratch + '/' + file) 
      elif file == 'stdout' or file == 'stderr' or file == 'log' or file.split('.')[-1] == 'log':  
        shutil.copy(self.__scratch + '/' + file, self.__dataset_dir)
    # remove scratch
    # shutil.rmtree( self.__scratch, True )

  ## Post processing.
  def postprocess(self, lock):
    # Create the final destination in the webpath 
    lock.acquire()
    release_webpath = Configuration.variables['WebPath'] + '/data/' + self.__release
    if os.path.isdir( release_webpath ) == False:
      os.mkdir ( release_webpath )
    lock.release()
    dataset_webpath = release_webpath + '/' + self.__package.split("__")[0]
    # Find all the root and log files and copy them to destination
    for file in os.listdir(self.__release_dir):
      if file.split('.')[-1] == 'root': 
        Publisher.StaticWeb().run(path=release_webpath, comparison=self.__release_dir + "/" + file)
      elif file.split('.')[-1] == 'log':
        shutil.copy(self.__release_dir + "/" + file, release_webpath)
    for file in os.listdir(self.__dataset_dir):
      if file.split('.')[-1] == 'log' :
        shutil.copy(self.__dataset_dir + "/" + file, dataset_webpath )
    
  ## Submmit a job using popen2 class. 
  def submit(self):
    return
    #status, output = commands.getstatusoutput(self.__scratch + '/cmsrun')    
    #self.__child = popen2.Popen4(self.__scratch + '/cmsrun')
    #self.__jobid = self.__child.pid
    
  ## Wait until the jobs are done.
  def wait(self):
    status, output = commands.getstatusoutput(self.__scratch + '/cmsrun')
    #self.__child.wait()
    #stdout = open(self.__scratch + '/stdout', 'w')
    #stdout.write( self.__child.fromchild.read() ) 

