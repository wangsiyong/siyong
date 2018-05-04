# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import re
import json
import logging
from copy import deepcopy
from collections import OrderedDict
import xmltodict
# import promptMessage
# resultKeys = ['CenterX', 'CenterY', 'CenterZ', 'True', 'Malign', 'Solid', 'GGO', 'Mixed', 'Calc','P_B','P_M',
#               u'血管长入', u'血管联通', 'R_B', 'R_M']
resultKeys = ["True", "Solid", "GGO", "Mixed", "Calc", "Malign", "P_B", 
                "P_M", "vessel intruder", "vessel connection", "R_B", "R_M", "AAH",
                "AIS", "MIA", "IA", "IB", "IIA", "IIB", "IIIA"]
additionalDiseasesKey = ["Consolidation", "Emphysema", "Overt_Edema", "Pleural_Effusion", "UIP_Pattern_Fibrosis"]

missedNoduleAttrDict={\
    "Label": "0",
    "PatientCoordBases": "",
    "ScanDirectionMtx0": "0",
    "ScanDirectionMtx1": "0",
    "ScanDirectionMtx2": "0",
    "ScanDirectionType": "",
    "ScanSpacing0": "0",
    "ScanSpacing1": "0",
    "ScanSpacing2": "0",
    "OrigDetCenter0": "0",
    "OrigDetCenter1": "0",
    "OrigDetCenter2": "0",
    "OrigDetScaleInVoxel0": "0",
    "OrigDetScaleInPhysical0": "0",
    "OrigDetBBoxLB0": "0",
    "OrigDetBBoxUB0": "0",
    "OrigDetScaleInVoxel1": "0",
    "OrigDetScaleInPhysical1": "0",
    "OrigDetBBoxLB1": "0",
    "OrigDetBBoxUB1": "0",
    "OrigDetScaleInVoxel2": "0",
    "OrigDetScaleInPhysical2": "0",
    "OrigDetBBoxLB2": "0",
    "OrigDetBBoxUB2": "0",
    "OrigDetScore": "0",
    "OrigDetMaligScore": "0",
    "CenterX": "0",
    "CenterY": "0",
    "CenterZ": "0",
    "DimX": "0",
    "DimY": "0",
    "DimZ": "0",
    "LungPart": "0",
    "LungLobe": "0",
    "lungRADs": "1",
    "aveDiameter2D": "0",
    "aveDiameterSolidComp2D": "0",
    "StatsValid": "false",
    "SegmentationCenterX": "0",
    "SegmentationCenterY": "0",
    "SegmentationCenterZ": "0",
    "SegmentationDimX": "20",
    "SegmentationDimY": "20",
    "SegmentationDimZ": "20",
    "Radius": "0",
    "EllipsoidRadius0": "0",
    "EllipsoidRadius1": "0",
    "EllipsoidRadius2": "0",
    "Volume": "0",
    "HUAve": "0",
    "HUStd": "0",
    "HUAvgAirInLung": "0",
    "HUStdDevAirInLung": "0",
    "_HUAverageSubsolid": "0",
    "_HUStdDevSubsolid": "0",
    "_HUAveWOSubsolid": "0",
    "_HUStdWOSubsolid": "0",
    "_HUMin": "0",
    "_HUMax": "0",
    "_HU5Percentile": "0",
    "_HU95Percentile": "0",
    "_HUMinWOSubsolid": "0",
    "_HUMaxWOSubsolid": "0",
    "_HU5PercentileWOSubSolid": "0",
    "_HU95PercentileWOSubSolid": "0",
    "_HUHistLowerBound": "0",
    "_HUHistUpperBound": "0",
    "_HUHistBinWidth": "0",
    "_HUHistProb": {
        "count": "0",
        "item_version": "0.5.0"
    },
    "_HUHistProbWOSubsolid": {
        "count": "0",
        "item_version": "0.5.0"
    },
    "SubsolidPct": "0",
    "NoduleType": "0",
    "CalcPct": "0",
    "IsCalcNodule": "false",
    "Regularity": "0",
    "Smoothness": "0",
    "RadiusHistogramToCentroid": {
        "binCenter": {
            "count": "0"
        },
        "binValue": {
            "count": "0"
        }
    },
    "RadiusHistogramOnPrincipalAxes": {
        "count": "0",
        "item_version": "0.5.0"
    },
    "StartLocX": "0",
    "StartLocY": "0",
    "StartLocZ": "0",
    "DimInPixelX": "0",
    "DimInPixelY": "0",
    "DimInPixelZ": "0",
    "DistanceToLungWall": "0",
    "ClosestPointOnLungWallX": "0",
    "ClosestPointOnLungWallY": "0",
    "ClosestPointOnLungWallZ": "0",
    "mask": {
        "xBegin": "0",
        "xEnd": "0",
        "yBegin": "0",
        "yEnd": "0",
        "zBegin": "0",
        "zEnd": "0",
        "sliceMask": {
            "version": "0.5.0",
            "count": "0"
        }
    },
    "sourceType": "1",
    "VerifiedNodule": {
        "lablelIndex": "0",
        "Center0": "0",
        "Center1": "0",
        "Center2": "0",
        "True": "false",
        "Malign": "false",
        "Solid": "false",
        "GGO": "false",
        "Mixed": "false",
        "Calc": "false"
    }
}

_logger = logging.getLogger(__name__)

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
        def generator():
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

        return generator()

def pretty_json(s, step_size=4, multi_line_strings=False, advanced_parse=False, tab=False):
    out = ''
    step = 0
    in_marks = False  # Are we in speech marks? What character will indicate we are leaving it?
    escape = False  # Is the next character escaped?

    if advanced_parse:
        # \x1D (group seperator) is used as a special character for the parser
        # \0x1D has the same effect as a quote ('") but will not be ouputted
        # Can be used for special formatting cases to stop text being processed by the parser
        s = re.sub(r'datetime\(([^)]*)\)', r'datetime(\x1D\g<1>\x1D)', s)
        s = s.replace('\\x1D', chr(0X1D))  # Replace the \x1D with the single 1D character

    if tab:
        step_char = '\t'
        step_size = 1  # Only 1 tab per step
    else:
        step_char = ' '
    for c in s:

        if step < 0:
            step = 0

        if escape:
            # This character is escaped so output it without looking at it
            escape = False
            out += c
        elif c in ['\\']:
            # Escape the next character
            escape = True
            out += c
        elif in_marks:
            # We are in speech marks
            if c == in_marks or (not multi_line_strings and c in ['\n', '\r']):
                # but we just got to the end of them
                in_marks = False
            if c not in ["\x1D"]:
                out += c
        elif c in ['"', "'", "\x1D"]:
            # Enter speech marks
            in_marks = c
            if c not in ["\x1D"]:
                out += c
        elif c in ['{', '[']:
            # Increase step and add new line
            step += step_size
            out += c
            out += '\n'
            out += step_char * step
        elif c in ['}', ']']:
            # Decrease step and add new line
            step -= step_size
            out += '\n'
            out += step_char * step
            out += c
        elif c in [':']:
            # Follow with a space
            out += c
            out += ' '
        elif c in [',']:
            # Follow with a new line
            out += c
            out += '\n'
            out += step_char * step
        elif c in [' ', '\n', '\r', '\t', '\x1D']:
            #Ignore this character
            pass
        else:
            # Character of no special interest, so just output it as it is
            out += c
    return out

def xml2json(xml_file, json_file=None):
    with open(xml_file) as f:
        xmlDict = xmltodict.parse(f.read())
    jsonData = OrderedDict()
    nodules = jsonData.setdefault('Nodules', {})
    root = xmlDict['boost_serialization']
    if root.get('sigmaLU_version'):
        nodules['version'] = root['sigmaLU_version']
    nodule_items = nodules.setdefault('item', [])
    origin_items = root.get('Nodules', {}).get('item', [])   # item可能不存在
    verify_items = root.get('VerifiedNodules', {}).get('item', [])
    missed_items = root.get('MissedNodules', {}).get('item', [])   # item可能不存在
    if not isinstance(origin_items, list):  # 处理只有一个item的情况
        origin_items = [origin_items]
    if not isinstance(verify_items, list):
        verify_items = [verify_items]
    if not isinstance(missed_items, list):
        missed_items = [missed_items]
    for oi in origin_items:
        oi['sourceType'] = oi.pop('SourceType', '0' if int(oi['Label']) >= 0 else '1')
        vn = {}
        for vi in verify_items:  # 寻找对应的VerifiedNodule
            if vi['LabelIndex'] == oi['Label']:
                vn = vi
                break
        _vn = oi.setdefault('VerifiedNodule', {'labelIndex': oi['Label']})
        for k in resultKeys:
            if k in ['CenterX', 'CenterY', 'CenterZ']:
                _vn[k] = vn.get(k, '0')
            else:
                v = vn.get(k, 'false')
                if v == '0':
                    v = 'false'
                elif v == '1':
                    v = 'true'
                _vn[k] = v

        sliceMask = oi.get('mask', {}).get('sliceMask')
        if sliceMask:
            sliceMask['version'] = sliceMask.pop('item_version', '0')
        else:   # 给没有自动分割的新增结节补充中心坐标
            for k in ['CenterX', 'CenterY', 'CenterZ']:
                oi[k] = _vn[k]
        nodule_items.append(oi)     # 将item插入json
    for mi in missed_items:     # MissedNodules只有中心坐标
        oi = {'Label': mi['LabelIndex'], 'sourceType': '1'}
        vn = oi.setdefault('VerifiedNodule', {'labelIndex': mi['LabelIndex']})
        for k in resultKeys:
            if k in ['CenterX', 'CenterY', 'CenterZ']:
                oi[k] = vn[k] = mi.get(k, '0')
            else:
                v = mi.get(k, 'false')
                if v == '0':
                    v = 'false'
                elif v == '1':
                    v = 'true'
                vn[k] = v
        nodule_items.append(oi)
    addition = root.get('AdditionalDiseases')
    if addition:
        if isinstance(addition, list):
            jsonData['AdditionalDiseases'] = addition[-1]
        else:
            jsonData['AdditionalDiseases'] = addition
    nodules['count'] = str(len(nodule_items))
    if json_file is None:
        json_file = os.path.splitext(xml_file)[0] + '.json'
    try:
        with open(json_file, 'w') as f:
            f.write(pretty_json(json.dumps(DuplicateDict(jsonData))))
    except Exception as e:
        print(e)
    else:
        # os.remove(xml_file)
        return json_file


class FileHandler(object):
    def __init__(self, path):
        self.path = path
        self.jsonData = OrderedDict()
        self.version = '0.2.0'

    @property
    def count(self):
        return int(self.jsonData['Nodules'].get('count', 0))

    def load(self):
        pass

    def dump(self, path):
        pass

    def parse(self, spacing):
        self.labelStats = {}
        self.labelStats['Labels'] = []
        self.labelStats["sigmaLUVersion"] = self.version
        self.labelStats["addCount"] = 0
        self.labelStats["cadCount"] = 0
        from generateLabel import fillData
        items = self.jsonData['Nodules'].get('item', [])
        if not isinstance(items, list):
            items = [items]
        for item in items:
            try:
                fillData(item, self.labelStats, self.version, spacing)
            except Exception:
                promptMessage.promptedMessage('SigmaLabel', "\n\n  File mistake! \n\n", ok='Yes')
                raise
            if item['sourceType'] == '0':
                self.labelStats["cadCount"] += 1
            else:
                self.labelStats["addCount"] += 1
        self.additionalDict = self.jsonData.get('AdditionalDiseases', {})

    def unparse(self):
        items = self.jsonData['Nodules'].get('item', [])
        if not isinstance(items, list):
            items = [items]
        for item in items:
            label = int(item['Label'])
            verified = item.setdefault('VerifiedNodule', OrderedDict())
            verified["labelIndex"] = str(label)
            verified["Center0"] = str(-self.labelStats[label, 'CenterCoord'][0])
            verified["Center1"] = str(-self.labelStats[label, 'CenterCoord'][1])
            verified["Center2"] = str(self.labelStats[label, 'CenterCoord'][2])
            for k in ['True', 'Malign', 'Solid', 'GGO', 'Mixed', 'Calc','P_B', 'P_M', u'血管长入', u'血管联通', 'R_B', 'R_M']:
                verified[k] = str(self.labelStats[label, k]).lower()

    def index(self):
        return [int(item['Label']) for item in self.jsonData['Nodules']['item']]

    def add(self, node):
        count = self.count
        if count == 0:
            self.jsonData['Nodules']['item'] = node
        elif count == 1:
            item = []
            item.append(self.jsonData['Nodules'].pop('item'))
            item.append(node)
            self.jsonData['Nodules']['item'] = item
        else:
            self.jsonData['Nodules']['item'].append(node)
        self.jsonData['Nodules']['count'] = str(count + 1)

    def remove(self, index):
        count = self.count
        assert count > 0
        if count == 1:
            assert int(self.jsonData['Nodules']['item']['Label']) == index
            self.jsonData['Nodules'].pop('item')
            self.jsonData['Nodules']['count'] = str(count - 1)
        else:
            for item in self.jsonData['Nodules']['item']:
                if index == int(item['Label']):
                    self.jsonData['Nodules']['item'].remove(item)
                    self.jsonData['Nodules']['count'] = str(count - 1)
                    break

    def get_data(self, sortOrder='CenterZ'):
        items = self.jsonData['Nodules'].get('item', [])
        if not isinstance(items, list):
            items = [items]
        sortedIndex = list(map(lambda i:int(i['Label']), sorted(items, key=lambda item:item[sortOrder], reverse=True)))
        return sortedIndex, self.labelStats, self.additionalDict

class XmlHandler(FileHandler):
    def __init__(self, path):
        super(XmlHandler, self).__init__(path)

    def load(self):
        with open(self.path) as f:
            xmlDict = xmltodict.parse(f.read())
        self.jsonData = OrderedDict()
        self.nodules = self.jsonData.setdefault('Nodules', {})
        root = xmlDict['boost_serialization']
        if root.get('sigmaLU_version'):
            self.nodules['version'] = root['sigmaLU_version']
            self.version = root['sigmaLU_version']
        items = self.nodules.setdefault('item', [])
        nodules = root.get('Nodules', {'item': []})
        verified = root.get('VerifiedNodules')
        missed = root.get('MissedNodules', {'item': []})
        for index, item in enumerate(nodules['item']):
            item['SourceType'] = item.pop('SourceType', '0' if int(item['Label']) >= 0 else '1')
            item['VerifiedNodule'] = verified['item'][index]
            items.append(item)
        for item in missed['item']:
            items.append(item)
        addition = root.get('AdditionalDiseases')
        if addition:
            self.jsonData['AdditionalDiseases'] = addition
        self.nodules['count'] = str(len(items))

    def dump(self, path):
        dumpDict = OrderedDict({'boost_serialization': {'@signature': 'serialization::archive', '@version': '13'}})
        copyDict = deepcopy(self.jsonData)
        nodules = copyDict['Nodules']
        verified = OrderedDict({'item': []})
        if nodules.get('version'):
            dumpDict['boost_serialization']['sigmaLU_version'] = nodules.pop('version')
        for nodule in nodules['item']:
            verified['item'].append(nodule.pop('VerifiedNodules'))
        dumpDict['boost_serialization']['sigmaLU_version']['Nodules'] = nodules
        dumpDict['boost_serialization']['sigmaLU_version']['VerifiedNodules'] = verified
        if not path.endswith('.xml'):
            path += '.xml'
        with open(path, 'w') as f:
            f.write(xmltodict.unparse(dumpDict, pretty=True))


class JsonHandler(FileHandler):
    def __init__(self, path):
        super(JsonHandler, self).__init__(path)

    def load(self):
        with open(self.path) as f:
            jsonDict = json.load(f, object_pairs_hook=join_duplicate_keys)
        self.jsonData = OrderedDict(jsonDict)
        if self.jsonData['Nodules'].get('version'):
            self.version = self.jsonData['Nodules']['version']

    def combineMissedNodules(self,item):
        noduleIndex=item['Label']
        nodulePos=(item['CenterX'],item['CenterY'],item['CenterZ'])
        verifiedSection=item['VerifiedNodule']
        newItem=deepcopy(missedNoduleAttrDict)
        #update the attributes with new values
        newItem['OrigDetCenter0'],newItem['OrigDetCenter1'],newItem['OrigDetCenter2']=nodulePos
        newItem['SegmentationCenterX'],newItem['SegmentationCenterY'],newItem['SegmentationCenterZ']=nodulePos
        newItem['CenterX'],newItem['CenterY'],newItem['CenterZ']=nodulePos
        newItem['Label'] = noduleIndex
        #check if current result file's verfiedNodule has CenterX/Y/Z,if yes,then pop them
        if verifiedSection.has_key("CenterX"):
            popKeyList=["CenterX","CenterY","CenterZ"]
            for key in popKeyList:
                verifiedSection.pop(key)
        verifiedSection["Center0"],verifiedSection["Center1"],verifiedSection["Center2"]=nodulePos
        #combine the item now 
        newItem.update(item)
        item.update(newItem)

    def dump(self, path):
        # self.unparse()
        if not path.endswith('.json'):
            path += '.json'
        items = self.jsonData['Nodules'].get('item', [])
        if not isinstance(items, list):
            items = [items]
        for item in items:
            self.combineMissedNodules(item)
        json_str = pretty_json(json.dumps(DuplicateDict(self.jsonData), ensure_ascii=False).encode('utf-8'))
        with open(path, 'w') as f:
            f.write(json_str)
        
class HandlerFactory(object):
    @staticmethod
    def getHandler(resultFile):
        if os.path.exists(resultFile + '.json'):
            _logger.debug("Created Json file Parser NOW.")
            handler = JsonHandler(resultFile + '.json')
        elif os.path.exists(resultFile + '.xml'):
            _logger.debug("Convert XML to JSON.")
            resultFile = xml2json(resultFile+'.xml')
            _logger.debug("Created Json file Parser NOW.")
            handler = JsonHandler(resultFile)
        else:
            _logger.error("ResultFile not found!")
            return
        handler.load()
        return handler


if __name__ == "__main__":
    # currentFilePath = r"E:\hospitalResults\ziwei\NLST_final_229"
    # targetFilePath = r"E:\hospitalResults\ziwei\NLST_final_229\test"
    # fileList=[]
    # #support both of xml and json format result
    # xmlFileList = [x for x in os.listdir(currentFilePath) if
    #             os.path.isfile(os.path.join(currentFilePath, x)) and os.path.splitext(x)[1].lower() == '.xml']
    # jsonFileList =[x for x in os.listdir(currentFilePath) if
    #             os.path.isfile(os.path.join(currentFilePath, x)) and os.path.splitext(x)[1].lower() == '.json' and 'CAD' in x]
    
    # fileList += xmlFileList
    # fileList += jsonFileList

    # for subfile in fileList:
    #     fileName = os.path.splitext(subfile)[0]
    #     createHandler = HandlerFactory.getHandler(os.path.join(currentFilePath, fileName))
    #     createHandler.dump(targetFilePath + '/' + subfile.split('.')[0] + '_cb.json')
    #     # print(subfile)

    _noduleKey = ['Label', 'OrigDetMaligScore', 'OrigDetScore', 'Radius', 'OrigDetCenter0', 'OrigDetCenter1', 'OrigDetCenter2', \
                           'SegmentationDimX', 'SegmentationDimY', 'OrigDetScaleInVoxel0', 'OrigDetScaleInVoxel1', 'OrigDetScaleInVoxel2', \
                           'NoduleType', 'IsCalcNodule', 'aveDiameter2D', 'VerifiedNodule']
    _verifiedKey = ['labelIndex', 'Center0', 'Center1', 'Center2', 'True', 'Malign', 'Solid', 'GGO', 'Mixed', 'Calc']

    file_path = r'D:\temp\NLST_final_batch_229_cases'
    # file_path = r'D:\Sigma_doc\上海肺科医院第二批数据第二次结果文件（602GGO）\part4'
    out_path = r'D:\temp\NLST_final_batch_229_cases_changed'
    # import pprint
    for subfile in os.listdir(file_path):
        # if not subfile.endswith('.json') or 'CAD_Lung' not in subfile:
        if not subfile.endswith('.json'):
            continue
        # read
        data = {}
        nodules = {}
        with open(os.path.join(file_path, subfile)) as f:
            origin = json.load(f, object_pairs_hook=join_duplicate_keys)
            # pprint.pprint(origin)
            nodules = origin.get('Nodules', {})
            if isinstance(nodules.get('item'), dict):
                nodules['item'] = [nodules['item']]
            for item in nodules.get('item', []):
                labelId = item.pop('Label')
                data[labelId] = item

        # write
        obj = deepcopy(data)
        items = []
        for k, v in obj.items():
            v['Label'] = k
            v.setdefault('VerifiedNodule', {})['labelIndex'] = k
            for key in _noduleKey:
                v.setdefault(key, '0')
            items.append(v)
        for item in items:
            for n, pos in enumerate([item.get(i) for i in ['CenterX', 'CenterY', 'CenterZ']]):
                item['VerifiedNodule']['Center{}'.format(n)] = pos
            for key in resultKeys:
                if key not in item.get('VerifiedNodule'):
                    item['VerifiedNodule'][key] = 'false'
        labelVersion = nodules.get('labelVersion') or origin.get('labelVersion')
        version = nodules.get('version') or origin.get('version')
        count = nodules.get('count') or origin.get('count')
        result = {'Nodules': {'labelVersion': labelVersion, 'version': version, 'count': count, 'item':items}}

        json_str = pretty_json(json.dumps(DuplicateDict(result), ensure_ascii=False).encode('utf-8'))
        print(os.path.join(out_path, subfile))
        with open(os.path.join(out_path, subfile), 'w') as fp:
            fp.write(json_str)
