# -*- coding:utf-8 -*-
import os
import csv
import json
import glob
from itertools import chain
from pprint import pprint


def join_duplicate_keys(ordered_pairs):
    '''to load duplicate key json'''
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            if isinstance(d[k], list):
                d[k].append(v)
            else:
                newlist = []
                newlist.append(d[k])
                newlist.append(v)
                d[k] = newlist
        else:
            d[k] = v
    return d



class DuplicateDict(dict):
    '''to dump duplicate key(item) json'''
    def __init__(self, data):
        self['who'] = '12sigma'     # need to have something in the dictionary 
        self._data = data

    def __getitem__(self, key):
        return self._value

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        for key, value in self._data.items():
            if isinstance(value, list) and key == 'item':
                for i in value:
                    if isinstance(i, dict):
                        self._value = DuplicateDict(i)
                    else:
                        self._value = i
                    yield key
            elif isinstance(value, dict):
                self._value = DuplicateDict(value)
                yield key
            else:
                self._value = value
                yield key


class JsonParser(object):

    def __init__(self):
        self._data = None
        self._header = []
        self._nodules = []

    def parse(self, filename):
        self._data = None
        with open(filename) as fp:
            self._data = json.load(fp, object_pairs_hook=join_duplicate_keys)
            pprint(self._data)

    def toJSON(self, filename):
        assert self._data is not None

    def toCSV(self, filename):
        assert self._data is not None
        self._prepare()
        with open(filename, 'wb') as fp:
            writer = csv.DictWriter(fp, fieldnames=self._header)
            writer.writeheader()
            for d in self._nodules:
                writer.writerow(d)


    def _prepare(self):
        nodules = self._data['Nodules']
        if 'item' in nodules:
            items = nodules['item']
            if isinstance(items, dict):
                items = [items]
        else:
            items = []
            for key in nodules.keys():
                if key.startswith('item'):
                    items.append(nodules[key])

        self._header = []
        self._nodules = sorted(items, key=lambda v: int(v['Label']))
        for n in self._nodules:
            sourceType = n.get('sourceType', None) or n.get('SourceType', '0')
            n['SourceType'] = sourceType
            n.pop('sourceType', None)
            for k in n.keys():
                if k.startswith('@'):
                    n.pop(k)
                elif isinstance(n[k], dict):
                    vn = n.pop(k)
                    if k == 'VerifiedNodule':
                        for vk in ['True', 'Solid', 'Malign', 'Mixed', 'GGO', 'Calc']:
                            n[vk] = vn.get(vk, 'false')
            if not self._header:        # 最好再加层判断，确保使用最长的表头
                prior = {'Label', 'SourceType', 'True', 'Solid', 'Malign', 'Mixed', 'GGO', 'Calc'}
                _header = set(n.keys()) - prior
                self._header.extend(['Label', 'SourceType', 'True', 'Solid', 'Malign', 'Mixed', 'GGO', 'Calc'])
                self._header.extend(sorted(_header))


jsonParser = None

def json2csv(jsonfile, csvfile=''):
    global jsonParser
    if jsonParser is None:
        jsonParser = JsonParser()
    jsonParser.parse(jsonfile)
    if not csvfile:
        csvfile = os.path.splitext(jsonfile)[0] + '.csv'
    jsonParser.toCSV(csvfile)


def dir2csv(dir):
    for f in chain(glob.glob('{}/*.json'.format(dir)), glob.glob('{}/*/*.json'.format(dir))):
        json2csv(f)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', nargs='+', help='single json file')
    parser.add_argument('--dir', nargs='+', help='json directory, batch mode')
    args = parser.parse_args()
    if args.file:
        for f in args.file:
            json2csv(f)
    elif args.dir:
        for d in args.dir:
            dir2csv(d)
    else:
        parser.print_help()
