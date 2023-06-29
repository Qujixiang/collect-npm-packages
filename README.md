# collect-NPM-packages
> Automatically collect new published packages every day from NPM registry.

## Install
Create a virtual environment and activate it, then install the third library.
```bash
./install.sh
```

## Usage

### A full day of npm packages
需要更改13行goal_day的值
```bash
source env/bin/activate
python download_packages.py
```

### only get messages for the specified number and days
需要更改13行goal_day的值+30行i的h值
```bash
python only_information.py
```

### only download by requirement notes
无需更改，下载目前requirements目录下记录的npm包
```bash
python only_information.py
```
