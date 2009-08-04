#!/bin/bash
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

BASE_COLOR=39ac34
BORDER_COLOR=000000
STAR_COLOR=ffff00

echo Fetching Maps marker images...
# get basic markers
for LETTER in A B C D E F G H I J; do
  curl -o $LETTER.png \
      "http://www.google.com/chart?chst=d_map_pin_letter&chld=$LETTER|$BASE_COLOR|$BORDER_COLOR" >/dev/null 2>&1
done

# get star markers
# for LETTER in A B C D E F G H I J; do
#   curl -o marker-$LETTER-star.png \
#       "http://www.google.com/chart?chst=d_map_xpin_letter&chld=pin_star|$LETTER|$BASE_COLOR|$BORDER_COLOR|$STAR_COLOR"
# done

# get simple marker
curl -o simple.png \
    "http://www.google.com/chart?chst=d_map_pin_letter&chld=|$BASE_COLOR|$BORDER_COLOR" >/dev/null 2>&1

# get shadow
curl -o shadow.png "http://www.google.com/chart?chst=d_map_pin_shadow" >/dev/null 2>&1