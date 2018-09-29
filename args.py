# coding:utf-8
"""
Created by tzw0745 at 18-9-28
"""
import os
import argparse


class ReadableDir(argparse.Action):
    def __call__(self, _parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))


parser = argparse.ArgumentParser(
    description='Crawler Tumblr Photos and Videos'
)
# parser.add_argument(
#     '-c', '--config', dest='config', type=argparse.FileType('r'),
#     help='config file path'
# )
parser.add_argument(
    '-t', '--type', dest='post_type', default='all',
    choices={'photo', 'video', 'all'}, help='tumblr post type you want to crawler'
)
parser.add_argument(
    '-d', '--dir', dest='save_dir', action=ReadableDir,
    default='.', help='where to save downloaded files'
)
parser.add_argument(
    '-x', '--proxy', dest='proxy',
    help='proxy for http request, support http/https/socks'
)
parser.add_argument(
    '-o', '--overwrite', dest='overwrite', default='false',
    choices={'true', 'false'}, help='is overwrite exists file, default is false'
)
parser.add_argument(
    '-n', '--thread', dest='thread_num', default=5,
    help='number of download thread, default is 5'
)
parser.add_argument(
    '-i', '--interval', dest='interval', default=0.5,
    help='download interval for single thread, default is 0.5 (seconds)'
)
parser.add_argument(
    '-r', '--retry', dest='retry', default=3,
    help='retry times for download failed file, default is 3'
)
parser.add_argument(dest='sites', help='sites', nargs='+')
