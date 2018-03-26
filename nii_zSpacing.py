# coding:utf-8

import nibabel as nib
import os
import shutil


def do(source_folder, out_folder):
    """
    filter nii and xml by zSpacing(Thickness)\n
    :param source_folder: source folder to filter
    :param out_folder: output folder for satisfied nii and xml
    :return:
    """
    for roots, _, files in os.walk(source_folder):
        for filename in files:
            if filename.endswith('.nii'):
                nii_filename = os.path.join(roots, filename)
                img_data =nib.load(nii_filename)
                zSpacing = img_data.affine[2][2]
                print(zSpacing)
                if zSpacing < 1:
                    name = '.'.join(filename.split('.')[:-1])
                    xml_name = '{}.xml'.format(name)
                    xml_filename = os.path.join(roots, xml_name)
                    if os.path.exists(xml_filename):
                        print(xml_filename)
                        # TODO move xml
                        shutil.move(xml_filename, os.path.join(out_folder, xml_name))
                        # shutil.copy(xml_filename, os.path.join(out_folder, xml_name))
                    print(nii_filename)
                    # TODO move nii
                    # shutil.move(nii_filename, os.path.join(out_folder, '{}.nii'.format(name)))
                    # shutil.copy(nii_filename, os.path.join(out_folder, '{}.nii'.format(name)))


if __name__ == '__main__':
    do(r'E:\SHZS_CT03', r'E:\SHZS_lt1')
    # do(r'E:\111', r'E:\test')
