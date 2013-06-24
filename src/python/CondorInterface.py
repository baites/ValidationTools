## @package CondorInterface
# \brief Interface for running job by using condor
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

import Configuration
import ErrorManager
import Publisher

from Tools import Template 

## This class implements a job interface for condor
class Interface:

  ## Default constructor.
  def __init__(self):
    self.__scratch = ''
    self.__jobList = []
    self.__pollTime = 60
    self.__destination = ''

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

  ## Return the job.
  def jobid(self):
    return self.__jobList[0]

  ## Creates a project area  
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
    # Create a cmsrun script
    tfile = open (Configuration.variables['VTRoot'] + '/data/cmsrun.template' ,'r')
    template = Template(tfile.read())
    tfile.close()
    cfile = open ( self.__scratch + '/cmsrun', 'w' )
    cmssws = Configuration.variables['WorkAreas'] + '/' + release + '/src' 
    cfile.write( template.substitute(scratch=self.__scratch, cfg=cfgfile, cmssw=cmssws) )
    cfile.close()
    os.chmod( self.__scratch + '/cmsrun', 0755 )
    # Create a condor script
    tfile = open (Configuration.variables['VTRoot'] + '/data/condor/condor.template' ,'r')
    template = Template(tfile.read())
    tfile.close()
    cfile = open ( self.__scratch + '/condor.script', 'w' ) 
    cfile.write( template.substitute(scratch=self.__scratch) )
    cfile.close()

  ## Clean a project arearchival and cleaning scratch places.
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

  ## Implements the submit function for a condor job. 
  def submit(self):
 
    # Submit a job
    status, output = commands.getstatusoutput("condor_submit " + self.__scratch + '/condor.script')

    if status != 0:
      raise ErrorManager.InterfaceError, 'condor_submit fail !'

    jobNumbers = []
    jobStrings = []

    for line in output.split("\n"):
      i = 0
      A = len(line)
      #print A 
      while i < A-1:
        j = i+1
        while j < A:
          if line[i:j] == 'submitted to cluster':
              jobSubmit = int(line[0])
              line1 = line.strip(' ')
              jobStrings = line1.split(' ')
              jobInput = jobStrings[5] 
          j = j + 1
        i = i + 1
      k = 0
    while k < jobSubmit:
      self.__jobList.append(jobInput.rstrip('\n') + str(k))
      k = k + 1

  ## Implements the poll function for a condor job.
  def wait(self):
    if len(self.__jobList) == 0:
      raise ErrorManager.InterfaceError, 'Job list in empty (try to run submit first).'

    completedJobs = []

    for jobsEnd in self.__jobList:
      i = 0
      jobs = jobsEnd.rstrip('\n')
      while i == 0:
        j = 0
        status, output = commands.getstatusoutput("condor_q " + jobs)
        for newLine in output.split('\n'):
          begin = 0
          while begin < len(newLine) - 1:
            end = begin + 1
            while end < len(newLine):
              if newLine[begin:end] == jobs:
                j = j + 1
              end = end + 1
            begin = begin + 1
        if j == 0:
          i = 1
          print jobs + "  is completed!"
        if j > 0:
          time.sleep(self.__pollTime)
    completedJobs.append(jobs)
    print jobs+" Done"

