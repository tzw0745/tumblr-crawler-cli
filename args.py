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
            err_msg = 'save_dir:{} is not a valid path'
            raise argparse.ArgumentTypeError(err_msg.format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            err_msg = 'save_dir:{} is not a readable dir'
            raise argparse.ArgumentTypeError(err_msg.format(prospective_dir))


class LimitInterval(argparse.Action):
    def __call__(self, _parser, namespace, values, option_string=None):
        try:
            interval = float(values)
        except ValueError:
            err_msg = 'interval:{} is not a float number'.format(values)
            raise argparse.ArgumentTypeError(err_msg.format(values))
        if not 0.1 <= interval <= 5:
            err_msg = 'interval must be between 0.1 and 10.0'
            raise argparse.ArgumentTypeError(err_msg)
        setattr(namespace, self.dest, interval)


class LimitRetries(argparse.Action):
    def __call__(self, _parser, namespace, values, option_string=None):
        try:
            retries = int(values)
        except ValueError:
            err_msg = 'retries:{} is not a number'.format(values)
            raise argparse.ArgumentTypeError(err_msg.format(values))
        if not 0 <= retries <= 10:
            err_msg = 'retries must be between 0 and 10'
            raise argparse.ArgumentTypeError(err_msg)
        setattr(namespace, self.dest, retries)


class LimitThread(argparse.Action):
    def __call__(self, _parser, namespace, values, option_string=None):
        try:
            thread = int(values)
        except ValueError:
            err_msg = 'thread:{} is not a number'.format(values)
            raise argparse.ArgumentTypeError(err_msg.format(values))
        if not 1 <= thread <= 20:
            err_msg = 'thread must be between 1 and 20'
            raise argparse.ArgumentTypeError(err_msg)
        setattr(namespace, self.dest, thread)


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
    default='.', help='download file save directory'
)
parser.add_argument(
    '-x', '--proxy', dest='proxy',
    help='http request agent, support http/socks'
)
parser.add_argument(
    '-n', '--thread', dest='thread_num', default=5, action=LimitThread,
    help='number of download threads, default is 5'
)
parser.add_argument(
    '--overwrite', dest='overwrite', action='store_true',
    help='overwrite file (if it exists)'
)
parser.add_argument(
    '--interval', dest='interval', default=0.5, action=LimitInterval,
    help='http request interval, default is 0.5 (seconds)'
)
parser.add_argument(
    '--retries', dest='retries', default=3, action=LimitRetries,
    help='http request retries, default is 3'
)
parser.add_argument(dest='sites', help='tumblr sites', nargs='+')
