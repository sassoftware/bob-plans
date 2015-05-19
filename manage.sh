#!/bin/bash -e
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


usage() {
    echo "usage: $0 {fetch,push} <branch>"
    exit 1
}

if [[ -n "$JBUTLER_PATH" ]]
then
    export PYTHONPATH="$JBUTLER_PATH:$PYTHONPATH"
    JBUTLER="$JBUTLER_PATH/commands/jbutler"
else
    JBUTLER=jbutler
fi

cmd=$1
branch=$2
[[ -z "$branch" ]] && usage

case "$cmd" in
    fetch)
        # Pull all jobs for the branch down and strip out the branch name
        rm -rf jobs jobs-clean
        mkdir jobs jobs-clean
        $JBUTLER jobs retrieve --filter="rbuilder-${branch}_.*"
        for job in jobs/*.xml
        do
            name=$(echo $(basename $job) | sed -e "s/${branch}/@BRANCH@/g")
            sed -e "s/$branch/@BRANCH@/g" "$job" | tidy -config meta/tidy.conf >"jobs-clean/$name"
        done
        git add jobs-clean
        git add -u jobs-clean
        git status
        echo "Retrieved all jobs in branch '$branch' and updated the git index"
        ;;

    update-deps)
        # Rewrite SCM watch paths and inter-job dependencies to match the .bob files
        bob-deps centos-6n --scm --graph >meta/graph.py
        python meta/jenkins_deps.py
        git add -u meta/graph.py jobs-clean
        git status
        echo "Deps updated, now run './manage.sh push $branch' and 'git commit'"
        ;;

    push)
        # Substitute a branch name into the generic jobs-clean templates and push it to jenkins
        rm -rf jobs
        mkdir jobs
        $JBUTLER jobs retrieve --filter="rbuilder-${branch}_.*"
        existing=$(mktemp)
        ls jobs >"$existing"

        for job in jobs-clean/*.xml
        do
            name=$(echo $(basename $job) | sed -e "s/@BRANCH@/${branch}/g")
            sed -e "s/@BRANCH@/$branch/g" "$job" >"jobs/$name"
            if grep -q "^$name$" "$existing"
            then
                $JBUTLER jobs update "jobs/$name"
            else
                $JBUTLER jobs create "jobs/$name"
            fi
            rm -f "jobs/$name"
        done
        rm -f "$existing"
        echo "Pushed all jobs in branch '$branch' to jenkins"
        extra=$(ls jobs)
        if [[ -n "$extra" ]]
        then
            echo "The following jobs are not currently tracked: $extra"
            echo "Either delete them or use './manage.sh fetch $branch' to pull them in."
        fi
        ;;

    *)
        usage
        ;;
esac
exit 0
