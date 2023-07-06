#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <destination_path> <requirements_file_path>" >&2
    exit 1
fi

destination_path=$(realpath $1)
requirements_file_path=$(realpath $2)

cd $destination_path
while IFS= read -r line; do
    npm pack $line
done < $requirements_file_path