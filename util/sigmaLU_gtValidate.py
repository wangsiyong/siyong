# encoding:utf-8
import json
import os
import sys

if sys.version_info[0] == 2:
    print('Error ! Please run with Python 3')
    exit(1)
    from io import open

platform = sys.platform
if platform.startswith('win'):
    slash = '\\'
elif platform.startswith('linux'):
    slash = '/'

# function to solve the problem of duplicated key ("item") in json files
def join_duplicate_keys(ordered_pairs):
    d = {}
    for k, v in ordered_pairs:
        if k in d:
           if type(d[k]) == list:
               d[k].append(v)
           else:
               newlist = []
               newlist.append(d[k])
               newlist.append(v)
               d[k] = newlist
        else:
           d[k] = v
    return d

class SigmaLU_gt_Validate(object):
    '''
    Author Siqi Qin
    Validation for given gt format
    '''
    def __init__(self, filename, nodule_add = [], verified_add = []):
        '''
        This class helps to validate the format of given ground truth file
        :param filename: name to the gt.json file
        :param nodule_add: other keywords for nodule section that you want to check with except for the hard coded ones
        :param verified_add: other keywords for verified section that you want to check with except for the hard coded ones
        '''
        self._filename = filename
        self._obj = json.loads(open(self._filename, 'r', encoding='utf8').read(), object_pairs_hook=join_duplicate_keys)
        self._count = int(self._obj['Nodules']['count'])
        self._noduleKey = ['Label', 'OrigDetMaligScore', 'OrigDetScore', 'Radius', 'OrigDetCenter0', 'OrigDetCenter1', 'OrigDetCenter2', \
                           'SegmentationDimX', 'SegmentationDimY', 'OrigDetScaleInVoxel0', 'OrigDetScaleInVoxel1', 'OrigDetScaleInVoxel2', \
                           'NoduleType', 'IsCalcNodule', 'aveDiameter2D', 'VerifiedNodule']
        self._verifiedKey = ['labelIndex', 'Center0', 'Center1', 'Center2', 'True', 'Malign', 'Solid', 'GGO', 'Mixed', 'Calc']
        self._noduleKey.extend(nodule_add)
        self._verifiedKey.extend(verified_add)
        print("Validate Nodule Keywords:")
        print(self._noduleKey)
        print("Validate Verified Keywords:")
        print(self._verifiedKey)

    def validate(self, outputfile):
        '''
        Loop through all keywords
        :param outputfile: the output log file path
        '''
        with open(outputfile, 'w', encoding='utf-8') as f:
            print('*******************************************')
            print('Validate ', self._filename)
            print('*******************************************')
            f.write('*******************************************' + '\n')
            f.write('Validate ' + self._filename + '\n')
            f.write('*******************************************' + '\n')
            f.write('Validate Nodule Keywords:' + '\n')
            for key in self._noduleKey:
                f.write(key + ', ')
            f.write('\n')
            f.write('*******************************************' + '\n')
            f.write('Validate Verified Keywords:' + '\n')
            for key in self._verifiedKey:
                f.write(key + ', ')
            f.write('\n')
            f.write('*******************************************' + '\n')
            if self._count == 0:
                print("No Nodule for ", self._filename)
                f.write("No Nodule for " + self._filename + '\n')
            else:
                if self._count == 1:
                    self._obj['Nodules']['item'] = [self._obj['Nodules']['item']]
                for child in self._obj['Nodules']['item']:
                    if 'Label' in child:
                        print('Validate Nodule ', str(child['Label']))
                        f.write('Validate Nodule ' + str(child['Label']) + '\n')
                    else:
                        print('Error ! No Label!')
                        f.write('Error ! No Label!' + '\n')
                        raise KeyError
                    for key in self._noduleKey:
                        if key not in child:
                            print('Error ! No ', key, ' in Nodule')
                            f.write('Error ! No ' + key + ' in Nodule' + '\n')
                            raise KeyError
                    print('-----------------------------------')
                    f.write('-----------------------------------' + '\n')
                    if 'VerifiedNodule' in child:
                        if 'labelIndex' in child['VerifiedNodule']:
                            print('Validate Verified ', str(child['VerifiedNodule']['labelIndex']))
                            f.write('Validate Verified ' + str(child['VerifiedNodule']['labelIndex']) + '\n')
                            if int(child['VerifiedNodule']['labelIndex']) != int(child['Label']):
                                print('Error ! Verified Index is not equal to Nodule Index !')
                                f.write('Error ! Verified Index is not equal to Nodule Index !' + '\n')
                                raise KeyError
                            else:
                                for key in self._verifiedKey:
                                    if key not in child['VerifiedNodule']:
                                        print('Error ! No ', key, ' in VerifiedNodule')
                                        f.write('Error ! No ' + key + ' in VerifiedNodule' + '\n')
                                        raise KeyError
                        else:
                            print('Error ! No labelIndex !')
                            f.write('Error ! No labelIndex !' + '\n')
                            raise KeyError
                    print('-----------------------------------')
                    f.write('-----------------------------------' + '\n')
            print('\n')
            f.write('\n')

class SigmaLU_gt_folder_Validate(object):
    def __init__(self, gt_path, gt_postfix, output_path, nodule_add, verified_add):
        '''
        This class helps to validate the ground truth format in a given folder
        :param gt_path: path to the ground truth files
        :param gt_postfix: postfix or the keywords that the ground truth files have income, eg: _CAD
        :param output_path: output to validate results
        :param nodule_add: other keywords for nodule section that you want to check with except for the hard coded ones
        :param verified_add: other keywords for verified section that you want to check with except for the hard coded ones
        '''
        self._gt_path = gt_path
        self._gt_postfix = gt_postfix
        self._output_path = output_path
        if os.path.isdir(self._output_path) == False:
            os.mkdir(self._output_path)
        self._nodule_add = nodule_add
        self._verified_add = verified_add
        self._gt_files = list(filter(lambda gt : self._gt_postfix in gt, os.listdir(self._gt_path)))

    def validate_folder(self):
        for gt in self._gt_files:
            name = gt.split(self._gt_postfix)[0]
            print(name)
            val_gt = SigmaLU_gt_Validate(self._gt_path + slash + gt, self._nodule_add, self._verified_add)
            val_gt.validate(self._output_path + slash + name + '.log')

if __name__ == '__main__':
    file_path = 'D:\\temp\\ConvertedJsonFiles_changed\\Results1_convertedJson\\G42_Zach_convertedJson\\'
    gt_postfix = '_CAD_zach_cb.json'
    output_path = 'D:\\temp\\out1\\'
    # file_path = 'Z:\\Data02\\Datasets\\Lung_cancer\\SHFK\\SHFK_labels_secondGroup_602GGO\\SHFK_labels_secondGroup_602GGO_siqi\\'
    # gt_postfix = '_CAD_Lung_SYL.json'
    # output_path = 'C:\\Users\\siqi\\Desktop\\ZhongshanValidate\\SHFK\\'
    nodule_add = []
    verified_add = []
    test = SigmaLU_gt_folder_Validate(file_path, gt_postfix, output_path, nodule_add, verified_add)
    test.validate_folder()

