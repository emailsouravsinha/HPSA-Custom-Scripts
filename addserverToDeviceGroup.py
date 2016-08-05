#!/opt/opsware/bin/python2
#
#Thu Aug 4 13: 17: 46 UTC 2016 Sourav Sinha
#
# Adds a server to a device group.
#
#Inputs DeviceGroupId & ServerId


# The typical setups, imports, and globals
import sys
import os
import inspect
import traceback
import pprint
import re
import getopt

sys.path.append("/opt/opsware/pylibs2")
from pytwist import *
from pytwist.com.opsware.search import Filter

ts = twistserver.TwistServer()
ds = ts.device.DeviceGroupService
ss = ts.server.ServerService
deviceGroupID = ''
serverID = ''


def usage():
  # Prints out help so the user knows what the options are
 
   usage = """
	Usage:
	 
	   -h --help             Prints this
	 
	   Arguments:
	   -d, --deviceGroupId   use with a Device Group Id from HPSA
	   -s, --serverId        use with a Server Id
	   
	   Syntax:
	   addserverToDeviceGroup.py -d <deviceGroupId> -s <serverId>	
	   """
 
   print usage

def main(argv):
  # Gets the details the user is looking for
 
   try:
     opts, args = getopt.getopt(argv, "hd:s:", ["deviceGroupId=", "serverId="])
   except getopt.GetoptError:
		usage()
		sys.exit(1)
	 
   if len(sys.argv) < 4 :
		usage()
		sys.exit(1)	 
	 
   for opt, arg in opts:
	  if opt == '-h':
			print 'addserverToDeviceGroup.py -d <deviceGroupId> -s <serverId>'
			sys.exit()
	  elif opt in ("-d", "--deviceGroupId"):
		    deviceGroupID = arg
	  elif opt in ("-s", "--serverId"):
		    serverID = arg
			
   filter = Filter()
   filter.expression = 'DeviceGroupVO.pK EQUAL_TO "%s"' % deviceGroupID

   filter2 = Filter()
   filter2.expression = 'ServerVO.pK EQUAL_TO "%s"' % serverID

   deviceGroup_refs = ds.findDeviceGroupRefs(filter)
   serverRefs = ss.findServerRefs(filter2)

   for serverRef in serverRefs:
		ss.addDeviceGroups(serverRef,deviceGroup_refs)
   
		


if __name__ == "__main__":
    main(sys.argv[1: ])
			