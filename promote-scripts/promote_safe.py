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

import epdb
import os
import sys

from conary import changelog
from conary import display
from conary import errors
from conary import state
from conary import versions
from conary.callbacks import CloneCallback
from conary.cmds import clone
from conary.conarycfg import ConaryConfiguration
from conary.conaryclient import ConaryClient
from conary.conaryclient import cmdline
from conary.conaryclient import callbacks
from conary.lib import util


SAFE_DEFAULT = set([
                    'centos6.rpath.com@rpath:centos-6e',
                    'centos6.rpath.com@rpath:centos-6-common',
                    ])

class QuietCloneCallback(CloneCallback):
    def __init__(self, cfg=None, defaultMessage=None):
        self.cfg = cfg
        self.defaultMessage = defaultMessage

    def getCloneChangeLog(self, trv):
        if self.defaultMessage:
            if self.cfg.name is None or self.cfg.contact is None:
                raise ValueError, \
                    "name and contact information must be set for clone"
            return changelog.ChangeLog(self.cfg.name, self.cfg.contact, self.defaultMessage)
        else:
            return trv.getChangeLog()

def excepthook(e_type, e_value, e_tb):
    if isinstance(e_value, KeyboardInterrupt):
        print >>sys.stderr
        print >>sys.stderr, 'Interrupted by Ctrl-C'
        sys.exit(-1)

    sys.excepthook = sys.__excepthook__
    util.formatTrace(e_type, e_value, e_tb, withLocals=False)
    epdb.post_mortem(e_tb, e_type, e_value)

def main(argv):
    import optparse

    safe_branches = set()
    safe_labels = set(SAFE_DEFAULT)

    usage = 'Usage: %prog [options] <target branch> <trovespec>+'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-m', '--message', dest='message',
        help="Commit message for cloned sources")
    parser.add_option('--context',
        help="Execute the promote within CONTEXT")
    parser.add_option('--to-file', metavar='FILE', help="Write changeset to "
        "FILE instead of committing it to a repository")
    parser.add_option('--safe-label', action='callback', type='string',
        callback=lambda x, y, value, z: safe_labels.add(
            versions.Label(value)),
        help="Don't flatten troves on this label")
    parser.add_option('--safe-branch', action='callback', type='string',
        callback=lambda x, y, value, z: safe_branches.add(
            versions.VersionFromString(value)), 
        help="Don't flatten troves on this branch")
    parser.add_option('--clear', action='callback',
            callback=lambda w, x, y, z: (safe_labels.clear(),
                safe_branches.clear()),
        help="Clear the safe branch and label lists")

    parser.add_option('-v', '--verbose', action='store_true',
        help="Display extra information")
    parser.add_option('-q', '--quiet', action='store_true',
        help="Display less unnecessary output")
    parser.add_option('--interactive', dest='interactive',
        action='store_true')
    parser.add_option('--no-interactive', dest='interactive',
        action='store_false')
    parser.add_option('--info', action='store_true',
        help="Show which branches will be flattened and quit")
    parser.add_option('--test', action='store_true',
        help="Do everything but the final commit")
    parser.add_option('--default-only', action='store_true',
        help="Only promote byDefault=True troves")
    parser.add_option('--config', action='append')

    (options, args) = parser.parse_args(argv)

    if len(args) < 2:
        parser.print_help()
        return 1

    targetBranch = versions.VersionFromString(args[0])

    # Parse trovespecs from commandline
    troveSpecs = []
    for x in args[1:]:
        n, v, f = cmdline.parseTroveSpec(x)
        troveSpecs.append((n, v, f))

    if options.info:
        print 'No changes will be made'
    elif options.test:
        print 'Will discard all changes'
    elif options.to_file:
        print 'Will write promote to changeset file %r' % options.to_file
    elif options.interactive:
        print 'Will ask before committing to repository'
    else:
        print 'Will commit to repository WITHOUT asking!'
    
    # Parsing's all done; let the games begin
    sys.excepthook = excepthook
    ccfg = ConaryConfiguration(True)
    for optname in 'interactive', 'quiet':
        if getattr(options, optname) is not None:
            setattr(ccfg, optname, getattr(options, optname))
    if options.config:
        for line in options.config:
            ccfg.configLine(line)
    cc = ConaryClient(ccfg)

    # Set conary context, if available
    context = ccfg.context
    if os.access('CONARY', os.R_OK):
        conaryState = state.ConaryStateFromFile('CONARY')
        if conaryState.hasContext():
            context = conaryState.getContext()
    if options.context:
        context = options.context
    if context:
        ccfg.setContext(context)

    # Find specified groups and build a frumptuu
    try:
        topLevelGroups = findGroups(cc, troveSpecs)
    except errors.TroveNotFound, e:
        print >>sys.stderr, '\n'.join(e.args)
        return 2
    frumptuu = buildFrumptuu(cc, targetBranch, topLevelGroups,
        safe_branches, safe_labels, verbose=options.verbose)

    # Exit after flattening info was printed if called with --info
    if options.info:
        return 0

    message = options.message
    if ccfg.quiet:
        callback = QuietCloneCallback(ccfg, defaultMessage=message)
    else:
        callback = callbacks.CloneCallback(ccfg, defaultMessage=message)

    # Do the promote
    okay, cs = flatten(cc, topLevelGroups, frumptuu,
        defaultOnly=options.default_only, callback=callback)
    if not okay:
        return 0

    # Confirm and commit
    if not ccfg.quiet:
        targetName = options.to_file \
            and 'file "%s"' % options.to_file or 'repository'
        if ccfg.interactive or options.test:
            print '+ Ready to commit changesets to', targetName
        else:
            print '+ Committing changesets to', targetName

    if finishClone(cc, ccfg, cs, callback,
      test=options.test, targetFile=options.to_file):
        return 0
    else:
        return 3

def findGroups(cc, troveSpecs):
    ss = cc.getSearchSource(flavor=0)

    # Get list of matching group troves
    if not cc.cfg.quiet: print '+ Finding troves to promote'
    results = ss.findTroves(troveSpecs, bestFlavor=False)
    topLevelGroups = []
    for spec, troves in results.iteritems():
        latest = max([x[1] for x in troves])
        troves = [x for x in troves if x[1] == latest]
        topLevelGroups.extend(troves)
    return topLevelGroups

def buildFrumptuu(cc, targetBranch, topLevelGroups,
  safeBranches=frozenset(), safeLabels=frozenset(SAFE_DEFAULT), verbose=False):
    ss = cc.getSearchSource(flavor=0)

    # Iterate over top-level groups to get a list of all branches
    branches_flattened = {}
    branches_spared = {}
    if not cc.cfg.quiet: print '+ Recursing through all troves'
    for troveTup, troveObj, flags, indent in display.iterTroveList(
      ss, topLevelGroups,
      recurseAll = True,
      recursePackages = True,
      showNotByDefault = True,
      showNotExists = True):
        n, v, f = troveTup
        b = v.branch()
        if b.asString() in safeBranches or \
          b.label().asString() in safeLabels:
            branches_spared.setdefault(b, []).append(troveTup)
        else:
            branches_flattened.setdefault(b, []).append(troveTup)

    # Show what we'll flatten
    def branchDetail(branches, heading):
        print
        print heading
        print '-' * 40
        for branch, troves in branches.iteritems():
            print branch.asString()
            if verbose:
                shown = set()
                for n, v, f in troves:
                    if (n, v, f) in shown:
                        continue
                    shown.add((n, v, f))
                    print '  %s=%s%s' % (n, v.trailingRevision().asString(),
                        (not f.isEmpty()) and ('[%s]' % f) or '')

    if not cc.cfg.quiet:
        branchDetail(branches_spared, 'BRANCHES PRESERVED')
        branchDetail(branches_flattened, 'BRANCHES FLATTENED TO %s' %
            targetBranch.asString())
        print

    # Build frumptuu
    frumptuu = {}
    for x in branches_flattened:
        frumptuu[x] = targetBranch

    return frumptuu

def flatten(cc, topLevelGroups, frumptuu, defaultOnly=False, callback=None):
    if not cc.cfg.quiet: print '+ Downloading changesets'

    okay, cs = cc.createSiblingCloneChangeSet(frumptuu, topLevelGroups,
            updateBuildInfo=False, infoOnly=False, callback=callback,
            cloneOnlyByDefaultTroves=defaultOnly, cloneSources=True)

    return okay, cs


def finishClone(client, cfg, cs, callback, info=False, test=False,
                 ignoreConflicts=False, targetFile=None):
    repos = client.repos
    if cfg.interactive or info:
        print 'The following clones will be created:'
        clone.displayCloneJob(cs)

    if info:
        return

    if cfg.interactive:
        print
        okay = cmdline.askYn('continue with clone? [y/N]', default=False)
        if not okay:
            return

    if targetFile:
        cs.writeToFile(targetFile)
    elif not test:
        repos.commitChangeSet(cs, callback=callback)
    return cs


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
