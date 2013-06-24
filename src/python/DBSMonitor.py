## @package DBSMonitor
# \brief Multiple dataset monitoring for ValidationTools
#
# Developers:
#   Victor E. Bazterra
#   Kenneth James Smith

import os
import time
import pickle
import shutil
import socket
import string
import threading
import Queue

import RSSListener
import ErrorManager
import Configuration 

from Subscription import Subscriber
from optparse import OptionParser

# Parsing command line option
usage = "usage: %prog [options]"
parser = OptionParser()
parser.add_option("-p", "--port", type="int", dest="port", default=Configuration.variables['DBSMonitorPort'], help="port used by the server")
parser.add_option("-n", "--threads", type="int", dest="nthreads", default=Configuration.variables['DBSMonitorNThreads'], help="number of threads use by the server")
(options, args) = parser.parse_args()


## Handler class for DBS monitoring. 
class Handler ( threading.Thread ):

  # Define the lock for this class
  lock = threading.Lock()

  ## Constructor.
  def __init__ ( self, polltime=Configuration.variables['DBSMonitorPollTime'] ):
    self.__scratch = None
    self.__polltime = polltime
    self.__listener = RSSListener.Listener()
    threading.Thread.__init__( self )

  ## Thread safe send function
  def send ( self, message ):
    # Acquire lock
    Handler.lock.acquire()
    # Connect to the server:
    server = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )        
    server.connect ( ( 'localhost', options.port ) )
    # Send a message
    server.send( pickle.dumps(message) )
    # Close the connection
    server.close()
    # Release the lock
    Handler.lock.release()

  ## Thread safe submit function
  def submit(self, messages):
    # Acquire lock
    Handler.lock.acquire()
    for message in messages:
      # Connect to the server:
      client = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
      client.connect ( ( 'localhost', Configuration.variables['JobMonitorPort'] ) )
      # Send a message    
      client.send( pickle.dumps(message) )
      # Close the connection
      client.close()
      # Release the lock
    Handler.lock.release()

  ## Run the handler.  
  def run ( self ):
    # Have our thread serve "forever"
    while True:
      # Get message out of the queue
      message = pickle.loads( queue.get() )
      # Decode the message
      release = message['startlisten']['release']
      dataset = message['startlisten']['dataset']
      site    = message['startlisten']['site']
      trigger = message['startlisten']['trigger']
      postprocess = message['startlisten']['postprocess']
      # Listen for a particular release, dataset, site 
      if self.__listener.listen( release, dataset, site, trigger):
        # Reporting last update
        status = time.strftime("Updated %a, %d %b %Y %H:%M:%S", time.gmtime())
        report = {}
        report['listenreport'] = { 'release' : release, 'dataset' : dataset, 'site' : site, 'trigger' : trigger, 'status' : status }
        self.send(report)
        # Job submittion
        self.submit(self.__listener.createcfgs(threading.Lock(), postprocess))
      else:
        time.sleep(self.__polltime)
        queue.put( pickle.dumps(message) )

# Create main status queue.
pool = {}

# Create main Queue.
queue = Queue.Queue (0)

# Check for a number of threads > than 0.
if options.nthreads < 0 :
  raise ErrorManager.ServerError, 'Negative number of threads.'

# Check for a port number > 5000.
if options.port < Configuration.variables['MinPortNumber'] :
  raise ErrorManager.ServerError, 'Port number must by > %d.' % Configuration.variables['MinPortNumber']

# Start a predefine number of handlers.
for x in xrange ( options.nthreads ) :
  handler = Handler()
  handler.start()

# Set up the server:
server = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
server.bind( ( '', options.port ) )
server.listen( Configuration.variables['PortPollTime'] )

# Have the server serve "forever":
while True:
  channel, details = server.accept()
  message = pickle.loads( channel.recv( 2048 ) )

  # Message decoding
  if message.has_key('startlisten'):

    release = message['startlisten']['release']
    site    = message['startlisten']['site']
    trigger = message['startlisten']['trigger']

    subscriptions = Subscriber()
    subscriptions.read(Configuration.variables['VTRoot']+'/data/subscriptions.xml')

    for dataset, subscriptions in subscriptions.map.iteritems():
      listenid = release  + '_' + dataset + '_' + site + '_' + trigger
      pool[ listenid ] = { 'release' : release, 'dataset' : dataset, 'site' : site, 'trigger' : trigger, 'status' : 'NoUpdate' }
      message['startlisten']['dataset'] = dataset
      queue.put ( pickle.dumps(message) )
      # Some wiered behavior from the blocking queue.

  elif message.has_key('listenreport'):
   
    release = message['listenreport']['release']
    dataset = message['listenreport']['dataset']
    site    = message['listenreport']['site']
    status  = message['listenreport']['status']
    listenid = release  + '_' + dataset + '_' + site + '_' + trigger
    pool[ listenid ] = { 'release' : release, 'dataset' : dataset, 'site' : site, 'trigger' : trigger, 'status' : status }

  elif message.has_key('status'):

    # Connect to the server:
    client = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    client.connect ( ( 'localhost', options.port + 1 ) )
    client.send ( pickle.dumps(pool) )
    client.close()
    
  elif message.has_key('stop'):
    print 'JobMonitor is stoping ... '
    flag = False
