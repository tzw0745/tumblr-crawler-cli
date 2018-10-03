# coding:utf-8
"""
Created by tzw0745 at 18-9-28
"""
# region import
import json
import os
import re
import time
from datetime import datetime
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

# endregion

queue_sites = Queue()  # 待解析站点队列
queue_down = Queue()  # 待下载队列
queue_fail = Queue()  # 下载失败队列
down_stop = False  # 下载停止信号

# 当post信息非标准格式时解析图片的正则
photo_regex = re.compile(r'https://\d+.media.tumblr.com/\w{32}/tumblr_[\w.]+')


def parse_site_thread(session, post_type, save_dir, retires, interval):
    """
    添加图片、视频下载任务到待下载队列
    :param post_type: post类型
    :param save_dir: 下载路径
    :param session: requests.Session
    :param retires: http请求重试次数
    :param interval: http请求间隔时间
    :return:
    """
    if not isinstance(session, requests.Session):
        raise TypeError('Param "session" must be request.Session')

    while not queue_sites.empty():
        try:
            site_name = queue_sites.get(block=True, timeout=0.5)
        except Empty:
            break

        print('start crawler tumblr site: {}'.format(site_name))
        site_dir = os.path.join(save_dir, site_name)
        os.mkdir(site_dir) if not os.path.exists(site_dir) else None

        global queue_down
        gmt_fmt = '%Y-%m-%d %H.%M.%S GMT'
        if post_type in ('photo', 'all'):
            for post in tumblr_posts(session, site_name,
                                     'photo', retires, interval):
                post_id, date = post['id'], post['gmt'].strftime(gmt_fmt)
                # 将图片url加入下载队列
                for photo_url in post['photos']:
                    photo_name = os.path.split(urlsplit(photo_url).path)[-1]
                    photo_name = '{}.{}.{}'.format(date, post_id, photo_name)
                    photo_path = os.path.join(site_dir, photo_name)
                    queue_down.put((photo_path, photo_url))
        if post_type in ('video', 'all'):
            for post in tumblr_posts(session, site_name,
                                     'video', retires, interval):
                # 将视频url加入下载队列
                post['date'] = post['gmt'].strftime(gmt_fmt)
                video_name = '{i[date]}.{i[id]}.{i[ext]}'.format(i=post)
                video_path = os.path.join(site_dir, video_name)
                queue_down.put((video_path, post['video']))


def download_thread(thread_name, session, overwrite, interval):
    """
    持续下载文件，直到stop_sing为True
    :param thread_name: 线程名称，用于输出
    :param session: requests.Session
    :param overwrite: 是否覆盖已存在文件
    :param interval: http请求间隔时间
    :return:
    """
    if not isinstance(session, requests.Session):
        raise TypeError('Param "session" must be request.Session')

    msg = ' '.join(['Thread', str(thread_name), '{}: {}'])
    global queue_down, queue_fail, down_stop, temp_dir
    while not down_stop:
        if queue_down.empty():
            continue
        try:
            task_path, task_url = queue_down.get(block=True, timeout=0.5)
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


def tumblr_posts(session, site, post_type, retries, interval):
    """
    获取tumblr博客下所有的文章
    :param session: request.Session，用于发送请求
    :param site: 站点id
    :param post_type: 文章类型，包括photo和video
    :param retries: http请求重试次数
    :param interval: http请求间隔时间
    :return: 文章信息列表迭代器
    """
    if not isinstance(session, requests.Session):
        raise TypeError('Param "s" must be requests.Session')
    if not re.match(r'^[a-zA-Z0-9_-]+$', site):
        raise ValueError('Param "site" not match "^[a-zA-Z0-9_-]+$"')
    if post_type not in ('photo', 'video'):
        raise ValueError('Param "post_type" must be "photo" or "video"')

    def _max_width_sub(node, sub_name):
        """
        获取node下max-width属性最大的子节点的文本
        :param node: xml父节点
        :param sub_name: 子节点名称
        :return: 子节点的文本
        """
        return sorted(
            node.findall(sub_name),
            key=lambda _i: int(_i.get('max-width', '0'))
        )[-1].text

    page_size, start = 50, 0
    gmt_fmt = '%Y-%m-%d %H:%M:%S GMT'
    while True:
        api = 'http://{}.tumblr.com/api/read'.format(site)
        params = {'type': post_type, 'num': page_size, 'start': start}
        start += page_size
        # 获取文章列表
        for _retry in range(retries + 1):
            try:
                time.sleep(interval)
                r = session.get(api, params=params, timeout=3)
                if r.status_code not in (200, 404):
                    continue
                break
            except requests.exceptions.RequestException:
                continue
        else:
            break
        if r.status_code == 404:
            raise ValueError('tumblr site "{}" not found'.format(site))
        posts = etree.fromstring(r.content).find('posts').findall('post')
        if not posts:
            break

        for post in posts:
            post_info = {
                'id': post.get('id'),
                'gmt': datetime.strptime(post.get('date-gmt'), gmt_fmt),
                'type': post_type
            }
            if post_type == 'photo':
                # 获取文章下所有图片链接
                if post.findall('photo-url'):  # 标准格式
                    photos = []
                    for photo_set in post.iterfind('photoset'):
                        for photo in photo_set.iterfind('photo'):
                            photos.append(_max_width_sub(photo, 'photo-url'))
                    first_photo = _max_width_sub(post, 'photo-url')
                    if first_photo:
                        photos.append(first_photo)
                else:  # 非标准格式，用正则
                    photos = photo_regex.findall(''.join(post.itertext()))
                post_info['photos'] = photos
                yield post_info
            elif post_type == 'video':
                # 获取视频链接
                try:
                    video_ext = post.find('video-source').find('extension').text
                except AttributeError:  # 忽略非标准格式
                    continue
                tree = html.fromstring(_max_width_sub(post, 'video-player'))
                options = json.loads(tree.get('data-crt-options'))
                if not options['hdUrl']:
                    options['hdUrl'] = tree.getchildren()[0].get('src')
                post_info.update({'video': options['hdUrl'], 'ext': video_ext})
                yield post_info

        time.sleep(interval)


def main():
    args = parser.parse_args()
    # region args check
    args.interval = float(args.interval)
    if not 0 <= args.interval <= 10:
        raise ValueError('Arg "INTERVAL" must between 0 and 10')
    args.thread_num = int(args.thread_num)
    if not 1 <= args.thread_num <= 20:
        raise ValueError('Arg "THREAD_NUM" must between 1 and 20')
    args.retries = int(args.retries)
    if not 0 <= args.retries <= 5:
        raise ValueError('Arg "retries" must between 0 and 5')
    for site in args.sites:
        if not re.match(r'^[a-zA-Z0-9_-]+$', site):
            raise ValueError('Args "sites" not match "^[a-zA-Z0-9_-]+$"')
    args.overwrite = args.overwrite.lower() == 'true'
    # endregion

    session = requests.session()
    if args.proxy:
        session.proxies = {'http': args.proxy, 'https': args.proxy}

    global queue_sites, queue_down, queue_fail, down_stop
    # 加入待解析站点队列
    for site_name in args.sites:
        queue_sites.put(site_name)
    # 多线程解析站点（最多3个线程）
    _parse_thread_num = min(len(args.sites), 3)
    parse_thread_pool = []
    for i in range(_parse_thread_num):
        thread_args = (session, args.post_type, args.save_dir,
                       args.retries, args.interval)
        _t = Thread(target=parse_site_thread, args=thread_args)
        _t.setDaemon(True)
        _t.start()
        parse_thread_pool.append(_t)

    # 多线程下载
    down_thread_pool = []
    for _retry in range(args.retries + 1):
        if not down_thread_pool:
            # 创建下载线程池
            for i in range(args.thread_num):
                thread_args = (i, session, args.overwrite, args.interval)
                _t = Thread(target=download_thread, args=thread_args)
                _t.setDaemon(True)
                _t.start()
                down_thread_pool.append(_t)

        # 等待站点解析线程结束
        for thread in parse_thread_pool:
            thread.join()
        # 等待下载队列清空
        while not queue_down.empty():
            continue
        # 发送下载停止信号并等待下载线程结束
        down_stop = True
        for thread in down_thread_pool:
            thread.join()

        # 如全部下载成功则结束重试
        if queue_fail.empty():
            break
        queue_down, queue_fail = queue_fail, queue_down
        down_stop = False
        down_thread_pool = []

        # 移除临时文件夹
        global temp_dir
        if isinstance(temp_dir, str) and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()
