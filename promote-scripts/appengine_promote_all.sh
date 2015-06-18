#!/bin/bash -ex
cd $(dirname $0)
rel="$1"
dest="$2"
if [ -z "$rel" ]
then
    echo "Usage: $0 <branch> <devel|prod>"
    exit 1
fi
if [ "$dest" == prod ]
then
    echo Promoting to production labels
    suffix=""
    plans=prod
else
    if [ "$rel" != "master" ]
    then
        echo Only master branch can be promoted to devel
        exit 0
    fi
    echo Promoting to devel labels
    suffix="-devel"
    plans=devel
fi
shift 2

major=8
ci_base="newton.eng.rpath.com@sas:rba-$rel"
dest_base="/pdt.cny.sas.com@sas:"

./promote_safe.py "${dest_base}rba-$major$suffix" \
    "group-rbuilder-dist=$ci_base-rba" \
    -m "promote to $plans" --interactive
bob ../centos-6n/proddefs/rba-${plans}.bob

if [ $plans == devel ]
then
./promote_safe.py "${dest_base}platform-$major$suffix" \
    "group-rpath-platform=$ci_base-platform" \
    -m "promote to $plans"
fi

./promote_safe.py "${dest_base}rus-$major$suffix" \
    "group-updateservice-appliance=$ci_base-updateservice" \
    -m "promote to $plans" --interactive
bob ../centos-6n/proddefs/rus-${plans}.bob

./promote_safe.py "${dest_base}devimage-$major$suffix" \
    "group-devimage-appliance=$ci_base-devimage" \
    -m "promote to $plans" --interactive
bob ../centos-6n/proddefs/devimage-${plans}.bob
