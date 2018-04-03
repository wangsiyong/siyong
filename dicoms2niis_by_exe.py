# coding:utf-8

import os
from subprocess import Popen
from pathlib import Path


def dicoms2niis(exe_path, source_path, out_path):
    """
    Convert dicoms to nii(use dcm2niiConverterX.exe)
    :param exe_path: where the exe in
    :param source_path: dicom dir
    :param out_path: output dir for niis
    """
    last_dicom_dir = ''
    for roots, _, files in os.walk(source_path):
        for _ in files:
            # nii_prefix = roots.replace(source_path + '\\', '').split('\\')[0]
            # nii_postfix = roots.split('\\')[-1]
            # nii_name = nii_prefix + '_' + nii_postfix
            nii_name = Path(roots).name          # 'E:/肺结节CAD测试影像/GE50/0024' --> 0024
            if roots == last_dicom_dir:
                continue
            last_dicom_dir = roots
            print(nii_name + '.nii')
            cmd = [exe_path, roots, out_path, nii_name]
            process = Popen(cmd, shell=True)
            process.communicate()


if __name__ == '__main__':
    dicoms2niis(r'D:\GitHub\siyong\exes\dcm2niiConverterX.exe', r'E:\肺结节CAD测试影像', r'E:\肺结节CAD测试影像_niis')
