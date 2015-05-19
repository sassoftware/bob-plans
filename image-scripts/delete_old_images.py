#!/usr/bin/python
#
# Copyright (c) SAS Institute Inc.
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
#


import os
import sys
from conary.lib import util


path, numToKeep = sys.argv[1:]
numToKeep = int(numToKeep)
subdirs = sorted(x for x in os.listdir(path)
    if x.replace('_', '').isdigit())
discard = subdirs[:-numToKeep]
for subdir in discard:
    subdir = os.path.join(path, subdir)
    for subpath in os.listdir(subdir):
        subpath = os.path.join(subdir, subpath)
        if os.path.isfile(subpath):
            # Truncate the file first so that if it's still mounted over NFS,
            # the space will still be freed up
            open(subpath, 'w').close()
    util.rmtree(subdir)
