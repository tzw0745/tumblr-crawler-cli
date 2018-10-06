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
            err_msg = 'SAVE_DIR:{} is not a valid path'
            raise argparse.ArgumentTypeError(err_msg.format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            err_msg = 'SAVE_DIR:{} is not a readable dir'
            raise argparse.ArgumentTypeError(err_msg.format(prospective_dir))


class LimitInterval(argparse.Action):
    def __call__(self, _parser, namespace, values, option_string=None):
        try:
            interval = float(values)
        except ValueError:
            err_msg = 'INTERVAL:{} is not a float number'.format(values)
            raise argparse.ArgumentTypeError(err_msg.format(values))
        if not 0.1 <= interval <= 5:
            err_msg = 'INTERVAL must be between 0.1 and 10.0'
            raise argparse.ArgumentTypeError(err_msg)
        setattr(namespace, self.dest, interval)


class LimitRetries(argparse.Action):
    def __call__(self, _parser, namespace, values, option_string=None):
        try:
            retries = int(values)
        except ValueError:
            err_msg = 'RETRIES:{} is not a number'.format(values)
            raise argparse.ArgumentTypeError(err_msg.format(values))
        if not 0 <= retries <= 10:
            err_msg = 'RETRIES must be between 0 and 10'
            raise argparse.ArgumentTypeError(err_msg)
        setattr(namespace, self.dest, retries)


class LimitThread(argparse.Action):
    def __call__(self, _parser, namespace, values, option_string=None):
        try:
            thread = int(values)
        except ValueError:
            err_msg = 'THREAD_NUM:{} is not a number'.format(values)
            raise argparse.ArgumentTypeError(err_msg.format(values))
        if not 1 <= thread <= 20:
            err_msg = 'THREAD_NUM must be between 1 and 20'
            raise argparse.ArgumentTypeError(err_msg)
        setattr(namespace, self.dest, thread)


class LimitMinSize(argparse.Action):
    def __call__(self, _parser, namespace, values, option_string=None):
        num, unit = values[:-1], values[-1].lower()
        if unit not in ('k', 'm'):
            err_msg = 'MIN_SIZE:{} not end with k/K or m/M'
            raise argparse.ArgumentTypeError(err_msg.format(values))
        try:
            min_size = float(num)
        except ValueError:
            err_msg = 'MIN_SIZE:{} is not a number'
            raise argparse.ArgumentTypeError(err_msg.format(num))
        if min_size < 0:
            err_msg = 'MIN_SIZE:{} cant be a negative number'
            raise argparse.ArgumentTypeError(err_msg.format(num))

        multiple = {'k': 1024, 'm': 1024 * 1024}
        min_size = int(min_size * multiple[unit])
        setattr(namespace, self.dest, min_size)


parser = argparse.ArgumentParser(
    description='Crawler Tumblr Photos and Videos'
)
# parser.add_argument(
#     '-c', '--config', dest='config', type=argparse.FileType('r'),
#     help='config file path'
# )
parser.add_argument(
    '-t', '--type', dest='post_type', default='all',
    choices=['all', 'photo', 'video'], help='tumblr post type you want to crawler'
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
    '--min', dest='min_size', default=0, action=LimitMinSize,
    help='minimum size of downloaded files, default is 0k (unlimited)'
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
