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

"""Defines the notion of `geocells' and exposes methods to operate on them.

A geocell is a hexadecimal string that defines a two dimensional rectangular
region inside the [-90,90] x [-180,180] latitude/longitude space. A geocell's
`resolution' is its length. For most practical purposes, at high resolutions,
geocells can be treated as single points.

Much like geohashes (see http://en.wikipedia.org/wiki/Geohash), geocells are
hierarchical, in that any prefix of a geocell is considered its ancestor, with
geocell[:-1] being geocell's immediate parent cell.

To calculate the rectangle of a given geocell string, first divide the
[-90,90] x [-180,180] latitude/longitude space evenly into a 4x4 grid like so:

             +---+---+---+---+ (90, 180)
             | a | b | e | f |
             +---+---+---+---+
             | 8 | 9 | c | d |
             +---+---+---+---+
             | 2 | 3 | 6 | 7 |
             +---+---+---+---+
             | 0 | 1 | 4 | 5 |
  (-90,-180) +---+---+---+---+

NOTE: The point (0, 0) is at the intersection of grid cells 3, 6, 9 and c. And,
      for example, cell 7 should be the sub-rectangle from
      (-45, 90) to (0, 180).

Calculate the sub-rectangle for the first character of the geocell string and
re-divide this sub-rectangle into another 4x4 grid. For example, if the geocell
string is `78a', we will re-divide the sub-rectangle like so:

               .                   .
               .                   .
           . . +----+----+----+----+ (0, 180)
               | 7a | 7b | 7e | 7f |
               +----+----+----+----+
               | 78 | 79 | 7c | 7d |
               +----+----+----+----+
               | 72 | 73 | 76 | 77 |
               +----+----+----+----+
               | 70 | 71 | 74 | 75 |
  . . (-45,90) +----+----+----+----+
               .                   .
               .                   .

Continue to re-divide into sub-rectangles and 4x4 grids until the entire
geocell string has been exhausted. The final sub-rectangle is the rectangular
region for the geocell.

TODO(romannurik): Unit tests!
"""

__author__ = 'api.roman.public@gmail.com (Roman Nurik)'

import os.path
import sys
import geotypes
import geomath

MAX_GEOCELL_RESOLUTION = 13  # The maximum *practical* geocell resolution.
GEOCELL_GRID_SIZE = 4
GEOCELL_ALPHABET = '0123456789abcdef'

#def _best_radius_search_cells(center, distance, cost_function):
#  n = geomath.destination(center, 0, distance).lat
#  e = geomath.destination(center, 90, distance).lon
#  s = geomath.destination(center, 180, distance).lat
#  w = geomath.destination(center, 270, distance).lon
#  
#  n, s = max(n, s), min(n, s)
#  e, w = max(e, w), min(e, w)
#  
#  return best_bbox_search_cells((n, e, s, w), cost_function)

def best_bbox_search_cells(bbox, cost_function):
  """Returns the most efficient set of geocells to search in a bounding box
  query, given a cost function.
  
  This method is guaranteed to return a set of geocells having the same
  resolution.
  
  Args:
    bbox: A geotypes.Box indicating the bounding box being searched.
    cost_function: A function that accepts two arguments:
        * num_cells: the number of cells to search
        * resolution: the resolution of each cell to search
        and returns the `cost' of querying against this number of cells
        at the given resolution.
  
  Returns:
    A list of geocell strings that contain the given box.
  """
  cell_ne = compute(bbox.north_east, resolution=MAX_GEOCELL_RESOLUTION)
  cell_sw = compute(bbox.south_west, resolution=MAX_GEOCELL_RESOLUTION)
  
  min_cost = 1e10000  # Practical infinity.
  min_cost_cell_set = None
  
  # First find the common prefix, if there is one.. this will be the base
  # resolution.. i.e. we don't have to look at any higher resolution cells.
  min_resolution = len(os.path.commonprefix([cell_sw, cell_ne]))
  
  # Iteravely calculate all possible sets of cells that wholely contain
  # the requested bounding box.
  for cur_resolution in range(min_resolution, MAX_GEOCELL_RESOLUTION + 1):
    cur_ne = cell_ne[:cur_resolution]
    cur_sw = cell_sw[:cur_resolution]
    
    num_cells = interpolation_count(cur_ne, cur_sw)
    if num_cells > 300:
      continue
    
    cell_set = sorted(interpolate(cur_ne, cur_sw))
    simplified_cells = []
    
    '''
    # NOTE: this may be moot
    # try to simplify the geocells by prefix matching
    consecs = {}
    for i in range(1, len(cell_set)):
      cp = commonprefix([cell_set[i], cell_set[i - 1]])
      # increment count for this prefix and all parent prefixes
      for s in range(len(cp)):
        pfx = cp[:s + 1]
        if not pfx in consecs:
          consecs[pfx] = 0
        elif consecs[pfx] < 0: # this prefix is already marked to be collapsed
          continue
        else:
          consecs[pfx] += 1
          if consecs[pfx] >= pow(16, cur_resolution - len(pfx)):
            consecs[pfx] = -1 # mark the prefix to be collapsed
            simplified_cells.append(pfx)
    
    print >> sys.stderr, simplified_cells
    
    for sc in sorted(simplified_cells):
      cell_set = filter(lambda c: not c.startswith(sc), cell_set)
      simplified_cells = filter(lambda c: c == sc or not c.startswith(sc),
                                simplified_cells)
    cell_set.extend(simplified_cells)
    '''
    
    cost = cost_function(num_cells=len(cell_set), resolution=cur_resolution) 
    
    # TODO(romannurik): See if this resolution is even possible, as in the 
    # future cells at certain resolutions may not be stored.
    if cost <= min_cost:
      min_cost = cost
      min_cost_cell_set = cell_set
      #print >> sys.stderr, 'boxes=%d, cost=%f' % (len(cell_set), cost)
    else:
      # Once the cost starts rising, we won't be able to do better, so abort.
      break
  
  return min_cost_cell_set


def collinear(cell1, cell2, direction=0):
  """Determines whether the given cells are collinear in the given
  dimension--that is, whether or not they are in the same row (direction=0)
  or in the same column (direction=1).
  
  Args:
    cell1: The first geocell string.
    cell2: The second geocell string.
    direction: An int, where 0 invokes a horizontal collinearity test and 1
        invokes a vertical collinearity test.
  
  Returns:
    A bool indicating whether or not the given cells are collinear in the given
    dimension.
  """
  for i in range(min(len(cell1), len(cell2))):
    x1, y1 = _subdiv_xy(cell1[i])
    x2, y2 = _subdiv_xy(cell2[i])
    
    # Check horizontal collinearity (assure y's are always the same).
    if direction == 0 and y1 != y2:
      return False
    
    # Check vertical collinearity (assure x's are always the same).
    if direction == 1 and x1 != x2:
      return False
  
  return True


def interpolate(cell_ne, cell_sw):
  """Generates the set of cells in the grid created by interpolating from the
  given Northeast geocell to the given Southwest geocell.
  
  Assumes the Northeast geocell is actually Northeast of Southwest geocell.
  
  Arguments:
    cell_ne: The Northeast geocell string.
    cell_sw: The Southwest geocell string.
  
  Returns:
    A list of geocell strings in the interpolation.
  """
  # 2D array, will later be flattened.
  cell_set = [[cell_sw]]
  
  # First get adjacent geocells across until Southeast--collinearity with
  # Northeast in vertical direction (0) means we're at Southeast.
  while not collinear(cell_set[0][-1], cell_ne, 1):
    cell_tmp = adjacent(cell_set[0][-1], (1, 0))
    if cell_tmp is None:
      break
    cell_set[0].append(cell_tmp)
  
  # Then get adjacent geocells upwards.
  while cell_set[-1][-1] != cell_ne:
    cell_tmp_row = [adjacent(g, (0, 1)) for g in cell_set[-1]]
    if cell_tmp_row[0] is None:
      break
    cell_set.append(cell_tmp_row)
  
  # Flatten cell_set, since it's currently a 2D array.
  cell_set = [g for inner in cell_set for g in inner]
  return cell_set


def interpolation_count(cell_ne, cell_sw):
  """Computes the number of cells in the grid created by interpolating from the
  given Northeast geocell to the given Southwest geocell.
  
  Assumes the Northeast geocell is actually Northeast of Southwest geocell.
  
  Arguments:
    cell_ne: The Northeast geocell string.
    cell_sw: The Southwest geocell string.
  
  Returns:
    An int, indicating the number of geocells in the interpolation.
  """
  bbox_ne = compute_box(cell_ne)
  bbox_sw = compute_box(cell_sw)
  
  return int(((bbox_ne.east - bbox_sw.west) / (bbox_sw.east - bbox_sw.west)) * \
            ((bbox_ne.north - bbox_sw.south) / (bbox_sw.north - bbox_sw.south)))


def all_adjacents(cell):
  """Calculates all of the given geocell's adjacent geocells, including None
  values where there is no neighboring cell in a possible direction.
  
  Args:
    cell: The geocell string for which to calculate adjacent/neighboring cells.
  
  Returns:
    A list of 8 geocell strings and/or None values indicating adjacent cells.
  """
  return [adjacent(cell, d) for d in [(-1,-1), ( 0,-1), ( 1,-1), (-1, 0),
                                      ( 1, 0), (-1, 1), ( 0, 1), ( 1, 1)]]


def adjacent(cell, dir):
  """Calculates the geocell adjacent to the given cell in the given direction.
  
  Args:
    cell: The geocell string whose neighbor is being calculated.
    dir: A (x, y) tuple indicating direction, where x and y can be -1, 0, or 1.
        -1 corresponds to West for x and South for y, and
         1 corresponds to East for x and North for y.
  
  Returns:
    The geocell adjacent to the given cell in the given direction, or None if
    there is no such cell.
  """
  if cell is None:
    return None
  
  dx = dir[0]
  dy = dir[1]
  
  cell_adj_arr = list(cell)  # Split the geocell string characters into a list.
  i = len(cell_adj_arr) - 1
  
  while i >= 0 and (dx != 0 or dy != 0):
    x, y = _subdiv_xy(cell_adj_arr[i])
    
    # Horizontal adjacency.
    if dx == -1:  # Asking for left.
      if x == 0:  # At left of parent cell.
        x = GEOCELL_GRID_SIZE - 1  # Becomes right edge of adjacent parent.
      else:
        x -= 1  # Adjacent, same parent.
        dx = 0  # Done with x.
    elif dx == 1:  # Asking for right.
      if x == GEOCELL_GRID_SIZE - 1:  # At right of parent cell.
        x = 0  # Becomes left edge of adjacent parent.
      else:
        x += 1  # Adjacent, same parent.
        dx = 0  # Done with x.
    
    # Vertical adjacency.
    if dy == 1:  # Asking for above.
      if y == GEOCELL_GRID_SIZE - 1:  # At top of parent cell.
        y = 0  # Becomes bottom edge of adjacent parent.
      else:
        y += 1  # Adjacent, same parent.
        dy = 0  # Done with y.
    elif dy == -1:  # Asking for below.
      if y == 0:  # At bottom of parent cell.
        y = GEOCELL_GRID_SIZE - 1  # Becomes top edge of adjacent parent.
      else:
        y -= 1  # Adjacent, same parent.
        dy = 0  # Done with y.
    
    cell_adj_arr[i] = _subdiv_char((x,y))
    i -= 1
  
  # If we're not done with y then it's trying to wrap vertically,
  # which is a failure.
  if dy != 0:
    return None
  
  # At this point, horizontal wrapping is done inherently.
  return ''.join(cell_adj_arr)


def contains_point(cell, point):
  """Returns whether or not the given cell contains the given point."""
  return compute(point, len(cell)) == cell


def point_distance(cell, point):
  """Returns the shortest great circle distance from a given point to the given
  geocell's rectangle.

  If the point is inside the cell, the shortest distance is always to a `edge'
  of the cell rectangle. If the point is outside the cell, the shortest distance
  will be to either a `edge' or `corner' of the cell rectangle.

  Returns:
    The shortest distance from the point to the geocell's rectangle, in meters.
  """
  bbox = compute_box(cell)
  
  between_w_e = bbox.west <= point.lon and point.lon <= bbox.east
  between_n_s = bbox.south <= point.lat and point.lat <= bbox.north
  
  if between_w_e:
    if between_n_s:
      # Inside the geocell.
      return min(geomath.distance(point, (bbox.south, point.lon)),
                 geomath.distance(point, (bbox.north, point.lon)),
                 geomath.distance(point, (point.lat, bbox.east)),
                 geomath.distance(point, (point.lat, bbox.west)))
    else:
      return min(geomath.distance(point, (bbox.south, point.lon)),
                 geomath.distance(point, (bbox.north, point.lon)))
  else:
    if between_n_s:
      return min(geomath.distance(point, (point.lat, bbox.east)),
                 geomath.distance(point, (point.lat, bbox.west)))
    else:
      # TODO(romannurik): optimize
      return min(geomath.distance(point, (bbox.south, bbox.east)),
                 geomath.distance(point, (bbox.north, bbox.east)),
                 geomath.distance(point, (bbox.south, bbox.west)),
                 geomath.distance(point, (bbox.north, bbox.west)))


def compute(point, resolution=MAX_GEOCELL_RESOLUTION):
  """Computes the geocell string containing the given point to the given
  resolution.
  
  This is a simple 16-tree lookup to an arbitrary depth (resolution).
  
  Args:
    point: The geotypes.Point to compute the cell for.
    resolution: An int indicating the resolution of the cell to compute.
  
  Returns:
    The geocell string containing the given point, of length <resolution>.
  """
  north = 90.0
  south = -90.0
  east = 180.0
  west = -180.0
  
  cell = ''
  while len(cell) < resolution:
    subcell_lon_span = (east - west) / GEOCELL_GRID_SIZE
    subcell_lat_span = (north - south) / GEOCELL_GRID_SIZE
    
    x = min(int(GEOCELL_GRID_SIZE * (point.lon - west) / (east - west)),
            GEOCELL_GRID_SIZE - 1)
    y = min(int(GEOCELL_GRID_SIZE * (point.lat - south) / (north - south)),
            GEOCELL_GRID_SIZE - 1)
    
    cell += _subdiv_char((x,y))
    
    south += subcell_lat_span * y
    north = south + subcell_lat_span
    
    west += subcell_lon_span * x
    east = west + subcell_lon_span
  
  return cell


def compute_box(cell):
  """Computes the rectangular boundaries (bounding box) of the given geocell.
  
  Args:
    cell: The geocell string whose boundaries are to be computed.
  
  Returns:
    A geotypes.Box corresponding to the rectangular boundaries of the geocell.
  """
  if cell is None:
    return None

  bbox = geotypes.Box(90.0, 180.0, -90.0, -180.0)
  
  while len(cell) > 0:
    subcell_lon_span = (bbox.east - bbox.west) / GEOCELL_GRID_SIZE
    subcell_lat_span = (bbox.north - bbox.south) / GEOCELL_GRID_SIZE
    
    x, y = _subdiv_xy(cell[0])
    
    bbox = geotypes.Box(bbox.south + subcell_lat_span * (y + 1),
                        bbox.west  + subcell_lon_span * (x + 1),
                        bbox.south + subcell_lat_span * y,
                        bbox.west  + subcell_lon_span * x)
    
    cell = cell[1:]
  
  return bbox


def is_valid(cell):
  """Returns whether or not the given geocell string defines a valid geocell."""
  return bool(cell and reduce(lambda val, c: val and c in GEOCELL_ALPHABET,
                              cell, True))


def children(cell):
  """Calculates the immediate children of the given geocell.
  
  For example, the immediate children of `a' are `a0', `a1', ..., `af'.
  """
  return [cell + chr for chr in GEOCELL_ALPHABET]


def _subdiv_xy(c):
  """Returns the (x, y) position of the given geocell character
  in the 4x4 alphabet grid."""
  # NOTE: This only works for grid size 4.
  c = GEOCELL_ALPHABET.index(c)
  return ((c & 4) >> 1 | (c & 1) >> 0,
          (c & 8) >> 2 | (c & 2) >> 1)


def _subdiv_char(pos):
  """Returns the geocell character in the 4x4 alphabet grid at pos. (x, y)."""
  # NOTE: This only works for grid size 4.
  return GEOCELL_ALPHABET[
      (pos[1] & 2) << 2 |
      (pos[0] & 2) << 1 |
      (pos[1] & 1) << 1 |
      (pos[0] & 1) << 0]


if __name__ == '__main__':
  pass