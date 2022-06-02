# bob-plans -- Archived Repository
**Notice: This repository is part of a Conary/rpath project at SAS that is no longer supported or maintained. Hence, the repository is being archived and will live in a read-only state moving forward. Issues, pull requests, and changes will no longer be accepted.**

Overview
--------
This repository holds build configuration scripts for SAS App Engine. It is
used by bob, a continuous integration tool that runs preconfigured rMake jobs
with fresh code from git.

The centos-6n directory holds bob plan files for the App Engine itself. Each
".bob" file is one build job. The "requires" and "config" directories support
these bob plans.

platform-tools bob plans are for the supporting packages of each supported OS
platform.

jobs-clean holds Jenkins job templates. The ./manage.sh script can download,
normalize, update inter-job dependencies, and create/update Jenkins jobs using
these files.
