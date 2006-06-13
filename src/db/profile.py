#!/usr/bin/python
#
# profile.py - Client profile interface
#
# Copyright 2005 Jack Neely <jjneely@gmail.com>
#
# SDG
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from exception import *
import db
from db.resultSet import resultSet

class CurrentProfileDB(CurrentDB):
    pass

class ProfileDB(object):

    def __init__(self):
        self.cursor = db.sdb.getCursor()
        self.conn   = db.sdb.getConnection()


    def addProfile(self, arch, os_release, name, release_name, uuid):
        q = """insert into PROFILE (profile_id, architecture, 
               os_release, name,
               release_name, uuid) values
               (NULL, %s, %s, %s, %s, %s)"""
               
        t = (arch, os_release, name, release_name, uuid)

        self.cursor.execute(q, t)
        self.conn.commit()

        return self.getProfileID(uuid)


    def getProfileID(self, uuid):
        q = "select profile_id from PROFILE where uuid = %s"
        self.cursor.execute(q, (uuid,))
        
        return resultSet(self.cursor)['profile_id']
    
    def getProfile(self, id):
        q = """select architecture, os_release, name, release_name, uuid
               from PROFILE where profile_id = %s"""

        self.cursor.execute(q, (id,))
        r = self.cursor.fetchone()
        
        # if r is None that's what we want
        return r

