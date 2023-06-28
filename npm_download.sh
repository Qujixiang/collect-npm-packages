#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <destination_path> <requirements_file_path>" >&2
    exit 1
fi

destination_path=$1
requirements_file_path=$2

while IFS= read -r line; do
    npm install $line --prefix $destination_path
    echo "install $line in $destination_path" >> note_ing.txt
done < $requirements_file_path

while IFS= read -r line; do
    npm pack $line --pack-destination $destination_path 
    echo "Packing $line in $destination_path " >> note_ing.txt
done < $requirements_file_path