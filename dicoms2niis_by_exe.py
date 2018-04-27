# coding:utf-8

import os
try:
    import dicom
except ImportError:
    import pydicom as dicom
from subprocess import Popen
from pathlib import Path
from datetime import datetime


def dicoms2niis(exe_path, source_path, out_path):
    """
    Convert dicoms to nii(use dcm2niiConverterX.exe)
    :param exe_path: where the exe in
    :param source_path: dicom dir
    :param out_path: output dir for niis
    """
    Path(out_path).mkdir(exist_ok=True)
    last_dicom_dir = ''
    failed_dcms = []
    # pre_analysis(source_path)
    for roots, _, files in os.walk(source_path):
        for dcm_file in files:
            if Path(dcm_file).suffix in ['.dat', '.cfg']:
                continue
            # nii_prefix = roots.replace(source_path + '\\', '').split('\\')[0]
            # nii_postfix = roots.split('\\')[-1]
            # nii_name = nii_prefix + '_' + nii_postfix
            # nii_name = Path(roots).name          # 'E:/肺结节CAD测试影像/GE50/0024' --> 0024

            ###### source下一级文件名 + ScanTime
            # nii_prefix = Path(roots).relative_to(Path(source_path)).parents[0]
            # try:
            #     data = dicom.read_file(str(Path(roots, dcm_file)))
            # # except(FileNotFoundError, IOError):  # FileNotFoundError in python3, IOError in python2
            # except:
            #     failed_dcms.append(os.path.join(roots, dcm_file))
            #     continue
            # study_date = data.StudyDate
            # nii_name = "{}_{}".format(nii_prefix, study_date)

            ######
            # dcm_file_abspath = Path(roots, dcm_file)
            # nii_name = '{}_{}'.format(dcm_file_abspath.parts[-3], dcm_file_abspath.parts[-2].split('_')[-1])

            ###### BJCH CT0611_Z1_250MM_20121116151936.nii
            try:
                data = dicom.read_file(str(Path(roots, dcm_file)))
            # except(FileNotFoundError, IOError):  # FileNotFoundError in python3, IOError in python2
            except:
                failed_dcms.append(os.path.join(roots, dcm_file))
                continue
            try:
                slice_thickness = int(data[0x0018, 0x0050].value)    # slice_thickness = data.SlicerThickness
            except KeyError:
                slice_thickness = ''
            study_date = data.StudyDate
            nii_prefix = Path(roots).relative_to(Path(source_path)).parents[0]
            nii_name = '{}_{}MM_{}'.format(nii_prefix, slice_thickness, study_date)

            if roots == last_dicom_dir:
                continue
            # print('###########################nii_prefix = {}, study_date = {}'.format(nii_prefix, study_date))

            #### PatientName + ScanTime
            # try:
            #     data = dicom.read_file(str(Path(roots, dcm_file)))
            # # except(FileNotFoundError, IOError):  # FileNotFoundError in python3, IOError in python2
            # except:
            #     failed_dcms.append(os.path.join(roots, dcm_file))
            #     continue
            # patient_name = data.PatientsName
            # study_date = data.StudyDate
            # nii_name = '{}_{}'.format(patient_name, study_date)

            last_dicom_dir = roots
            print(nii_name + '.nii')
            # cmd = [exe_path, roots, out_path, r'{}_%t'.format(nii_name)]
            cmd = [exe_path, roots, out_path, nii_name]
            process = Popen(cmd, shell=True)
            process.communicate()
    print(failed_dcms)

def pre_analysis(source_path):
    """
    通过AcquisitionDateTime, 来判断平扫和增强, 重命名文件夹(plain/enhanced)
    """
    for name_folder in os.listdir(source_path):
        pe_list = []
        for pe_folder in os.listdir(str(Path(source_path, name_folder))):
            pe_folder_abspath = Path(source_path, name_folder, pe_folder)
            if not pe_folder_abspath.is_dir():
                continue
            for dcm_file in os.listdir(str(pe_folder_abspath)):
                dcm_file_abspath = Path(pe_folder_abspath, dcm_file)
                try:
                    data = dicom.read_file(str(dcm_file_abspath))
                    # except(FileNotFoundError, IOError):  # FileNotFoundError in python3, IOError in python2
                except:
                    continue
                else:
                    try:
                        ac_time = data.AcquisitionDateTime
                    except AttributeError:
                        ac_time = '{}{}'.format(data.AcquisitionDate, data.AcquisitionTime)
                    dt_time = datetime.strptime(ac_time, '%Y%m%d%H%M%S.%f')
                    pe_list.append((pe_folder_abspath, dt_time))     # (目录名, 扫描时间)
                    break
        print(pe_list)
        if len(pe_list) != 2:
            continue
        dir1, time1 = pe_list[0]
        dir2, time2 = pe_list[1]
        if time1 < time2:
            os.rename(str(dir1), str('{}_plain'.format(dir1)))
            os.rename(str(dir2), str('{}_enhanced'.format(dir2)))
        else:
            os.rename(str(dir2), str('{}_plain'.format(dir2)))
            os.rename(str(dir1), str('{}_enhanced'.format(dir1)))


if __name__ == '__main__':
    # dicoms2niis(r'D:\GitHub\siyong\exes\dcm2niiConverterX.exe', r'E:\肺结节CAD测试影像', r'E:\肺结节CAD测试影像_niis')
    # dicoms2niis(r'D:\GitHub\siyong\exes\dcm2niiConverterX.exe', r'F:\聊城二院', r'F:\聊城二院_niis')
    dicoms2niis(r'D:\GitHub\siyong\exes\dcm2niiConverterX.exe', r'E:\test', r'E:\niis')
