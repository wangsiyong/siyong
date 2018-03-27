# coding:utf-8

import os
import json


def parse_one_file(filename):
    origin = {}
    # verified = {}
    with open(filename) as f:
        origin = json.load(f)
    nodules = origin.get('MammoDisease', {})
    # count = origin.get('count') or nodules.get('count')
    # labelVersion = origin.get('labelVersion') or nodules.get('labelVersion')
    # version = origin.get('version') or nodules.get('version')
    # AdditionalDiseases = origin.get('AdditionalDiseases', {})
    for k, v in nodules.items():
        if not isinstance(v, dict):
            continue
        verified = v.get('VerifiedInfo', {})
        # 'Findings' rename to 'Disease'
        v['Disease'] = v.pop('Findings', None) or v.pop('Disease', None) or ''
        if verified:
            verified['Disease'] = verified.pop('Findings', None) or verified.pop('Disease', None) or ''

        # 'Lesion level BIRADS' rename to 'BI-RADS'
        v['BI-RADS'] = v.pop('Lesion level BIRADS', None) or v.pop('BI-RADS', None) or ''
        if verified:
            verified['BI-RADS'] = verified.pop('Lesion level BIRADS', None) or verified.pop('BI-RADS', None) or ''

        # if no 'Malignancy', then init it
        v['Malignancy'] = v.pop('Malignancy', None) or ''
        verified['Malignancy'] = verified.pop('Malignancy', None) or ''

        # deal with ['Disease', 'BI-RADS', 'Malignancy']
        for i in ['Disease', 'BI-RADS', 'Malignancy']:
            # list to str
            if isinstance(v[i], list):
                try:
                    v[i] = str(v[i][0])
                except IndexError:
                    v[i] = ''
                try:
                    verified[i] = str(verified[i][0])
                except IndexError:
                    verified[i] = ''
            # int to str
            elif isinstance(v[i], int):
                v[i] = str(v[i])
                verified[i] = str(verified[i])

        # deal with 'Malignancy'
        v_malig = v.get('Malignancy')
        verified_malig = verified.get('Malignancy')
        if v_malig in ['0', '1']:
            v['Malignancy'] = ''
            verified['Malignancy'] = ''
        elif v_malig == '2':
            v['Malignancy'] = '0'
        elif v_malig == '3':
            v['Malignancy'] = '1'
        if verified_malig in ['0', '1']:
            verified['Malignancy'] = ''
        elif v_malig == '2':
            verified['Malignancy'] = '0'
        elif v_malig == '3':
            verified['Malignancy'] = '1'

        # 'ROIType' Polygon   TiltedRectangle  Rectangle
        if 'vertex' in v:
            verified['TiltedRectangle'] = v.pop('vertex')
            v['ROIType'] = 'TiltedRectangle'
            verified['ROIType'] = 'TiltedRectangle'
            verified['Lesion'] = 'True'
            for key in ['CenterX', 'CenterY', 'DimX', 'DimY']:
                v[key] = 0
        elif 'points' in v:
            verified['Points'] = v.pop('points')
            v['ROIType'] = 'Polygon'
            verified['ROIType'] = 'Polygon'
            verified['Lesion'] = 'True'
            for key in ['CenterX', 'CenterY', 'DimX', 'DimY']:
                v[key] = 0
        else:
            v['ROIType'] = 'Rectangle'
            verified['ROIType'] = 'Rectangle'
            verified['Lesion'] = 'True'
            for key in ['CenterX', 'CenterY', 'DimX', 'DimY']:
                verified[key] = v[key]

    # update version 0.5.0
    origin['labelVersion'] = '0.5.0'

    return origin


def main(path):
    for roots, _, files in os.walk(path):
        for filename in files:
            if not filename.endswith('.json'):
                continue
            json_file = os.path.join(roots, filename)
            print(json_file)
            data = parse_one_file(json_file)
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=4)


if __name__ == '__main__':
    main(r'D:\temp\SavedLabel1_139cases_changed')
