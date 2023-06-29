#解压并删除原始压缩包
for i in $(ls *.tgz); do
    folder_name="${i%.tgz}" 
    mkdir "$folder_name"
    tar zxvf "$i" -C "$folder_name"
    rm "$i"
done

#所有文件夹结尾加上tgz
for folder in */; do
    folder_name="${folder%/}" 
    new_name="${folder_name}.tgz"
    mv "$folder_name" "$new_name"
done

#修改二级子文件夹为package
for folder in */*/; do
    folder_name="${folder%/}"
    if [ "$folder_name" != "package" ]; then
        new_name="${folder_name%/*}/package"
        mv "$folder_name" "$new_name"
    fi
done


