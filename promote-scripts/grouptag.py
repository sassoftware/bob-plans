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

"""
Script to find packages built from git with bob that supprots getting and
setting tags in conary as well as finding the git repository and revision
to tag.

Listing Git Repository Info -
Given a group or package spec, find all sources that were built from git using
bob, parse their recipes to extract the git repository, branch, and tag
information.

Tagging in Conary -
* Store tag info in keyValue metadata
* Assumes tags are applied to versions that have already been promoted off of
  the devel label.
* Based on the recurse flag either only walk all troves from the same label as
  the specified trove, or walk the entire group structure.
"""

import sys
import epdb
sys.excepthook = epdb.excepthook()

import re
import argparse
import itertools

from conary import trove
from conary import conarycfg
from conary import conaryclient
from conary.deps import deps
from conary.conaryclient import cmdline

class GroupTags(object):
    BLACK_LIST = (
        'centos6.rpath.com@rpath:centos-6e',
        'centos6.rpath.com@rpath:centos-6-common',
    )

    _git_version = re.compile('.*([0-9a-f]{7,40})$')
    _git_snapshot = re.compile(
            '.*addGitSnapshot\(\'(.*)\', branch=\'(.*)\', tag=\'(.*)\'.*\)')

    def __init__(self, trvSpecs, tag=None, recurse=False):
        self.trvSpecs = trvSpecs
        self.tag = tag
        self._recurse = recurse

        self._cfg = conarycfg.ConaryConfiguration(True)
        self._client = conaryclient.ConaryClient(self._cfg)
        self._repos = self._client.getRepos()

        self._nvfs = dict()

    @staticmethod
    def parseTroves(trvSpecs):
        return [ cmdline.parseTroveSpec(x) for x in trvSpecs ]

    def getTags(self):
        tags = self._getTags()
        if not tags:
            print >>sys.stderr, 'no tags found'
            return 1

        for (n, v, f), tag in tags.iteritems():
            print '%s=%s[%s]: %s' % (n, v, f, tag)
        return 0

    def _getTags(self):
        binaries = self._getBinaries(recurse=True)

        md = dict((x, y and y.get(1).get('keyValue') or None) for x, y in itertools.izip(sorted(binaries),
            self._repos.getTroveInfo(trove._TROVEINFO_TAG_METADATA, sorted(binaries))))

        tags = dict((x, y['tag']) for x, y in md.iteritems() if y and 'tag' in y.keys())

        return tags

    def setTags(self):
        tags = self._setTags()
        if not tags:
            print >>sys.stderr, 'no troves found to tag'
            return 1

        for n, v, f in tags:
            print 'set tag for: %s=%s[%s]' % (n, v, f)
        return 0

    def _setTags(self):
        assert self.tag
        binaries = self._getBinaries(recurse=self._recurse)
        trvs = dict((x, y) for x, y in itertools.izip(sorted(binaries),
            self._repos.getTroves(sorted(binaries))))

        req = []
        for nvf, trv in trvs.iteritems():
            md = trv.troveInfo.metadata
            kv = md.get(1).get('keyValue')
            if not kv:
                mi = trove.MetadataItem()
                md.addItem(mi)
                kv = mi.keyValue
            kv['tag'] = self.tag

            req.append((nvf, trv.troveInfo))

        self._repos.setTroveInfo(req)
        return [ x[0] for x in req ]

    def _getBinaries(self, recurse=False):
        srcMap = {}
        nvfs = self._getnvfs(recurse)
        clonedFrom = self._followClonedFrom(nvfs)
        for bnvf, snvf in self._getSourceTroves(clonedFrom).iteritems():
            srcMap.setdefault(snvf, list()).append(bnvf)
        gitRepos = self._getGitRepos(recurse=recurse)

        binaries = set()
        for snvf in gitRepos:
            for bnvf in srcMap.get(snvf):
                binaries.add(clonedFrom[bnvf])

        # Include all groups as well
        binaries |= set(x for x in nvfs if x[0].startswith('group-'))

        return binaries

    def getGitRepos(self):
        gitRepos = self._getGitRepos(recurse=self._recurse)
        if not gitRepos:
            print >>sys.stderr, 'no git repositories found'
            return 1

        for nvf, lst in gitRepos.iteritems():
            for url, branch, tag in lst:
                print url, branch, tag
        return 0

    def _getGitRepos(self, recurse=False):
        repos = {}
        nvfs = self._getnvfs(recurse=recurse)
        clonedFrom = self._followClonedFrom(nvfs)
        sourceVersions = self._getSourceTroves(clonedFrom)
        for n, v, f in set(sourceVersions.values()):
            recipe = self._getRecipe(n, v, f)
            for line in recipe:
                m = self._git_snapshot.match(line)
                if m:
                    url, branch, tag = m.groups()
                    repos.setdefault((n, v, f), list()).append(
                            (url, branch, tag))
        return repos

    def _getnvfs(self, recurse=False):
        if self._nvfs.get((recurse, )):
            return self._nvfs.get((recurse, ))
        nvfs = self._nvfs.setdefault((recurse, ), set())
        specs = self.parseTroves(self.trvSpecs)
        nvfsMap = self._repos.findTroves(self._cfg.installLabelPath, specs)
        for nvf in itertools.chain(*nvfsMap.itervalues()):
            nvfs.add(nvf)
            trv = self._repos.getTrove(*nvf)
            for n, v, f in trv.iterTroveList(weakRefs=True, strongRefs=True):
                # already seen this nvf
                if (n, v, f) in nvfs:
                    continue
                # is a component
                if ':' in n:
                    continue
                # blacklisted labels
                if v.trailingLabel().asString() in self.BLACK_LIST:
                    continue
                # not a git version
                if not self._mightBeGit(v):
                    continue
                # if not recursing, only return nvfs on the same label
                # as the requested nvf
                if not recurse and (nvf[1].trailingLabel().asString() != 
                        v.trailingLabel().asString()):
                    continue
                nvfs.add((n, v, f))
        return nvfs

    def _mightBeGit(self, v):
        return bool(self._git_version.match(v.trailingRevision().version))

    def _getSourceTroves(self, nvfs):
        return dict([ ((n, v, f),
            (x(), v.getSourceVersion(), deps.parseFlavor('')))
            for x, (n, v, f) in itertools.izip(self._repos.getTroveInfo(
                trove._TROVEINFO_TAG_SOURCENAME, nvfs), nvfs) ])

    def _followClonedFrom(self, nvfs):
        """
        Follow cloned from to find the original source for this package.
        """

        nvfsp = {}
        nvfs = list(nvfs)
        ti = self._repos.getTroveInfo(trove._TROVEINFO_TAG_CLONEDFROM, nvfs)
        for (n, v, f), cf in itertools.izip(nvfs, ti):
            if not cf:
                nvfsp[(n, v, f)] = (n, v, f)
            else:
                nvfsp[(n, cf(), f)] = (n, v, f)
        return nvfsp

    def _getRecipe(self, n, v, f):
        recipeName = '%s.recipe' % n.split(':')[0]
        fObjs = self._repos.getFileContentsFromTrove(n, v, f, [recipeName, ])
        return fObjs[0].get()


def main(args):
    parser = argparse.ArgumentParser(description='Manage Group Tags')
    parser.add_argument('troves', metavar='name=version[flavor]', type=str,
            nargs='+', help='list of troves to query or update')
    parser.add_argument('--get-tags', dest='get_tags', action='store_true',
            help='get all tags for a given set of troves')
    parser.add_argument('--get-git-repos', dest='get_git_repos',
            action='store_true',
            help='get get repos and revisions for all troves')
    parser.add_argument('--set-tag', dest='set_tags',
            help='set the tag on all troves')
    parser.add_argument('--recurse', dest='recurse', action='store_true',
            help='recurse all troves')
    ns = parser.parse_args()

    tags = GroupTags(ns.troves, tag=ns.set_tags or None,
            recurse=ns.recurse)

    rc = 0
    if ns.get_tags:
        rc = tags.getTags()
    elif ns.get_git_repos:
        rc = tags.getGitRepos()
    elif ns.set_tags:
        rc = tags.setTags()

    return rc

if __name__ == '__main__':
    sys.exit(main(sys.argv))
