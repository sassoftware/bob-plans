#!/bin/bash -ex
label="$1"
push_root="$2"
shift 2

bindir=$(dirname $0)
timestamp=$(date "+%Y%m%d_%H%M%S")
hostname=$(echo "$label" | cut -d. -f1)
base=$(echo "$label" | cut -d: -f2)
label_dir="$push_root/$base"
image_dir="$label_dir/$timestamp"
image_base="image-disc1.iso"
image_name="$image_dir/$image_base"
temp_name="$image_name.tmp"

mkdir -p "$image_dir"
"$bindir/imagescript.py" \
    -l "$label" \
    -u bob -p thebuilder \
    -s rba.cny.sas.com \
    -P "$hostname" \
    -i 0 \
    -o "$temp_name"
find "$label_dir" -type d -exec chmod 0755 {} +
find "$label_dir" -type f -exec chmod 0644 {} +
#explodeiso "$temp_name" "$image_dir/contents"
mv "$temp_name" "$image_name"
ln -fn "$image_name" "$label_dir/$image_base"
ln -sfn "$image_dir" "$label_dir/current"
"$bindir/delete_old_images.py" "$label_dir" 2
