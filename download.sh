#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <destination_path> <requirements_file_path>" >&2
    exit 1
fi

destination_path=$1
requirements_file_path=$2

while IFS= read -r line; do
    npm install $line --prefix $destination_path 
    npm pack $line --pack-destination $destination_path 
done < $requirements_file_path