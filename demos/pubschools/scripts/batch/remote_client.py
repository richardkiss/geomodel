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

"""Module for executing code locally against a remote app datastore."""

__author__ = 'api.roman.public@gmail.com (Roman Nurik)'

import base64
import getpass
import sys

# Replace the path below with your GAE Python SDK path.
sys.path.append('/Applications/GoogleAppEngineLauncher.app/Contents/Resources/'
                'GoogleAppEngine-default.bundle/Contents/Resources/'
                'google_appengine/')

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db


def auth_func():
  return raw_input('Email: '), getpass.getpass('Password: ')


app_id = sys.argv[1]
if len(sys.argv) > 2:
  host = sys.argv[2]
else:
  host = '%s.appspot.com' % app_id

remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)
