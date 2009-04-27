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

"""Defines common geo math functions used throughout the library."""

import math

RADIUS = 6378135


def distance(p1, p2):
  """Calculates the great circle distance between two points using the
  law of cosines formula.
  
  Args:
    p1: A geotypes.Point or db.GeoPt indicating the first point.
    p2: A geotypes.Point or db.GeoPt indicating the second point.
  
  Returns:
    The 2D great-circle distance between the two given points, in meters.
  """
  p1lat, p1lon = math.radians(p1.lat), math.radians(p1.lon)
  p2lat, p2lon = math.radians(p2.lat), math.radians(p2.lon)
  return RADIUS * math.acos(math.sin(p1lat) * math.sin(p2lat) +
      math.cos(p1lat) * math.cos(p2lat) * math.cos(p2lon - p1lon))


def destination(p, heading, distance):
  """Approximates a destination point given a start point, an initial bearing,
  and a distance.
  
  Args:
    p: A geotypes.Point or db.GeoPt indicating the start point.
    heading: The initial bearing to follow, in degrees.
    distance: The distance to travel, in meters.
  
  Returns:
    A geotypes.Point approximately <distance> away from the starting point
    if following an initial bearing of <heading>.
  """
  plat = math.radians(p.lat)
  plon = math.radians(p.lon)
  
  angular_distance = distance * 1.0 / RADIUS
  heading = math.radians(heading)
  lat2 = math.asin(math.sin(plat) * math.cos(angular_distance) + 
                   math.cos(plat) * math.sin(angular_distance) *
                     math.cos(heading))
  
  return geotypes.Point(
      math.degrees(lat2),
      math.degrees(math.atan2(
          math.sin(heading) * math.sin(angular_distance) * math.cos(lat2),
          math.cos(angular_distance) - math.sin(plat) * math.sin(lat2))) + plon)