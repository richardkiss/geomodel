#!/usr/bin/python2.5
#
# Copyright 2009 Roman Nurik
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Bulk uploader for PublicSchool entities, for use with appcfg.py upload_data.

Expected CSV format is http://nces.ed.gov/ccd/psadd.asp, augmented with 3
extra columns for latitude, longitude, and accuracy value (0-9, per
http://code.google.com/apis/maps/documentation/geocoding/#GeocodingAccuracy).

A batch geocoder must be used to augment the CSV with lat/lon data.
"""

__author__ = 'api.roman.public@gmail.com (Roman Nurik)'


import datetime
import os
import sys

from google.appengine.ext import db
from google.appengine.tools.bulkloader import Loader

sys.path.append('../..')
import models


class PublicSchoolLoader(Loader):
  def __init__(self):
    fail_vals = ['M', 'N', '-1', '-2']
    grade_level_fail_vals = fail_vals + ['UG', '00']
    
    def unicode_str(s):
      return s.decode('utf8', 'ignore')
    
    def ccd_str(s):
      if s in fail_vals:
        return None
      
      return unicode_str(s)
    
    def ccd_int(s):
      if s in fail_vals:
        return None
      
      return int(s)
    
    def lat_lon(s):
      lat, lon = [float(v) for v in s.split(',')]
      return db.GeoPt(lat, lon)
    
    def grade_range(s):
      def _grade_level(v):
        if v == 'PK':
          return -1
        elif v == 'KG':
          return 0
        elif v in grade_level_fail_vals:
          return None

        return int(v)
      
      lo, hi = [_grade_level(v) for v in s.split(',')]
      return range(lo, hi + 1) if lo is not None and hi is not None else []
    
    dummy = lambda x: None
    
    Loader.__init__(self, 'PublicSchool',
                    [('school_id', unicode_str),
                     ('name', unicode_str),
                     ('address', ccd_str),
                     ('city', ccd_str),
                     ('state', ccd_str),
                     ('zip_code', ccd_int),
                     ('_dummy', dummy), # skip zip+4
                     ('enrollment', ccd_int),
                     ('phone_number', ccd_str),
                     ('locale_code', ccd_int),
                     ('school_type', ccd_int),
                     ('school_level', ccd_int),
                     ('grades_taught', grade_range), # set grade levels
                     ('_dummy', dummy), # skip highest_grade_level
                     ('location', lat_lon), # set lat and lon
                     ('_dummy', dummy), # skip longitude
                     ('_dummy', dummy), # skip accuracy
                     ])

  def create_entity(self, values, key_name=None, parent=None):
    # Set the 13th column as the 13th,14th column (lowest/highest grade)
    # so that we can set one property (grades_taught:ListProperty) from two
    # CSV columns.
    values[12] = values[12] + ',' + values[13]
    
    # Set the 15th column as the 15th,16th column (lat/lon)
    # so that we can set one property (location:GeoPt) from two
    # CSV columns.
    values[14] = values[14] + ',' + values[15]
    
    return super(PublicSchoolLoader, self).create_entity(values, key_name)

  def handle_entity(self, entity):
    entity.update_location()
    return entity


loaders = [PublicSchoolLoader]
