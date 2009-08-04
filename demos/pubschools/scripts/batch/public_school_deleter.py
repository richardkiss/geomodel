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

"""Public school deleter using the mapper framework.

This entity mapper deletes all entities of a given kind.
"""

__author__ = 'api.roman.public@gmail.com (Roman Nurik)'

import sys

import remote_client

import mapper

sys.path.append('../..')
import models


class PublicSchoolDeleter(mapper.Mapper):
  """Public school deleter using mapper framework."""
  KIND = models.PublicSchool

  def map(self, entity):
    return ([], [entity])


if __name__ == '__main__':
  PublicSchoolDeleter().run(batch_size=100)

