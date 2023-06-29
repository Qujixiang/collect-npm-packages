#!/bin/bash
if [ $# -ne 1 ]; then
    echo "Usage: $0 <package_path>" >&1
    exit 1
fi
package_path=$1

if [ ! -d $1 ]; then
	exit 1
fi
cd $1
#解压并删除原始压缩包
for folder in $(ls *.tgz); do
    folder_name="${folder%.tgz}" 
    mkdir "$folder_name"
    tar zxvf "$folder" -C "$folder_name"
    rm "$folder"
done

#所有文件夹结尾加上.tgz
for folder in */; do
    folder_name="${folder%/}" 
    new_name="${folder_name}.tgz"
    mv "$folder_name" "$new_name"
done

#修改二级子文件夹为package
for folder in */; do
	folder_name="${folder%/}" 
	PackPath="$folder_name/package"
	if [ ! -d "$PackPath" ]; then
		mv $folder_name/* $PackPath
	fi
	
done



