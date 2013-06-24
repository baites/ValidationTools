## @package JobMonitor
# \brief Basic job monitoring for ValidationTools
#
# Developers:
#   Victor E. Bazterra
#   Kenneth James Smith

import os
import sys
import pickle
import socket
import threading
import Queue
import commands

import ErrorManager
import Configuration
import ForkInterface, CondorInterface
import Publisher

from optparse import OptionParser


# Parsing command line option
parser = OptionParser()
parser.add_option("-p", "--port", type="int", dest="port", default=Configuration.variables['JobMonitorPort'], help="port used by the server")
parser.add_option("-n", "--threads", type="int", dest="nthreads", default=Configuration.variables['JobMonitorNThreads'], help="port used by the server")
(options, args) = parser.parse_args()


## Our thread class
class Handler ( threading.Thread ):

  ## Define the lock for this class
  lock = threading.Lock()

  ## Override Thread's __init__ method to accept the parameters needed:
  def __init__ ( self ):
    self.__scratch = None 
    threading.Thread.__init__( self )

  ## Define the basic send function
  def send ( self, message ):
    # Acquire lock
    Handler.lock.acquire()
    # Connect to the server:
    client = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )        
    client.connect ( ( 'localhost', options.port ) )
    # Send a message
    client.send( pickle.dumps(message) )
    # Close the connection
    client.close()
    # Release the lock
    Handler.lock.release()

  ## Code executed by the handler.
  def run ( self ):
    # Have our thread serve "forever"
    while True:
       # Get a client out of the queue
       message = pickle.loads( queue.get() )
       # Check if we actually have an actual client in the client variable:
       if message.has_key('startjob'):
         # Select the job interface
         interface = None
         itype   = message['startjob']['interface']
         release = message['startjob']['release']
         cfgfile = message['startjob']['cfgfile']
         postprocess = message['startjob']['postprocess']
         if itype  == "fork":
           interface = ForkInterface.Interface()            
         elif itype == "condor":
           interface = CondorInterface.Interface()
         else:
           raise ErrorManager.JobMonitorError, 'Unknown ' + client[0] + ' interface'           
         # Create a project area
         interface.create(release, cfgfile)
         # Submit the job
         interface.submit()
         # Send job report
         message = {}
         # Combined name for jobid (interface + jobid)
         jobid = str(interface.jobid())
         message = {}
         message['jobreport'] = { 'release' : release, 'interface' : itype, 'cfgfile' : cfgfile.split('/')[-1], 'jobid' : jobid, 'status' : 'submitted' }
         self.send(message)
         # Wait for finishing the job
         interface.wait()
         # Send job report
         message = {}
         message['jobreport'] = { 'release' : release, 'interface' : itype, 'cfgfile' : cfgfile.split('/')[-1], 'jobid' : jobid, 'status' : 'cleaning' }
         self.send(message)
         # Cleaning the project area
         interface.clean(Handler.lock)
         if postprocess == True:
           # Send job repor
           message = {}
           message['jobreport'] = { 'release' : release, 'interface' : itype, 'cfgfile' : cfgfile.split('/')[-1], 'jobid' : jobid, 'status' : 'postprocess' }
           self.send(message)
           # Post process by the plugin
           interface.postprocess(Handler.lock)
         # Send job report
         message = {}
         message['jobreport'] = { 'release' : release, 'interface' : itype, 'cfgfile' : cfgfile.split('/')[-1], 'jobid' : jobid, 'status' : 'done' }
         self.send(message)           


# Create main status queue.
pool = {}

# Create main Queue.
queue = Queue.Queue (0)

# Check for a number of threads > than 0.
if options.nthreads < 0:
  raise ErrorManager.JobMonitorError, 'Negative number of threads.'

# Check for a port number > 5000.
if options.port < 5000  and options.nthreads > 65535 :
  raise ErrorManager.JobMonitorError, 'Port number interval is [5000,65535].'

for x in xrange ( options.nthreads ) :
  handler = Handler()
  handler.start()

# Set up the server:
server = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
server.bind ( ( '', options.port ) )
server.listen ( Configuration.variables['PortPollTime'] )

flag = True

# Have the server serve "forever"
while flag:
  # Open a channel for communications
  channel, details = server.accept()
  message = pickle.loads( channel.recv( 2048 ) )

  # print message

  # Message decoding
  if message.has_key('startjob'):

    release   = message['startjob']['release']
    interface = message['startjob']['interface']
    cfgfile   = message['startjob']['cfgfile']
    joblabel  = release + "_" + interface + "_" + cfgfile.split('/')[-1]

    # job bookeeping         
    pool[ joblabel ] = { 'release' : release, 'interface' : interface, 'cfgfile' : cfgfile.split('/')[-1], 'jobid' : 'None', 'status' : 'received' }
    queue.put ( pickle.dumps(message) )

  elif message.has_key('jobreport'):

    release   = message['jobreport']['release']
    interface = message['jobreport']['interface']
    cfgfile   = message['jobreport']['cfgfile']
    jobid     = message['jobreport']['jobid']
    status    = message['jobreport']['status']
    joblabel = release + "_" + interface + "_" + cfgfile.split('/')[-1]
        
    # Job bookeeping
    pool[ joblabel ] = { 'release' : release, 'interface' : interface, 'cfgfile' : cfgfile, 'jobid' : jobid, 'status' : status }
        
  elif message.has_key('status'):

    # Connect to the server:
    client = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    client.connect ( ( 'localhost', options.port + 1 ) )
    client.send ( pickle.dumps(pool) )
    client.close()

  elif message.has_key('stop'):
    print 'JobMonitor is stoping ... '
    flag = False
