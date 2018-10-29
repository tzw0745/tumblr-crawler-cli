### [English](/README.md) | 简体中文

# tumblr-crawler-cli
高性能&高定制化的Tumblr下载工具。
![](http://pictures.tzw0745.cn/18-9-29/13036783.jpg)

# 特性 
* 丰富的命令行。
* 支持多线程下载。
* 确保文件完整性。
* 支持不同类型的网络代理。
* 兼容Python2和Python3。

# 准备工作
```shell
$ git clone git@github.com:tzw0745/tumblr-crawler-cli.git
$ cd tumblr-crawler-cli
$ pip install -r requirements.txt  # -i https://pypi.tuna.tsinghua.edu.cn/simple/
$ python tumblr-crawler.py --help
```
> 大陆用户推荐使用清华大学TUNA的pypi源以提高pip的安装速度；

> **注意：** 如果想使用socks代理，需要再安装一个第三方模组：**pySocks**
```shell
$ pip install pySocks
```

# 使用方法
```shell
usage: tumblr-crawler.py [-h] [-p] [-v] [-d SAVE_DIR] [-x PROXY]
                         [-n THREAD_NUM] [--min MIN_SIZE] [--overwrite]
                         [--interval INTERVAL] [--retries RETRIES]
                         sites [sites ...]

Crawler Tumblr Photos and Videos

positional arguments:
  sites                 tumblr sites

optional arguments:
  -h, --help            show this help message and exit
  -p, --photo           whether to download photo
  -v, --video           whether to download video
  -d SAVE_DIR, --dir SAVE_DIR
                        download file save directory
  -x PROXY, --proxy PROXY
                        http request agent, support http/socks
  -n THREAD_NUM, --thread THREAD_NUM
                        number of download threads, default is 5
  --min MIN_SIZE        minimum size of downloaded files, default is 0k
                        (unlimited)
  --overwrite           overwrite file (if it exists)
  --interval INTERVAL   http request interval, default is 0.5 (seconds)
  --retries RETRIES     http request retries, default is 3
```

## 例子
* 下载Tumblr [@liamtbyrne](http://liamtbyrne.tumblr.com)上所有的图片和视频：
```shell
$ python tumblr-crawler.py liamtbyrne
```

* 指定下载文件类型：
```shell
$ python tumblr-crawler.py -p liamtbyrne  # 只下载图片
$ python tumblr-crawler.py --video liamtbyrne  # 只下载视频
```

* 下载文件到其它文件夹：
```shell
$ python tumblr-crawler.py -d /somedir/ liamtbyrne
```

* 设置网络代理：
```shell
$ python tumblr-crawler.py --proxy http://127.0.0.1:1080 liamtbyrne  # http proxy
$ python tumblr-crawler.py -x socks5h://127.0.0.1:1080 liamtbyrne  # socket5 proxy
```

* 设置更多下载线程以提高下载速度：
```shell
$ python tumblr-crawler.py -n 20 liamtbyrne
```

* 只希望下载超过一定大小的文件：
```shell
$ python tumblr-crawler.py --min 0.5m liamtbyrne  # 只下载超过512k的文件
$ python tumblr-crawler.py --min 100k liamtbyrne  # 只下载超过100k的文件
```

# 待添加的功能
* 自定义下载文件命名格式。
* 支持多种下载工具，如wget、aria2c等。
* ……

# 更新日志
* 2018年10月09日：
  * 修改命令行参数。
* 2018年10月06日：
  * 增加最小文件体积设置。
* 2018年10月04日：
  * 异步&多线程解析tumblr站点；
  * 优化代码结构；
  * 修改命令行参数。
* 2018年10月03日：
  * 优化媒体文件提取兼容性。
* 2018年09月29日：
  * **使用临时文件机制以确保文件被完整下载；**
  * 程序结束时提示文件总数；
  * 修复命令行参数BUG；
  * 修复多线程BUG。
* 2018年09月28日：
  * 第一个版本。
