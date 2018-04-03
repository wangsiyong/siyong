# -*- coding:utf-8 -*-
import os
import csv
import json
import glob
from itertools import chain
from pprint import pprint


class JsonParser(object):

    def __init__(self):
        self._data = None
        self._header = []
        self._nodules = []

    def parse(self, filename):
        self._data = None
        with open(filename) as fp:
            self._data = json.load(fp)

    def toJSON(self, filename):
        assert self._data is not None

    def toCSV(self, filename):
        assert self._data is not None
        self._prepare()
        with open(filename, 'w') as fp:
            writer = csv.DictWriter(fp, fieldnames=self._header)
            writer.writeheader()
            for d in self._nodules.values():
                # print(d)
                writer.writerow(d)

    def _prepare(self):
        self._nodules = self._data['Nodules']
        for other_key in ['version', 'count', 'labelVersion']:
            self._nodules.pop(other_key, None)

        self._header = []

        for key, n in self._nodules.items():
            sourceType = n.get('sourceType', None) or n.get('SourceType', '0')
            n['SourceType'] = sourceType
            n.pop('sourceType', None)
            if key == 'VerifiedNodule':
                for vk in ['True', 'Solid', 'Malign', 'Mixed', 'GGO', 'Calc']:
                    n[vk] = n.get(key).get(vk, 'false')
            # 没有verifiedNodule时, 赋值'false'
            for vk in ['True', 'Solid', 'Malign', 'Mixed', 'GGO', 'Calc']:
                n[vk] = n.get(key, {}).get(vk, 'false')
            n = {k: v for k, v in n.items() if not k.startswith('@') and not isinstance(v, dict)}
            self._nodules[key] = n
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
