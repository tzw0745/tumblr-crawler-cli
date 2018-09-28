# tumblr-crawler
高性能&高定制化的Tumblr下载工具。
![](https://pictures.tzw0745.cn/18-9-28/98992040.jpg)
### [English Document](/README.md)

# 特性 
* 丰富的命令行。
* 支持多线程下载。
* 支持不同类型的网络代理。
* 兼容Python2和Python3。

# 准备工作
```shell
$ git@github.com:tzw0745/tumblr-crawler-cli.git
$ cd tumblr-crawler-cli
$ sudo pip install -r requirements.txt  # -i https://pypi.tuna.tsinghua.edu.cn/simple/
$ python tumblr-crawler.py --help
```
> 大陆用户推荐使用清华大学TUNA的pypi源以提高pip的安装速度；

> **注意：** 如果想使用socks代理，需要再安装一个第三方模组：**pySocks**
```shell
$ sudo pip install pySocks
```

# 使用方法
```shell
usage: tumblr-crawler.py [-h] [-t {video,all,photo}] [-d SAVE_DIR] [-x PROXY]
                         [-o {true,false}] [-w WORKER_NUM] [-i INTERVAL]
                         [-r RETRY]
                         sites [sites ...]

Crawler Tumblr Photos and Videos

positional arguments:
  sites                 sites

optional arguments:
  -h, --help            show this help message and exit
  -t {video,all,photo}, --type {video,all,photo}
                        tumblr post type you want to crawler
  -d SAVE_DIR, --dir SAVE_DIR
                        where to save downloaded files
  -x PROXY, --proxy PROXY
                        proxy for http request, support http/https/socks
  -o {true,false}, --overwrite {true,false}
                        is overwrite exists file, default is false
  -w WORKER_NUM, --worker WORKER_NUM
                        number of worker thread, default is 5
  -i INTERVAL, --interval INTERVAL
                        download interval for single worker, default is 0.5
                        (seconds)
  -r RETRY, --retry RETRY
                        retry times for download failed post, default is 3
```

## 例子
* 下载Tumblr [@liamtbyrne](http://liamtbyrne.tumblr.com)上所有的图片和视频：
```shell
$ python tumblr-crawler.py liamtbyrne
```

* 只下载视频，不下载图片:
```shell
$ python tumblr-cralwer.py -t video liamtbyrne
```

* 下载文件到其它文件夹：
```shell
$ python tumblr-cralwer.py -d /somedir/ liamtbyrne
```

* 设置网络代理：
```shell
$ python tumblr-cralwer.py --proxy http://127.0.0.1:1080 liamtbyrne  # http proxy
$ python tumblr-cralwer.py -x socks5h://127.0.0.1:1080 liamtbyrne  # socket5 proxy
```

* 设置更多下载线程以提高下载速度：
```shell
$ python tumblr-cralwer.py -w 20 liamtbyrne
```

# 待添加的功能
* 自定义下载文件命名格式。
* 支持多种下载工具，如wget、aria2c等。
* ……

# 更新日志
* 2018年09月28日: 第一个版本