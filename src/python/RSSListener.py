## @package RSSListener
# \brief Polls RSS and makes config files for ValidationTools
#
# Developers:
#   Victor E. Bazterra
#   Kenneth James Smith
#

import os
from xml.dom.minidom import parse
import threading
import shutil
import commands
import pickle
import socket
import random

from string import letters

import ErrorManager
import Configuration 
import RSSParser
from Tools import Template
from Subscription import Subscriber


class Listener:

    def getJobs(self):
        return self.__jobList

    def __init__(self):
        self.__lfns = []
        self.__interface = []
        self.__cfg_List = []
        self.__dataset_list = []
        self.__finished_RSS = []
        
    def getdata(self, nodes):
        rc = ''
        for node in nodes:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def listen(self,  release, dataset, site=RSSParser.CERN, trigger=''):
        self.__release = release
        self.__dataset = dataset
        # Request a RSS with the following conditions
        dbsrss = RSSParser.Parser()
        dbsrss.request(release=release, dataset=dataset)
        # Check for a given trigger if there is an update.
        try:
          self.__lfns = dbsrss.trigger(format='txt', site=site, keyword=trigger).split()
        except ErrorManager.RSSParserError:
          return False
        return True

    def createcfgs(self, lock, postprocess):
        # Get the subscription list 
        subscriptions = Subscriber()
        subscriptions.read(Configuration.variables['VTRoot']+'/data/subscriptions.xml')

        # Message list
        messages = []
               
        # For a given dataset get all the subscripted templates
        if subscriptions.map.has_key(self.__dataset):
        
          for template, interface in subscriptions.map[self.__dataset].iteritems():
    
            # open the associated template file
            tfile = open(template, 'r')
            tobject = Template(tfile.read())
            tfile.close()
    
            # create the proper source string
            string = 'source = PoolSource{\n\nuntracked vstring fileNames = {\n'
            for i in range(len(self.__lfns)):
              if i == len(self.__lfns) - 1:
                string = string + '\'' + self.__lfns[i] + '\'\n'
              else:
                string = string + '\'' + self.__lfns[i] + '\',\n'
            string = string + '}\n}\n'

            # creates a config file
            lock.acquire()
            if os.path.isdir(Configuration.variables['DropBox'] + '/CfgFiles/' + self.__release + '/') == False:
              os.mkdir(Configuration.variables['DropBox'] + '/CfgFiles/' + self.__release + '/')
            lock.release()
            cfgfile = Configuration.variables['DropBox'] + '/CfgFiles/' + self.__release + '/' + self.__dataset + '__' + template.split('/')[-1].split('.')[0] + '.cfg'
            cfile = open(cfgfile, 'w')
            cfile.write( tobject.safe_substitute(lfns=string, dataset=self.__dataset) )
            cfile.close()

            # Add a message for submitting the job
            message = {}
            message['startjob'] = { 'groupid' : 'None', 'interface' : str(interface), 'release' : self.__release, 'cfgfile' : str(cfgfile), 'postprocess' : postprocess }
            messages.append(message)
        
        return messages        
