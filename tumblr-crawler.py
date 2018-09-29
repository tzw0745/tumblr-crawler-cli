# coding:utf-8
"""
Created by tzw0745 at 18-9-28
"""
import json
import os
import re
import time
import shutil
from threading import Thread

import requests
from lxml import etree, html

try:
    # Python3 import
    from urllib.parse import urlsplit
    from queue import Queue, Empty
except ImportError:
    # Python2 import
    from urlparse import urlparse as urlsplit
    from Queue import Queue, Empty

try:
    # after Python3.2
    from tempfile import TemporaryDirectory

    temp_dir = TemporaryDirectory('tumblr_crawler_cli')
except ImportError:
    temp_dir = '.tumblr_crawler_cli'
    os.mkdir(temp_dir) if not os.path.exists(temp_dir) else None

from args import parser

queue_down = Queue()  # 待下载队列
queue_fail = Queue()  # 下载失败队列
stop_sign = False  # 线程停止信号


def download_thread(thread_name, session, overwrite=False, interval=0.5):
    """
    持续下载文件，直到stop_sing为True
    :param thread_name: 线程名称，用于输出
    :param session: request.Session
    :param overwrite: 是否覆盖已存在文件
    :param interval: 单个进程下载文件的间隔，减少出现异常的概率
    :return:
    """
    if not isinstance(session, requests.Session):
        raise TypeError('Param "session" must be request.Session')

    msg = ' '.join(['Thread', str(thread_name), '{}: {}'])
    global queue_down, queue_fail, stop_sign, temp_dir
    while not stop_sign:
        if queue_down.empty():
            continue
        try:
            task_path, task_url = queue_down.get(True, 0.5)
        except Empty:
            continue
        # 判断文件是否存在
        if not overwrite and os.path.isfile(task_path):
            print(msg.format('Exists', task_path))
            continue
        # 向url发送请求
        time.sleep(interval)
        try:
            r = session.get(task_url, timeout=3)
        except requests.exceptions.RequestException:
            # 请求失败
            print(msg.format('RequestException', task_path))
            queue_fail.put((task_path, task_url))
            continue
        # 先写入临时文件
        _temp_name = 'tumblr_thread_{}.downloading'.format(thread_name)
        _temp_path = os.path.join(
            temp_dir if isinstance(temp_dir, str) else temp_dir.name,
            _temp_name
        )
        chunk_size = 10 * 1024 * 1024  # 10M缓存
        try:
            with open(_temp_path, 'wb') as f:
                for content in r.iter_content(chunk_size=chunk_size):
                    f.write(content)
            # 下载完后再移动到目标目录
            shutil.move(_temp_path, task_path)
        except (IOError, OSError):
            print(msg.format('IO/OSError', _temp_path))
            print(msg.format('IO/OSError', task_path))
            queue_fail.put((task_path, task_url))
            continue
        print(msg.format('Completed', task_path))


def tumblr_posts(session, site, post_type):
    """
    获取tumblr博客下所有的文章
    :param session: request.Session，用于发送请求
    :param site: 站点id
    :param post_type: 文章类型，包括photo和video
    :return: 文章信息列表迭代器
    """
    if not isinstance(session, requests.Session):
        raise TypeError('Param "s" must be requests.Session')
    if not re.match(r'^[a-zA-Z0-9_]+$', site):
        raise ValueError('Param "site" not match "^[a-zA-Z0-9_]+$"')
    if post_type not in ('photo', 'video'):
        raise ValueError('Param "post_type" must be "photo" or "video"')

    def _max_width_sub(node, sub_name):
        """
        获取node下max-width属性最大的子节点的文本
        :param node: xml父节点
        :param sub_name: 子节点名称
        :return: 子节点的文本
        """
        if not node.findall(sub_name):
            return None
        return sorted(
            node.findall(sub_name),
            key=lambda _i: int(_i.get('max-width', '0'))
        )[-1].text

    page_size, start = 50, 0
    while True:
        api = 'http://{}.tumblr.com/api/read'.format(site)
        params = {'type': post_type, 'num': page_size, 'start': start}
        start += page_size
        # 获取文章列表
        r = session.get(api, params=params, timeout=3)
        if r.status_code != 200:
            raise ValueError('tumblr site "{}" not found'.format(site))
        posts = etree.fromstring(r.content).find('posts').findall('post')
        if not posts:
            break

        for post in posts:
            post_info = {
                'id': post.get('id'),
                'date': post.get('date-gmt'),
                'type': post_type
            }
            if post_type == 'photo':
                # 获取文章下所有图片链接
                photos = []
                for photo_set in post.iterfind('photoset'):
                    for photo in photo_set.iterfind('photo'):
                        photos.append(_max_width_sub(photo, 'photo-url'))
                first_photo = _max_width_sub(post, 'photo-url')
                photos.append(first_photo) if first_photo not in photos else None
                post_info['photos'] = filter(lambda _p: _p, photos)
                yield post_info
            elif post_type == 'video':
                # 获取视频链接
                video_ext = post.find('video-source').find('extension').text
                tree = html.fromstring(_max_width_sub(post, 'video-player'))
                options = json.loads(tree.get('data-crt-options'))
                if not options['hdUrl']:
                    options['hdUrl'] = tree.getchildren()[0].get('src')
                post_info.update({'video': options['hdUrl'], 'ext': video_ext})
                yield post_info


def main():
    args = parser.parse_args()
    args.interval = float(args.interval)
    if not 0 <= args.interval <= 10:
        raise ValueError('Arg "INTERVAL" must between 0 and 10')
    args.thread_num = int(args.thread_num)
    if not 1 <= args.thread_num <= 20:
        raise ValueError('Arg "THREAD_NUM" must between 1 and 20')
    args.retry = int(args.retry)
    if not 0 <= args.retry <= 5:
        raise ValueError('Arg "RETRY" must between 0 and 5')
    for site in args.sites:
        if not re.match(r'^[a-zA-Z0-9_]+$', site):
            raise ValueError('Args "sites" not match "^[a-zA-Z0-9_]+$"')
    args.overwrite = args.overwrite.lower() == 'true'

    session = requests.session()
    if args.proxy:
        session.proxies = {'http': args.proxy, 'https': args.proxy}

    # 遍历输入站点
    for site in args.sites:
        print('start crawler tumblr site: {}'.format(site))
        site_dir = os.path.join(args.save_dir, site)

        global queue_down, queue_fail, stop_sign
        if args.post_type in ('photo', 'all'):
            for post in tumblr_posts(session, site, 'photo'):
                post_id, date = post['id'], post['date'].replace(':', '.')
                os.mkdir(site_dir) if not os.path.exists(site_dir) else None
                # 将图片url加入下载队列
                for photo_url in post['photos']:
                    photo_name = os.path.split(urlsplit(photo_url).path)[-1]
                    photo_name = '{}.{}.{}'.format(date, post_id, photo_name)
                    photo_path = os.path.join(site_dir, photo_name)
                    queue_down.put((photo_path, photo_url))
        if args.post_type in ('video', 'all'):
            for post in tumblr_posts(session, site, 'video'):
                os.mkdir(site_dir) if not os.path.exists(site_dir) else None
                # 将视频url加入下载队列
                post['date'] = post['date'].replace(':', '.')
                video_name = '{i[date]}.{i[id]}.{i[ext]}'.format(i=post)
                video_path = os.path.join(site_dir, video_name)
                queue_down.put((video_path, post['video']))

        files_count = queue_down.qsize()
        print('found {} files to download'.format(files_count))
        thread_pool = []
        for _retry in range(args.retry):
            if not thread_pool:
                # 创建线程池
                args.thread_num = min(queue_down.qsize(), args.thread_num)
                for i in range(args.thread_num):
                    thread_args = (i, session, args.overwrite, args.interval)
                    _t = Thread(target=download_thread, args=thread_args)
                    _t.setDaemon(True)
                    _t.start()
                    thread_pool.append(_t)

            # 等待下载队列清空
            while not queue_down.empty():
                continue
            # 发送线程停止信号并等待下载线程结束
            stop_sign = True
            for thread in thread_pool:
                thread.join()

            # 如全部下载成功则结束重试
            if queue_fail.empty():
                break
            queue_down, queue_fail = queue_fail, queue_down
            stop_sign = False
            thread_pool = []

        # 移除临时文件夹
        global temp_dir
        if isinstance(temp_dir, str) and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        _ = files_count - queue_down.qsize() - queue_fail.qsize()
        print('\n{} files found, {} files download.'.format(files_count, _))


if __name__ == '__main__':
    main()
