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

if [[ "$1" == "" ]]; then
  echo 'Usage '$0' <app-host-name> <school-csv-file>' >&2
  exit
fi

CSV=$2
CSV_BASE=`basename $2`

appcfg.py upload_data --config_file=public_school_loader.py \
                      --filename=$CSV \
                      --has_header \
                      --kind=PublicSchool \
                      --url=http://$1/remote_api \
                      --db_filename=$CSV_BASE.sql3 \
                      --batch_size=50 \
                      --rps_limit=200 \
                      --num_threads=5 \
                      ../../
