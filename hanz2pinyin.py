# coding:utf-8

import os
import pathlib
from pypinyin import lazy_pinyin

def is_zh(c):
    """
    这段代码来自 jjgod 写的 XeTeX 预处理程序\n
    判断是否是汉字
    """
    x = ord(c)
    # Punct & Radicals
    if x >= 0x2e80 and x <= 0x33ff:
        return True

    # Fullwidth Latin Characters
    elif x >= 0xff00 and x <= 0xffef:
        return True

    # CJK Unified Ideographs &
    # CJK Unified Ideographs Extension A
    elif x >= 0x4e00 and x <= 0x9fbb:
        return True
    # CJK Compatibility Ideographs
    elif x >= 0xf900 and x <= 0xfad9:
        return True

    # CJK Unified Ideographs Extension B
    elif x >= 0x20000 and x <= 0x2a6d6:
        return True

    # CJK Compatibility Supplement
    elif x >= 0x2f800 and x <= 0x2fa1d:
        return True

    else:
        return False

def do(path):
    for roots, dirs, _ in os.walk(path):
        # 遍历所有目录
        for d in dirs:
            string = ''
            for c in d:
                if is_zh(c):
                    string += c
            if string:
                replaced = ''.join(lazy_pinyin(string)) + '_'
                old_dir = pathlib.Path(roots, d)
                new_dir = pathlib.Path(roots, d.replace(string, replaced))
                os.rename(old_dir, new_dir)

def main():
    do(r'E:\201601-3')


if __name__ == '__main__':
    main()