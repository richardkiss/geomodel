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

"""Defines some useful geo types such as points and boxes."""

__author__ = 'api.roman.public@gmail.com (Roman Nurik)'


class Point(object):
  """A two-dimensional point in the [-90,90] x [-180,180] latitude/longitude
  space.
  
  Attributes:
    lat: A float in the range [-90,90] indicating the point's latitude.
    lon: A float in the range [-180,180] indicating the point's longitude.
  """
  
  lat = None
  lon = None
  
  def __init__(self, lat, lon):
    """Initializes a point with the given latitude and longitude."""
    if -90 > lat or lat > 90:
      raise ValueError("Latitude must be in [-90, 90] but was %f" % lat)
    if -180 > lon or lon > 180:
      raise ValueError("Longitude must be in [-180, 180] but was %f" % lon)
      
    self.lat = lat
    self.lon = lon
  
  def __str__(self):
    return '(%f, %f)' % (self.lat, self.lon)


class Box(object):
  """A two-dimensional rectangular region defined by Northeast and Southwest
  points.
  
  Attributes:
    north_east: A read-only geotypes.Point indicating the box's Northeast
        coordinate.
    south_west: A read-only geotypes.Point indicating the box's Southwest
        coordinate.
    north: A float indicating the box's North latitude.
    east: A float indicating the box's East longitude.
    south: A float indicating the box's South latitude.
    west: A float indicating the box's West longitude.
  """
  
  _ne = None
  _sw = None
  
  def __init__(self, north, east, south, west):
    # TODO(romannurik): swap south/north if necessary
    # TODO(romannurik): port geojs LatLonBox here
    self._ne = Point(north, east)
    self._sw = Point(south, west)
  
  north_east = property(lambda self: self._ne)
  south_west = property(lambda self: self._sw)
  
  def _set_north(self, val):
    self._ne.lat = val
  north = property(lambda self: self._ne.lat, _set_north)
  
  def _set_east(self, val):
    self._ne.lat = val
  east  = property(lambda self: self._ne.lon, _set_east)
  
  def _set_south(self, val):
    self._sw.lat = val
  south = property(lambda self: self._sw.lat, _set_south)
  
  def _set_west(self, val):
    self._sw.lon = val
  west  = property(lambda self: self._sw.lon, _set_west)
  
  def __str__(self):
    return '(N:%f, E:%f, S:%f, W:%f)' % (self.north, self.east,
                                         self.south, self.west)