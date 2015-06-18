#!/bin/bash -e
top=$(cd $(dirname $0) && pwd)
branch=$1
if [ "$branch" != "master" ]
then
    echo This script is for master branch only
    exit 0
fi
shift 1
rbuild="rbuild --skip-default-config --config-file $top/../rbuildrc"

project=pdt
suffix=rba-8-devel
label=${project}.cny.sas.com@sas:$suffix
dir=$project-$suffix
imagename='SAS App Engine 8-devel x86_64 ISO'
image_url=$(echo "$imagename" | sed -e 's/ /%20/g')
bucket=sas-app-engine-ci

rm -rf $dir
$rbuild init $label
cd $dir/Release
$rbuild build images "$imagename"

cd $top
imagefile=appengine-8-devel-x86_64.iso
http_proxy= wget -O $imagefile "http://rba.cny.sas.com/api/v1/projects/$project/project_branches/$label/project_branch_stages/Release/images_by_name/$image_url/latest_file"
s3put -b $bucket --reduced --grant=public-read --prefix=$top $imagefile
rm -f $imagefile

imageids=$($rbuild list images |grep '^[0-9]' | cut -d' ' -f1)
if [ -n "$imageids" ]
then
    $rbuild delete images --force $imageids ||:
fi
