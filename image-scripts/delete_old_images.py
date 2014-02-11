#!/usr/bin/python
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
