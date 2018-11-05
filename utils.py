# coding:utf-8
"""
Created by tzw0745 at 18-11-5
"""
import re

import string

_formatter = string.Formatter()


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def safe_format(fmt, **kwargs):
    """
    安全字符串格式化，在缺少对应参数时仍能正常工作
    :param fmt: 格式字符串
    :param kwargs: 参数字典
    :return: 格式化后的字符串
    """
    return _formatter.vformat(fmt, (), SafeDict(**kwargs))


def clean_fn(filename):
    """
    移除文件名中的特殊字符
    :param filename: 文件名
    :return: 处理后的文件名
    """
    return re.sub(r'[\\/:*?"<>|]+', '', filename)


def main():
    print(safe_format('{id}', uid=111))
    print(clean_fn('2018-10-1 19:00 <|>"\\/:*?".zip'))


if __name__ == '__main__':
    main()
