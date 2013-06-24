## @package Configuration
# \brief Full configuration for ValidationTools
#
# Developers:
#   Victor E. Bazterra
#   Kenneth James Smith

import os

variables = {}

## get the validation tool director.
variables['VTRoot'] = os.getenv('VTOOLS_ROOT')

## set work areas for different cmssw distributions 
variables['WorkAreas'] = '/afs/cern.ch/user/b/bazterra/work/CMSSW'

## dropbox and web location
variables['DropBox'] = '/afs/cern.ch/user/b/bazterra/private/DropBox'
variables['WebPath'] = '/afs/cern.ch/user/b/bazterra/www/validation'

## Python pydrive command files
variables['PyCommandFile'] = 'Configuration/PyReleaseValidation/data/cmsDriver_commands.txt'

## Port poll time in ms.  
variables['PortPollTime'] = 5
## Mininul port number allow to use.  
variables['MinPortNumber'] = 5000

## Port number for JobMonitor.
variables['JobMonitorPort'] = 44790
## Default number of threads used by JobMonitor.
variables['JobMonitorNThreads'] = 2  
## Port number for DBSMonitor.
variables['DBSMonitorPort'] = variables['JobMonitorPort'] + 10
## Default number of threads used by DBSMonitor.
variables['DBSMonitorNThreads'] = 2 
## RSSListenerp oll time in seconds 
variables['DBSMonitorPollTime'] = 10

## String for requesting rss generator in DBS.
variables['RssGenerator'] = 'http://cmsdbs.cern.ch/DBS2_discovery/rssGenerator?'
## String for requesting logical file name for a given site.
variables['LFNForSite'] = 'https://cmsweb.cern.ch/dbs_discovery/getLFNsForSite?'  
## Site location strings for dbs.
variables['CERNSITE'] = 'srm.cern.ch'
variables['FNALSITE'] = 'cmssrm.fnal.gov'


