## @package Subscription
# \brief Suscription tools to map dataset to cfgfiles
#
# Developers:
#   Victor E. Bazterra
#   Kenneth James Smith

import os

from xml.dom.minidom import parse
from xml.dom.minidom import getDOMImplementation

## Main class to manipulate subscriptions.
class Subscriber:

  ## Constructor by file.
  def __init__(self, file=None):

    self.map = {}
    if file != None:
      self.read(file) 
  
  ## String for printing suscriptions.  
  def __str__(self):
    imp = getDOMImplementation()
    document = imp.createDocument(None, 'suscriptions', None)
    subscriptionsElement = document.documentElement
    for k1,v1 in self.map.iteritems():
      subscribeElement = document.createElement('subscribe')
      subscribeElement.setAttribute('dataset',k1)
      for k2,v2 in v1.iteritems():
        cfgfileElement = document.createElement('cfgfile')
        cfgfileElement.setAttribute('filename',k2)
        cfgfileElement.setAttribute('interface',v2)
        subscribeElement.appendChild(cfgfileElement)
      subscriptionsElement.appendChild(subscribeElement)
    return document.toprettyxml(" " * 2)

  ## Auxiliary function.
  def __getdata(self, nodes):
    rc = ''	
    for node in nodes:
      if node.nodeType == node.TEXT_NODE:
        rc = rc + node.data
    return rc
                                   
  ## Add a new suscription.  
  def add(self, dataset, cfgfile, active=True):
    if self.map.has_key(dataset):
      if self.map[dataset].has_key(cfgfile) == False:
        self.map[dataset][cfgfile] = active
    else:
      self.map[dataset] = {}
      self.map[dataset][cfgfile] = active

  ## Remove a suscription.    
  def remove(self, dataset, cfgfile):
    if self.map[dataset].has_key(cfgfile):
      del self.map[dataset][cfgfile]
      if len(self.map[dataset]) == 0:
        del self.map[dataset]

  ## Add a new suscription.  
  def set(self, dataset, cfgfile, interface):
    if self.map.has_key(dataset):
      if self.map[dataset].has_key(cfgfile):
        self.map[dataset][cfgfile] = interface 
  
  ## Read subscription from xml file.
  def read(self, file):
    dom = parse(file)
    try:
      subscriptionElements = dom.getElementsByTagName('subscribe')      
      for subscriptionElement in subscriptionElements:
        dataset = subscriptionElement.getAttribute('dataset')
        cfgfileElements = subscriptionElement.getElementsByTagName('cfgfile')        
        for cfgfileElement in cfgfileElements:
          filename  = cfgfileElement.getAttribute('filename')
          interface = cfgfileElement.getAttribute('interface')
          self.add(dataset, filename, interface)
              
    except:
      raise ErrorManager.SubscriptionError, 'subcribe element cannot be found'

  ## Write the suscriptions into a file. 
  def write(self, filename):
    file = open (filename, "w")
    file.write(str(self))
    
