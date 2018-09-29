### English | [简体中文](/README-CN.md)

# tumblr-crawler
Tumblr Download Tool with High Speed and Customization.
![](http://pictures.tzw0745.cn/18-9-28/98992040.jpg)

# Feature
* Rich command line parameters support.
* Multi-threaded Download support.
* Different Type of Proxy support.
* Python2 & Python3 Compatibility.

# Prepare
```shell
$ git@github.com:tzw0745/tumblr-crawler-cli.git
$ cd tumblr-crawler-cli
$ sudo pip install -r requirements.txt  # -i https://pypi.tuna.tsinghua.edu.cn/simple/
$ python tumblr-crawler.py --help
```
> **NOTICE:** if you want use socks proxy for this program, you need install another package: **pySocks**
```shell
$ sudo pip install pySocks
```

# Usage
```shell
usage: tumblr-crawler.py [-h] [-t {photo,all,video}] [-d SAVE_DIR] [-x PROXY]
                         [-o {false,true}] [-n THREAD_NUM] [-i INTERVAL]
                         [-r RETRY]
                         sites [sites ...]

Crawler Tumblr Photos and Videos

positional arguments:
  sites                 sites

optional arguments:
  -h, --help            show this help message and exit
  -t {photo,all,video}, --type {photo,all,video}
                        tumblr post type you want to crawler
  -d SAVE_DIR, --dir SAVE_DIR
                        where to save downloaded files
  -x PROXY, --proxy PROXY
                        proxy for http request, support http/https/socks
  -o {false,true}, --overwrite {false,true}
                        is overwrite exists file, default is false
  -n THREAD_NUM, --thread THREAD_NUM
                        number of download thread, default is 5
  -i INTERVAL, --interval INTERVAL
                        download interval for single thread, default is 0.5
                        (seconds)
  -r RETRY, --retry RETRY
                        retry times for download failed file, default is 3
```

## Example
* you want download all photos and videos from tumblr [@liamtbyrne](http://liamtbyrne.tumblr.com):
```shell
$ python tumblr-crawler.py liamtbyrne
```

* you just want download all videos, not include photos:
```shell
$ python tumblr-cralwer.py -t video liamtbyrne
```

* you want put download all files to another directory:
```shell
$ python tumblr-cralwer.py -d /somedir/ liamtbyrne
```

* you want use proxy for download files:
```shell
$ python tumblr-cralwer.py --proxy http://127.0.0.1:1080 liamtbyrne  # http proxy
$ python tumblr-cralwer.py -x socks5h://127.0.0.1:1080 liamtbyrne  # socket5 proxy
```

* you want set more thread to speed up the download speed:
```shell
$ python tumblr-cralwer.py -n 20 liamtbyrne
```

# Coming Feature
* Customize filename format.
* Multiple download tools support like wget, aria2c.
* ...

# Change log
* 2018-09-28: first version