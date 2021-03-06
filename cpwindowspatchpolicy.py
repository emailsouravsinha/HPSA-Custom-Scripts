#!/opt/opsware/bin/python2
#
# Tue Apr 16 13:17:46 UTC 2013 Gary Des Roches First version with copy, list, compare working
# Thu Apr  4 20:35:06 UTC 2013 Gary Des Roches
#
# Copies all the patches from one patch policy to another patch policy.
#
# This version is pre-Beta
#
# This version of the program is hard coded to only copy from and to a specific pair of patch policies
 
 
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
 
 
patchpolicyreflist = []
thepatchlist = []
patchpolicies = {}
refpatchpoliciesIDandName = {}
 
# A description of what is in patchpolicies:
# patchpolicies[patchpolicyref.id] = {'patchpolicyname': patchpolicyref.name,
#                                     'patchesinpolicy': thepatchlist,
#                                     'patchpolicyref': patchpolicyref }
#
# commandlineuserinput = {'frompatchpolicy': '','topatachpolicy': ''}
 
# Construct a search filter
filter = Filter()
 
# Create a return for a PatchReference
patchreference = []
infosearchitems = {}
userinput = {}
 
# Create a TwistServer object
ts = twistserver.TwistServer()
 
# Set up some twistserver references
folderservice = ts.folder.FolderService
hypervisorservice = ts.virtualization.HypervisorService
patchpolicyservice = ts.swmgmt.PatchPolicyService
platformservice = ts.device.PlatformService
patchpolicyref = ts.swmgmt.PatchPolicyRef
patchservice = ts.swmgmt.PatchService
serverservice = ts.server.ServerService
swpolicyservice = ts.swmgmt.SoftwarePolicyService
unitservice = ts.pkg.UnitService
winpatchservice = ts.swmgmt.WindowsPatchPolicyService
windowspatchpolicyservice = ts.swmgmt.WindowsPatchPolicyService
winpatchpolicyref = ts.swmgmt.WindowsPatchPolicyRef
winswmgmt = ts.swmgmt
 
 
def get_commandline_args():
  # Gets the details the user is looking for
 
   try:
     opts, args = getopt.getopt(sys.argv[1:], 'hvf:st:cl', ['list', 'fromname=', 'fromid=', 'toname=', 'toid='])
   except getopt.GetoptError:
     usage()
     sys.exit(1)
 
   if len(sys.argv) < 2:
     usage()
     sys.exit(1)
 
   # Preset the variables
   frompatchpolicyid = frompatchpolicyname = topatchpolicyid = topatchpolicyname = ''
   compareflag = verboseflag = listflag = silentflag = False
 
   for opt, arg in opts:
     if opt in ("-h", "--help"):
       usage()
       sys.exit(1) # I'm using exit 1 for help
     elif opt in ('-v', '-V'):
       verboseflag = True
 
     elif opt in ('-l', '-L', '--list'):
       listflag = True
     elif opt in ('-f', '-F', '--fromid'):
       frompatchpolicyid = arg
     elif opt in ('--fromname'):
       frompatchpolicyname = arg
     elif opt in ('-t', '-T', '--toid'):
       topatchpolicyid = arg
     elif opt in ('--toname'):
       topatchpolicyname = arg
     elif opt in ('-c', '-C'):
       compareflag = True
     elif opt in ('-s', '-S'):
       silentflag = True
 
   commandlineuserinput = { 'FromPatchPolicyID': frompatchpolicyid, 'FromPatchPolicyName': frompatchpolicyname, 'ToPatchPolicyID': topatchpolicyid, 'ToPatchPolicyName': topatchpolicyname, 'Compare': compareflag, 'List': listflag, 'VerboseFlag': verboseflag, 'SilentFlag': silentflag }
   return commandlineuserinput
 
 
def usage():
  # Prints out help so the user knows what the options are
 
   usage = """
Usage:
 
   -h --help             Prints this
 
   Arguments:
   -f, --fromid          use with a from patch policy id
   --fromname            use with a from patch policy name
   -t, --toid            use with a to patch policy id
   --toname              use with a to patch policy name
   -l                    list the patches in a patch policy
   -c                    compare two patch policies, -f and -t options required
   -s                    silent headers; don't print headers
   -v                    verbose, print out more details
   """
 
   print usage
 
 
def getrefallpatchpolicies():
  # Gets the patch policy references to all Windows patch policies
 
  # refallpatchpolicies = {}  # Didn't use this; delete?
 
  # Get all the WindowsPatchPolicyRefs
  filter.expression = ''  # Gets all of them.  Could add a filter pattern here
  winpatchpolicyrefs = winpatchservice.findWindowsPatchPolicyRefs(filter)
 
  # From all the WindowsPatchPolicyRefs get the patchpolicies
  for winpatchpolicyref in winpatchpolicyrefs:
    try:
      filter.expression = 'PatchPolicyVO.pK EQUAL_TO "%s"' % winpatchpolicyref.id
      patchpolicyrefs = patchpolicyservice.findPatchPolicyRefs(filter)
 
      for patchpolicyref in patchpolicyrefs:
        patchpolicyreflist.append(patchpolicyref)
 
    except:
      print >> sys.stderr, '  *** Something wrong trying to get the windows patch policies ***'
 
  return patchpolicyreflist
 
def fromnameAndID(refallpatchpolicieslist, commandlineuserinput):
  # If a patch policy ID was given return the patch policy name
  # May need to rename this because it doesn't get the ID from a name, or fix it so it will
 
  # commandlineuserinput = { 'FromPatchPolicyID': frompatchpolicyid, 'FromPatchPolicyName': frompatchpolicyname, 'ToPatchPolicyID': topatchpolicyid, 'ToPatchPolicyName': topatchpolicyname, 'Compare': compare, 'VerboseFlag': verboseflag }
 
  # First need to decide if they gave me a name or ID
 
  # A couple of lines I'm going to need to figure out it matches
  if commandlineuserinput['FromPatchPolicyID']:
    try:
      # Get the matching Name
      for apatchpolicyref in refallpatchpolicieslist:
        # print 'Checking id %s against id %s', commandlineuserinput['FromPatchPolicyID'], apatchpolicyref.id
        if commandlineuserinput['FromPatchPolicyID'] == str(apatchpolicyref.id):
          commandlineuserinput['FromPatchPolicyName'] = apatchpolicyref.name
    except:
      print >> sys.stderr, '  *** Could not find a patchpolicy by the number "%s" ***' % commandlineuserinput['FromPatchPolicyID']
      traceback.print_exc()
 
  return commandlineuserinput
 
 
def  getwinpatchpolicyrefs(findrefslike):
   # Given a Windows patch policy name return the information in patchpolicies{}:
   #   'patchpolicyname'
   #   'patchesinpolicy'
   #   'patchpolicyref'
 
   # filter.expression = findrefslike
   filter.expression = ''  # Gets all of them.  Could add a filter pattern here
   winpatchpolicyrefs = winpatchservice.findWindowsPatchPolicyRefs(filter)
 
   print '\n\nWindows patch policy references:'
   for winpatchpolicyref in winpatchpolicyrefs:
     try:
       if re.match(findrefslike, winpatchpolicyref.name):
         try:
           winpatchpolicyvo = winpatchservice.getWindowsPatchPolicyVO(winpatchpolicyref)
         except:
           print >> sys.stderr, '  *** Something wrong trying to get the windows patch policy VOs ***'
 
         try:
           filter.expression = 'PatchPolicyVO.pK EQUAL_TO "%s"' % winpatchpolicyref.id
           patchpolicyrefs = patchpolicyservice.findPatchPolicyRefs(filter)
 
           for patchpolicyref in patchpolicyrefs:
             patchpolicyreflist.append(patchpolicyref)
 
             # Get the patches in the policy
             patchlist = patchpolicyservice.getPatches(patchpolicyreflist)
             for thepatch in patchlist:
               thepatchlist.append(thepatch)
 
             # Put all the information into the dictionary
             patchpolicies[patchpolicyref.id] = {'patchpolicyname': patchpolicyref.name, 'patchesinpolicy': thepatchlist, 'patchpolicyref': patchpolicyref }
 
         except:
           traceback.print_exc()
           print >> sys.stderr, '  *** Something wrong trying to get findPatchPolicyRefs to work ***'
     except:
       print >> sys.stderr, "\n*** Some kind of problem with wppvo or bad variable attempt ***\n\n"
 
def printpatchpolicyinformation(refallpatchpolicieslist):
  eachpatch = ''
  # Print the patch ID and name for each patch policy in patchpolicies{}
  # I don't see why I passed refallpatchpolicieslist to this routine
 
  for thepatchid in patchpolicies:
    print '\nThe patch policy ID: ', thepatchid, ' the patch name: ', patchpolicies[thepatchid]['patchpolicyname']
    for eachpatch in patchpolicies[thepatchid]['patchesinpolicy']:
      print eachpatch.id, ' ', eachpatch.name
    print
 
def printrefallpatchpolicieslist (refallpatchpolicieslist):
  # Print all the policies with patch policy ID and name
 
  print 'ID\t\tName'
  for apatchpolicy in refallpatchpolicieslist:
    print apatchpolicy.id, '\t', apatchpolicy.name
 
def patchpolicieslistIDandNameDict (refallpatchpolicieslist):
  # For every patch policy in refallpatchpolicieslist return the patch policy name and numeric ID
 
  for refpatchpolicy in refallpatchpolicieslist:
    theid = str(refpatchpolicy.id)
    thename = refpatchpolicy.name
    refpatchpoliciesIDandName[theid] = thename
 
  return refpatchpoliciesIDandName
 
def validFromandTo(commandlineuserinput):
  # Finds out if the information for both the "from" and "to" IDs and names are valid
 
  FromPatchPolicyIDFlag = False
  FromPatchPolicyNameFlag = False
  FromPatchPolicyNameMatchesIDFlag = False
 
  ToPatchPolicyIDFlag = False
  ToPatchPolicyNameFlag = False
  ToPatchPolicyNameMatchesIDFlag = False
 
  ToAndFromPatchPolicyIDsSame = False
 
  # This program always needs a valid "from policy", so I'm going to make sure it is there.
 
  # Possiblity 1: I got a From ID
  if commandlineuserinput['FromPatchPolicyID']:
    if commandlineuserinput['FromPatchPolicyID'] not in refpatchpoliciesIDandName:
      FromPatchPolicyIDFlag = False
    else:
      # If I didn't get a from name then fill it in
      if not commandlineuserinput['FromPatchPolicyName']:
        commandlineuserinput['FromPatchPolicyName'] = refpatchpoliciesIDandName[commandlineuserinput['FromPatchPolicyID']]
      FromPatchPolicyIDFlag = True
 
  # Possibilyt 2: I got a From name
  if commandlineuserinput['FromPatchPolicyName']:
    for thepatchpolicyid in refpatchpoliciesIDandName:
      if commandlineuserinput['FromPatchPolicyName'] == refpatchpoliciesIDandName[thepatchpolicyid]:
        FromPatchPolicyNameFlag = True
        # Possibility 3: From id and a From name
        if commandlineuserinput['FromPatchPolicyID'] == thepatchpolicyid:
          FromPatchPolicyNameMatchesIDFlag = True
 
  # Possiblity 4: I got a To id
  if commandlineuserinput['ToPatchPolicyID']:
    if commandlineuserinput['ToPatchPolicyID'] not in refpatchpoliciesIDandName:
      ToPatchPolicyIDFlag = False
    else:
      # If I didn't get a from name then fill it in
      if not commandlineuserinput['ToPatchPolicyName']:
        commandlineuserinput['ToPatchPolicyName'] = refpatchpoliciesIDandName[commandlineuserinput['ToPatchPolicyID']]
      ToPatchPolicyIDFlag = True
 
  # 5: I got a To name
  if commandlineuserinput['ToPatchPolicyName']:
    for thepatchpolicyid in refpatchpoliciesIDandName:
      if commandlineuserinput['ToPatchPolicyName'] == refpatchpoliciesIDandName[thepatchpolicyid]:
        ToPatchPolicyNameFlag = True
        # Possibility 6: From id and a From name
        if commandlineuserinput['ToPatchPolicyID'] == thepatchpolicyid:
          ToPatchPolicyNameMatchesIDFlag = True
 
  # 7: Both the from and to IDs are the same
  if commandlineuserinput['FromPatchPolicyID'] == commandlineuserinput['ToPatchPolicyID']:
    ToAndFromPatchPolicyIDsSame = True
 
 
  valid_from_and_to = { 'FromPatchPolicyIDFlag': FromPatchPolicyIDFlag, 'FromPatchPolicyNameFlag': FromPatchPolicyNameFlag, 'FromPatchPolicyNameMatchesIDFlag': FromPatchPolicyNameMatchesIDFlag, 'ToPatchPolicyIDFlag': ToPatchPolicyIDFlag, 'ToPatchPolicyNameFlag': ToPatchPolicyNameFlag, 'ToPatchPolicyNameMatchesIDFlag': ToPatchPolicyNameMatchesIDFlag, 'ToAndFromPatchPolicyIDsSame': ToAndFromPatchPolicyIDsSame }
 
  return valid_from_and_to
 
 
def copypatchesinpolicy(commandlineuserinput, patchpolicyid, thepatchesintheFrompolicy):
  # Wed Apr 10 18:21:05 UTC 2013
  # If I've gotten this far I have the From and To policies and know the
  # list of patches to copy from.
 
  patchreflong = []
  topatchpolicyrefarray = []
  patchreflist = []
 
  if commandlineuserinput['VerboseFlag']:
    print '\nThe "FROM" patch policy will be ID: ', commandlineuserinput['FromPatchPolicyID']
    print '\nThe "TO" patch policy will be ID: ', commandlineuserinput['ToPatchPolicyID']
 
  # Fill a list with long patch IDs
  try:
    # I need the patch policy reference from the patch policy ID
    filter.expression = 'PatchPolicyVO.pK EQUAL_TO "%s"' % commandlineuserinput['ToPatchPolicyID']
    patchpolicyrefs = patchpolicyservice.findPatchPolicyRefs(filter)
 
    for eachpatch in thepatchesintheFrompolicy:
      if not commandlineuserinput['SilentFlag']:
        # print 'Copying patch %s now' % eachpatch.name
        print 'Copying patch %s now' % thepatchesintheFrompolicy[eachpatch]['patchref'].name
 
      patchreflist.append (thepatchesintheFrompolicy[eachpatch]['patchref'])
 
    # print patchreflist
 
    # Adds the whole list of patches
    patchpolicyservice.addPatches( patchpolicyrefs, patchreflist )
 
  except:
    print >> sys.stderr, '*** There was a problem trying to copy the patch ***'
    traceback.print_exc()
 
def copypatchpolicytonew(newpatchpolicyname):
  # The original def I came up with, hard coded from and to to get the patch copy working
 
  topatchpolicyname = ''
  topatchpolicyid = ''
  frompatchpolicyname = ''
  frompatchpolicyid = ''
  thepatch = []
  longtopatchpolicyid = []
  longeachpatchid = []
  topatchpolicyrefarray = []
  eachPatchreference = []
 
  # A statement letting the user what the new name is going to be
  # I'm stubbing in a name here for this test because I
  # don't want to take the time to code how to create a new policy
  newpatchpolicyname = 'gdesrochtestpolicy2'
  print '\nNew patch policy will be named: ', newpatchpolicyname
 
  # Just for now, since I didn't just create the patch policy I need to search for the one that is already there I am using
  for eachpolicyid in patchpolicies:
    if newpatchpolicyname == patchpolicies[eachpolicyid]['patchpolicyname']:
      topatchpolicyname = patchpolicies[eachpolicyid]['patchpolicyname']
      topatchpolicyid = eachpolicyid
      topatchpolicyref = patchpolicies[eachpolicyid]['patchpolicyref']
      topatchpolicyrefarray.append(patchpolicies[eachpolicyid]['patchpolicyref'])
 
    if frompatchpolicyid == eachpolicyid:
      frompatchpolicyname = patchpolicies[eachpolicyid]['patchpolicyname']
      frompatchpolicyid = eachpolicyid
 
  try:
    print 'The from patch policy is: ', frompatchpolicyname, ' with ID: ', frompatchpolicyid
    print 'The to patch policy is: ', topatchpolicyname, ' with ID: ', topatchpolicyid
  except:
    print >> sys.stderr, "*** There is a problem with either the from or to patch policy name ***"
 
  try:
    for eachpatch in patchpolicies[frompatchpolicyid]['patchesinpolicy']:
      print 'Copying patch %s now' % eachpatch.name
      longeachpatchid.append(eachpatch.id)
      eachPatchreference.append(eachpatch)
      # expected com.opsware.pkg.PatchReference[] for argument #1
 
      patchpolicyservice.addPatches( topatchpolicyrefarray, eachPatchreference )
  except:
    print >> sys.stderr, '*** There was a problem trying to copy the patch "%s" ***' % eachpatch.name
 
 
def getpatchpolicyreffromid(refallpatchpolicieslist, patchpolicyid):
  for apatchpolicy in refallpatchpolicieslist:
    if patchpolicyid == str(apatchpolicy.id):
      return apatchpolicy
 
def  getpatchesinpolicybyid(patchpolicyid, refallpatchpolicieslist):
 
  patchesinthepolicy = {}
 
  # Get the patch policy reference to that ID
  patchpolicytolist = getpatchpolicyreffromid(refallpatchpolicieslist, patchpolicyid)
 
  # Set up the filter to get the patch policy ref
  filter.expression = 'PatchPolicyVO.pK EQUAL_TO "%s"' % patchpolicytolist.id
  patchpolicyrefs = patchpolicyservice.findPatchPolicyRefs(filter)
 
  # Go through each patch policy found (there is only one) and get the patches for it
  for patchpolicyref in patchpolicyrefs:
    patchpolicyreflist = [patchpolicyref]
 
    # Get the patches in the policy
    patchlist = patchpolicyservice.getPatches(patchpolicyreflist)
 
  for thepatch in patchlist:
    patchesinthepolicy[thepatch.id] = { 'name': thepatch.name, 'patchpolicyid': patchpolicyid, 'patchref': thepatch }
 
 
  return patchesinthepolicy
 
def getpatchesinfrompolicy(commandlineuserinput, refallpatchpolicieslist):
  patchlist = {}
 
  if not commandlineuserinput['SilentFlag']:
    print '\nPatch Policy Name: ', commandlineuserinput['FromPatchPolicyName']
    print 'Patch Policy ID: ',  commandlineuserinput['FromPatchPolicyID']
    print 'Patch name', '\t', 'Patch ID'
 
  # The ID of the patch From list
  patchpolicyid = commandlineuserinput['FromPatchPolicyID']
 
  thepatchesinthepolicy = getpatchesinpolicybyid(patchpolicyid, refallpatchpolicieslist)
 
  return thepatchesinthepolicy
 
def getpatchesintopolicy(commandlineuserinput, refallpatchpolicieslist):
  patchlist = {}
 
  if not commandlineuserinput['SilentFlag']:
    print '\nPatch Policy Name: ', commandlineuserinput['ToPatchPolicyName']
    print 'Patch Policy ID: ',  commandlineuserinput['ToPatchPolicyID']
    print 'Patch name', '\t', 'Patch ID'
 
  # The ID of the patch to list
  patchpolicyid = commandlineuserinput['ToPatchPolicyID']
 
  thepatchesinthepolicy = getpatchesinpolicybyid(patchpolicyid, refallpatchpolicieslist)
 
  return thepatchesinthepolicy
 
def compares (commandlineuserinput, refallpatchpolicieslist):
  thepatchesintheFrompolicy  = {}
  patchesincommonFrominTo = []
  patchesdifferentFrominTo = []
  patchesincommonToinFrom = []
  patchesdifferentToinFrom = []
 
  # Get the patches in the From list
  patchpolicyid = commandlineuserinput['FromPatchPolicyID']
  thepatchesintheFrompolicy = getpatchesinpolicybyid(patchpolicyid, refallpatchpolicieslist)
 
  # Get the patches in the To list
  patchpolicyid = commandlineuserinput['ToPatchPolicyID']
  thepatchesintheTopolicy = getpatchesinpolicybyid(patchpolicyid, refallpatchpolicieslist)
 
  # Count the number of patches in each list
  lengthofFrom = len (thepatchesintheFrompolicy)
  lengthofTo = len (thepatchesintheTopolicy)
 
  # If there are no patches in either list there is no point in comparing them
  if lengthofFrom == 0 and lengthofTo == 0:
    print '\nBoth patch lists, From and To, are empty'
  else:
    # Here are a series of comparisons between the From and To lists
 
    # COUNTS: Tell the user if the counts of the lists are the same or not
    if lengthofFrom == lengthofTo:
      print '\nThe number of IDs in the From and the To lists are the same: ', lengthofFrom, '\n'
    else:
      print '\nThe number of patches in the From patch policy list: ', lengthofFrom
      print 'The number of patches in the To patch policy list: ', lengthofTo
 
    # Compare lists, From in To and To in From
 
    # Find the list of common and the lists of common and differences, From in To
    for apatch in thepatchesintheFrompolicy:
      if apatch in thepatchesintheTopolicy:
        patchesincommonFrominTo.append(apatch)
      else:
        patchesdifferentFrominTo.append(apatch)
 
    # Find the list of common and the lists of common and differences, To in From
    for apatch in thepatchesintheTopolicy:
      if apatch in thepatchesintheFrompolicy:
        patchesincommonToinFrom.append(apatch)
      else:
        patchesdifferentToinFrom.append(apatch)
 
    print '\nThe number patches in the From set that are also in the To set is: ', len(patchesincommonFrominTo)
    print 'The number of patches in the From set that are not in the To set is: ', len(patchesdifferentFrominTo)
 
    print '\nThe number patches in the To set and also in the From set is: ', len(patchesincommonToinFrom)
    print 'The number of the To set that are not in the From set is: ', len(patchesdifferentToinFrom), '\n'
 
  if commandlineuserinput['VerboseFlag']:
    # patchesinthepolicy[thepatch.id] = { 'name': thepatch.name, 'patchpolicyid': patchpolicyid, 'patchref': thepatch }
    # Figure out the lentgths of the above for all four sets
    lenpatchesFrominTodifferent = len(patchesincommonFrominTo)
    lenpatchesFrominTodifferent = len(patchesdifferentFrominTo)
 
    lenpatchesToinFromdifferent = len(patchesincommonToinFrom)
    lenpatchesToinFromdifferent = len(patchesdifferentToinFrom)
 
    print '\nDetailed comparisons of the From and To patch lists:\n'
    # Print the comparisons of the lists, From in To and To in From
    print '\nList of patch IDs in both the From and the To list: '
    # for eachpatch in patchesincommonFrominTo[:-1]:
    for eachpatch in patchesincommonFrominTo:
      print thepatchesintheFrompolicy[eachpatch]['name']
 
    # New listing
    if len(patchesdifferentFrominTo) > 0:
      print '\nHere is the list of patch IDs in the From missing from the To: '
      for eachpatch in patchesdifferentFrominTo:
        # print '%s,' % eachpatch,
        print thepatchesintheFrompolicy[eachpatch]['name']
      print
    else:
      print '\nAll the patches in the From are also in the To patch set.\n'
 
 
def main():
 
  # Notes and references of variables
  # refpatchpoliciesIDandName = {} # Will contain a list of policy IDs to names
  # commandlineuserinput = { 'FromPatchPolicyID': frompatchpolicyid, 'FromPatchPolicyName': frompatchpolicyname, 'ToPatchPolicyID': topatchpolicyid, 'ToPatchPolicyName': topatchpolicyname, 'Compare': compare, 'VerboseFlag': verboseflag }
  valid_from_and_to = {}
  thepatchesintheFrompolicy  = {}
  patchesincommonFrominTo = []
  patchesdifferentFrominTo = []
  patchesincommonToinFrom = []
  patchesdifferentToinFrom = []
 
 
  # Get the command line args
  commandlineuserinput = get_commandline_args()
 
  # Get the patch policies so we can find out if the user gave existing information accurately
  refallpatchpolicieslist = getrefallpatchpolicies()
 
  # Get the id and policy name into a dictionary
  refpatchpoliciesIDandName = patchpolicieslistIDandNameDict (refallpatchpolicieslist)
 
  # Print out all the patch policy IDs and names (mostly used for debugging to get the policy names and IDs)
  # printrefallpatchpolicieslist (refallpatchpolicieslist)
 
  # Figure out what information the user gave matches the existing patch policy IDs and names
  # It returns seven flags telling which user supplied information matches existing patch policies
 
  valid_from_and_to = validFromandTo(commandlineuserinput)
 
  # Determine which of the three things to do: 1. list, 2. compare, 3. copy
 
  # The 1. list section:
  if commandlineuserinput['List']:
    if valid_from_and_to[ 'FromPatchPolicyIDFlag']:
      thepatchesintheFrompolicy = getpatchesinfrompolicy(commandlineuserinput, refallpatchpolicieslist)
      # Print out the patches
      for thepatch in thepatchesintheFrompolicy:
        print thepatchesintheFrompolicy[thepatch]['name'], '\t', thepatch
    else:
      if not valid_from_and_to[ 'ToPatchPolicyIDFlag']:
        print >> sys.stderr, '*** A patch listing was requested but there is no from patch policy ID "%s" ***' % commandlineuserinput['FromPatchPolicyID']
    if valid_from_and_to[ 'ToPatchPolicyIDFlag']:
      thepatchesintheTopolicy = getpatchesintopolicy(commandlineuserinput, refallpatchpolicieslist)
      # Print out the patches
      for thepatch in thepatchesintheTopolicy:
        print thepatchesintheTopolicy[thepatch]['name'], '\t', thepatch
 
  # The 2. compare two patch policies section:
  if commandlineuserinput['Compare']:
    if valid_from_and_to[ 'FromPatchPolicyIDFlag'] and valid_from_and_to[ 'ToPatchPolicyIDFlag']:
     compares (commandlineuserinput, refallpatchpolicieslist)
    else:
      # Figure out which patch policies are not valid
      # Verify the from patch policy
      if not valid_from_and_to[ 'FromPatchPolicyIDFlag']:
        print >> sys.stderr, '  *** The "FROM" patch policy ID %s is not valid ***' % commandlineuserinput['FromPatchPolicyID']
 
      # Verify the to patch policy
      if not valid_from_and_to [ 'ToPatchPolicyIDFlag']:
        print >> sys.stderr, '  *** The "TO" patch policy ID %s is not valid ***' % commandlineuserinput['ToPatchPolicyID']
 
  # The 3. copy section, the original task:
  #  I'm going to skip the new policy create at first but that needs to be done before the program is complete
  # This is a copy, there is no List or Compare selected, this is the default of the program
  # Make sure it is not a List request
  if not commandlineuserinput['List']:
    # Make sure it is not a Compare
    if not commandlineuserinput['Compare']:
      try:
        # Make sure the place we're copying from and to is there
        if valid_from_and_to[ 'FromPatchPolicyIDFlag'] and valid_from_and_to[ 'ToPatchPolicyIDFlag']:
          if commandlineuserinput['VerboseFlag']:
            print 'I know both policies are there'
          # The ID of the patch From list
          patchpolicyid = commandlineuserinput['FromPatchPolicyID']
          thepatchesintheFrompolicy = getpatchesinpolicybyid(patchpolicyid, refallpatchpolicieslist)
 
          if commandlineuserinput['VerboseFlag']:
            # Print out the patches just to be sure I have them in the copy routine
            print 'This is the "From" policy patch list'
            for thepatch in thepatchesintheFrompolicy:
              print thepatchesintheFrompolicy[thepatch]['name'], '\t', thepatch
 
          # Here is the part that actuall copies the patch list to the new policy
          copypatchesinpolicy(commandlineuserinput, patchpolicyid, thepatchesintheFrompolicy)
        else:
          if not valid_from_and_to['FromPatchPolicyIDFlag'] and not commandlineuserinput['List']:
            print >> sys.stderr, '  *** The "FROM" patch policy ID %s is not valid ***' % commandlineuserinput['FromPatchPolicyID']
          if not valid_from_and_to[ 'ToPatchPolicyIDFlag'] and not commandlineuserinput['List']:
            print >> sys.stderr, '  *** The "TO" patch policy ID %s is not valid ***' % commandlineuserinput['ToPatchPolicyID']
      except:
        print >> sys.stderr, '  *** Trying to copy patches to a new policy error ***'
        traceback.print_exc()
 
 
 
if __name__ == '__main__':
      try:
          main()
      except Exception, e:
          if str(e) != '1' and str(e) != '2':   # Only complain if this is not a help exit
            print "I'm getting a sys.exit error '%s' from main" % str(e)
            traceback.print_exc()
          os._exit(1)
