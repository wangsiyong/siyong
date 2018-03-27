# coding:utf-8

import os
import shutil
from util import load_duplicate_json, dump_duplicate_json


def deal_with_file(filename, out_file):
    """
    删除json文件中labelindex(label)的重复部分
    :param filename: json绝对文件名
    :param out_file: 处理后存放的绝对文件名
    """
    label_list = []
    duplicate_item = []
    origin = load_duplicate_json(filename)
    nodules = origin.get('Nodules', {})
    items = nodules.get('item', [])
    if isinstance(items, dict):
        items = [items]
    for item in items:
        label = item.get('Label')
        if label not in label_list:
            label_list.append(label)
        else:
            duplicate_item.append(item)
    if not duplicate_item:
        return
    for i in duplicate_item:
        items.remove(i)
    nodules['count'] = str(int(nodules.get('count')) - len(duplicate_item))
    dump_duplicate_json(origin, out_file)


def main(walk_dir, out_dir=r'D:\temp\out'):
    """
    遍历目录
    :param walk_dir: 被遍历目录
    :param out_dir: 输出目录（有默认值），此处没有使用
    """
    for roots, _, files in os.walk(walk_dir):
        for filename in files:
            if not filename.endswith('.json'):
                continue
            json_file = os.path.join(roots, filename)
            print(json_file)
            # out_file = os.path.join(out_dir, filename)
            deal_with_file(json_file, json_file)


if __name__ == '__main__':
    main(r'D:\temp\ConvertedJsonFiles')
