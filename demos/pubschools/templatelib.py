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

"""A template library consisting of various frontend/UI related helper tags."""

__author__ = 'api.roman.public@gmail.com (Roman Nurik)'

import os

from google.appengine.api import users
from google.appengine.ext import webapp


JSAPI_KEYS = {
  'localhost:8081': 'ABQIAAAAsc0UQXoo2BnAJLhtpWCJFBR4EqRj3RNZnoYuzojShxUjcPQKRRTRGGOs44wdQ4X8DzLXMfd1zp6Pag',
  'geomodel-demo.appspot.com:80': 'ABQIAAAAKkfkHb2nXsD0o1OX2TbdkRTF1o4efM8vQJVwhtHQDLR3ZWMiYhT5A9y4YtISxJ2FetOMuCL1YkBiaw',
  '2.latest.geomodel-demo.appspot.com:80': 'ABQIAAAAKkfkHb2nXsD0o1OX2TbdkRTviFmNkNIQO8yqbxHmKO-CSduAsRR3q-4j7qE0AI6PhpvozLMFiXKlWg',
}


register = webapp.template.create_template_register()


@register.simple_tag
def jsapi_key():
  # the os environ is actually the current web request's environ
  server_key = '%s:%s' % (os.environ['SERVER_NAME'], os.environ['SERVER_PORT'])
  return JSAPI_KEYS[server_key] if server_key in JSAPI_KEYS else ''


def _current_request_uri():
  """Returns the current request URI."""
  return os.environ['PATH_INFO'] + (('?' + os.environ['QUERY_STRING'])
                                    if os.environ['QUERY_STRING'] else '')

@register.simple_tag
def login_url(dest_url=''):
  """Template tag for creating login URLs."""
  dest_url = dest_url or _current_request_uri()
  return users.create_login_url(dest_url)


@register.simple_tag
def logout_url(dest_url=''):
  """Template tag for creating logout URLs."""
  dest_url = dest_url or _current_request_uri()
  return users.create_logout_url(dest_url)
