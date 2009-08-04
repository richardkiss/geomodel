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

"""location_geocell_n --> location_geocells Migration script

Migrates old-style multiple StringProperty GeoModel-based entities to
new-style single StringListProperty entities using the remote API.
"""

__author__ = 'api.roman.public@gmail.com (Roman Nurik)'

import sys

import remote_client

import mapper

sys.path.append('../..')
import models


class LocationGeocellMigration(mapper.Mapper):
  """location_geocell property migration using mapper framework."""
  KIND = models.PublicSchool

  def map(self, entity):
    dirty = False
    for f in range(1, 14):
      if getattr(entity, 'location_geocell_%d' % f):
        dirty = True
        setattr(entity, 'location_geocell_%d' % f, None)
    
    if dirty:
      entity.update_location()
      return ([entity], [])
    else:
      return ([], [])


if __name__ == '__main__':
  LocationGeocellMigration().run(batch_size=100)
