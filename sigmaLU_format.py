#!/usr/bin/env python
# coding: utf-8

import pathlib
from subprocess import Popen
from util.sigmaLU_gtValidate import *


class SigmaLUChecker(object):
    """
    sigmaLU checker(use python3)
    """
    def __init__(self, check_exe_path, input_path, output_path=r'D:\sigmaLUchecked', suffix_name='', nodule_add=[], verified_add=[]):
        self.check_exe_path = check_exe_path
        # self.check_script_path = r'D:\GitHub\siyong\exes\format\sigmaLU_gtValidate.py'
        self.input_path = input_path
        self.output_path = output_path
        self.suffix = suffix_name
        self.nodule_add = nodule_add
        self.verified_add = verified_add
        os.makedirs(output_path, exist_ok=True)

    def check_exe(self, input_filename):
        """
        use exe to check
        :param input_filename: json filename
        """
        if pathlib.Path(input_filename).suffix != '.json':
            return
        output_name = str(pathlib.Path(self.output_path, pathlib.Path(input_filename).stem))
        cmd = [self.check_exe_path, input_filename, output_name]
        print(cmd)
        process = Popen(cmd, shell=True)
        process.communicate()

    def gt_validate(self):
        """
        sigmaLU gtValidate
        :param file_dir: 输入文件目录
        :param suffix: 后缀(如'_CAD_zach_cb.json')
        :param output_dir: 输出目录(log)
        :param nodule_add: 额外需要检验的nodule
        :param verified_add: 额外需要检验的verifiedInfo
        """
        # file_path = 'D:\\temp\\ConvertedJsonFiles_changed\\Results1_convertedJson\\G42_Zach_convertedJson\\'
        file_path = self.input_path + '\\'
        # gt_postfix = '_CAD_zach_cb.json'
        gt_postfix = self.suffix
        # output_path = 'D:\\temp\\out1\\'
        output_path = self.output_path + '\\'
        test = SigmaLU_gt_folder_Validate(file_path, gt_postfix, output_path, self.nodule_add, self.verified_add)
        test.validate_folder()

    def check(self, exe_check=True, gt_check=True):
        """
        check a dir
        :param exe_check: 是否使用sigmaLU_format_checker.exe验证
        :param gt_check: 是否使用sigmaLU_gtValidate.py验证
        """
        if exe_check:
            for filename in os.listdir(self.input_path):
                print(self.input_path, filename)
                self.check_exe(str(pathlib.Path(self.input_path, filename)))
        if gt_check:
            self.gt_validate()


if __name__ == '__main__':
    check_exe_path = r'D:\GitHub\siyong\exes\sigmaLU_format_checker.exe'
    # input_path = r'D:\temp\ConvertedJsonFiles_changed\Results1_convertedJson\G42_Zach_convertedJson'
    input_path = r'D:\temp\ConvertedJsonFiles_changed\Results 3_convertedJson'
    output_path = r'D:\sigmaLUchecked'
    suffix_name = '_CAD_zach_cb.json'
    nodule_add = []
    verified_add = []
    checker = SigmaLUChecker(input_path, output_path, suffix_name, nodule_add, verified_add)
    checker.check(exe_check=True, gt_check=True)
