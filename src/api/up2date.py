## up2date.py
""" up2date API for implementing the server side of up2date.

Copyright (c) 2001 Hunter Matthews    Distributed under GPL.

Note: The actual up2date client makes some 'registration' calls as well.

For details on the exact API, what each method expects and what it 
returns, please see the rhn_api.txt file.
"""

import copy
import os
import pprint
import rpm
import xmlrpclib
import stat
import string
import sys

import misc
import db
import configure
import auth
from logger import *

__current_api__ = [
    'login',                               ## These are the newer 2.7 API
    'listChannels',
    'solveDependencies',
    ]


def login(sysid_string):

    logfunc(locals())

    # Authorize the client
    si = auth.SysId(sysid_string)   
    (valid, reason) = si.isValid()
    if not valid:
        return xmlrpclib.Fault(1000, reason)

    # Setup the basic SysHeaders stuff
    hi = auth.SysHeaders()
    hi.loadSysId(si)
    hi.setTimeValues()
    
    # Need a list of channels this client is authorized for 
    # FIXME: we assume only one channel right now is returned...
    channels = db.db.getCompatibleChannels(si.getattr('architecture'), 
                                                  si.getattr('os_release'))    
    if len(channels) == 0:
        log("Fault! - no channels")
        return xmlrpclib.Fault(1000, 
            "No compatible channels found for client")

    # This is mostly here as a marker - we'd pass in a list of all possible
    #   (compatible) channels, and get back a list (pos. empty) of the ones
    #   this client was authorized to to touch.
    channels = auth.authorize.getAuthorizedChannels(si, channels)
    if len(channels) == 0:
        log ("Fault! - not authorized for channels")
        return xmlrpclib.Fault(1000, 
            "Client is not authorized for any channels")

    # Actually append that information to our headerId
    for chan in channels:
        hi.addAuthChannel(chan)

    hi.setChecksum()            
    return hi.dumpLoginInfo()
    

def listChannels(sysid_string):
    """ Send a list of all compatible channels back to client. """

    logfunc(locals())

    # Authorize the client
    si = auth.SysId(sysid_string)   
    (valid, reason) = si.isValid()
    if not valid:
        return xmlrpclib.Fault(1000, reason)

    # Need a list of channels this client is authorized for 
    # FIXME: we assume only one channel right now is returned...
    channels = db.db.getCompatibleChannels(si.getattr('architecture'),
                                                  si.getattr('os_release'))
    if len(channels) == 0:
        return xmlrpclib.Fault(1000, 
            "No compatible channels found for client")

    # This is mostly here as a marker - we'd pass in a list of all possible
    #   (compatible) channels, and get back a list (pos. empty) of the ones
    #   this client was authorized to to touch.
    channels = auth.authorize.getAuthorizedChannels(si, channels)
    if len(channels) == 0:
        return xmlrpclib.Fault(1000, 
            "Client is not authorized for any channels")

    # Must not alter the in-memory copy - we need a temp form
    result = copy.deepcopy(channels)

    # Transfer chanInfo structure into API result
    for chan in result:
        for key in chan.keys():
            if key not in ('name', 'parent_channel', 'label', 'arch', 'description'):
                del chan[key]

    return result

        
def solveDependencies(sysid_string, unknowns):
    """ Find all the packages needed to 'provide' these unknown dependancies.

    """

    logfunc({'unknowns': unknowns})    ## cheat: sysid is boring

    # Authorize the client
    si = auth.SysId(sysid_string)   
    (valid, reason) = si.isValid()
    if not valid:
        return xmlrpclib.Fault(1000, reason)

    channels = db.db.getCompatibleChannels(si.getattr('architecture'),
                                           si.getattr('os_release'))
    if len(channels) == 0:
        return xmlrpclib.Fault(1000, 
            "No compatible channels found for client")

    provides = {}
    for unk in unknowns:
        # according to up2date 2.7.11, pkg could be _plural_, and right now
        # it sucks off the first one returned.
        pkgs = db.db.solveDependancy(channels[0]['label'], 
                                     si.getattr('architecture'),
                                     unk)

        # packagedb.solveDep will return None if our db can't solve that
        # in which case, we return an empty list for that unk, which is what
        # the client expects.
        provides[unk] = []

        if pkgs:
            for pkg in pkgs:
                provides[unk].append(pkg[0:4])

    return provides


## END OF LINE ##    
