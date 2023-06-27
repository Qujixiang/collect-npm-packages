#!/bin/bash

folders=("data/package_info" "logs" "packages" "requirements")
for folder in "${folders[@]}"
do
  if [ ! -d "$folder" ]; then
    mkdir -p "$folder"
  fi
done

if [ ! -d "env" ]; then
  python3 -m venv env
  source env/bin/activate
  pip install -r requirements.txt
  deactivate
fi