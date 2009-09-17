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

"""Main frontend/UI handlers."""

__author__ = 'api.roman.public@gmail.com (Roman Nurik)'

import os
import os.path
import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


template.register_template_library(
    'django.contrib.humanize.templatetags.humanize')
template.register_template_library('templatelib')


def make_static_handler(template_file):
  """Creates a webapp.RequestHandler type that renders the given template
  to the response stream."""
  class StaticHandler(webapp.RequestHandler):
    def get(self):
      self.response.out.write(template.render(
          os.path.join(os.path.dirname(__file__), template_file),
          {'current_user': users.get_current_user()}))
  
  return StaticHandler


def main():
  application = webapp.WSGIApplication([
      ('/', make_static_handler('../templates/index.html')),
      ('/speedtest', make_static_handler('../templates/speedtest.html')),
      ],
      debug=('Development' in os.environ['SERVER_SOFTWARE']))
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
