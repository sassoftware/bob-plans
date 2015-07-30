#!/bin/fish

set ver $argv
if [ "$ver" = "" ]
    echo "missing argument: tag"
    exit 1
end

set tags (python ~/grouptag.py \
    'group-rbuilder-appliance=pdt.cny.sas.com@sas:rba-8[is: x86(i486,i586,i686) x86_64]' \
    'group-devimage-appliance=pdt.cny.sas.com@sas:devimage-8[is: x86 x86_64]' \
    'group-updateservice-appliance=pdt.cny.sas.com@sas:rus-8[is: x86 x86_64]' \
    --get-git-repos --recurse)

for l in $tags
    set repo (basename (echo $l | awk '{print $1}') | cut -d . -f 1)
    set branch (echo $l | awk '{print $2}')
    set tag (echo $l | awk '{print $3}')
    echo "tagging $repo $tag"
    pushd $repo
        git checkout $branch
        git pull
        git tag -a -m "tagging AppEngine $ver" $ver $tag
        git push --tags
    popd
end
