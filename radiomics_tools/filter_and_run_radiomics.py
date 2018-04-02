#coding:utf-8

import os
import sys
import json
import shutil
from functools import partial
from PyQt4.QtGui import *
from PyQt4.Qt import *

sys.path.append(r'D:\sigmaUtil')
from radiomicsHandle import run
from radiomics_label import radiomicsFromLabel

def join_duplicate_keys(ordered_pairs):
    """to load duplicate key json"""
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


class MainWindow(QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('12sigma')
        self.nii_source_path = ''
        self.rad_csv_source_path = ''
        self.rad_nii_source_path = ''
        self.rad_label_source_path = ''
        self.rad_json_source_path = ''
        self.filter_checkBoxs = {}
        self.rad_checkBoxs = {}
        self.save_absolute_path = r'D:\ExcelResults'
        self.setui()

    def setui(self):
        group_filter = QGroupBox('Filter')
        group_radiomics = QGroupBox('Radiomics')
        inputFileLabel = QLabel('inputFolder')
        self.inputFileLineEdit = QLineEdit()
        inputFileButton = QPushButton('inputFolderSelect')
        outputFileLabel = QLabel('outputFolder')
        self.outputFileLineEdit = QLineEdit()
        outputFileButton = QPushButton('outputFolderSelect')

        grid_folder = QGridLayout()
        grid_folder.addWidget(inputFileLabel, 0, 0)
        grid_folder.addWidget(self.inputFileLineEdit, 0, 1, 1, 2)
        grid_folder.addWidget(inputFileButton, 0, 3)
        grid_folder.addWidget(outputFileLabel, 1, 0)
        grid_folder.addWidget(self.outputFileLineEdit, 1, 1, 1, 2)
        grid_folder.addWidget(outputFileButton, 1, 3)
        
        grid_check = QGridLayout()
        for i, text in enumerate(["Solid", "GGO", "Mixed", "Calc", "Malign", "P_B", "P_M", "vessel intruder", "vessel connection", "R_B", "R_M"]):
            checkbox = QCheckBox(text)
            grid_check.addWidget(checkbox, i//4, i%4)
            self.filter_checkBoxs[text] = checkbox
        diameterLabel = QLabel('Diameter:')
        self.minLevelLineEdit = QLineEdit()
        separatorLabel = QLabel('-')
        self.maxLevelLineEdit = QLineEdit()
        filterButton = QPushButton('filter')

        self.hintTextEdit = QTextEdit()
        # self.hintTextEdit.setReadOnly(True)
        self.hintTextEdit.setFixedHeight(60)
        self.hintTextEdit.setStyleSheet('color: red')

        # select nii folder
        selectFileLabel = QLabel('SelectFolder(nii)')
        self.selectFileLineEdit = QLineEdit()
        selectFileButton = QPushButton('FolderSelect')
        # select label folder
        label = QLabel('SelectFolder(label)')
        self.selectLabelLineEdit = QLineEdit()
        selectLabelButton = QPushButton('FolderSelect')
        # select json folder
        jsonFileLabel = QLabel('SelectFolder(json)')
        self.selectJsonLineEdit = QLineEdit()
        selectJsonButton = QPushButton('FolderSelect')
        # select save folder
        saveFileLabel = QLabel('saveFolder')
        self.saveFileLineEdit = QLineEdit()
        self.saveFileLineEdit.setText(self.save_absolute_path)
        saveFileButton = QPushButton('saveFolderSelect')
        self.checkbox_wavelet = QCheckBox('applyWavelet')
        self.checkbox_log = QCheckBox('applyLog')
        runButton = QPushButton('run')

        layout_diameter = QHBoxLayout()
        layout_diameter.addWidget(diameterLabel)
        layout_diameter.addWidget(self.minLevelLineEdit)
        layout_diameter.addWidget(separatorLabel)
        layout_diameter.addWidget(self.maxLevelLineEdit)
        layout_diameter.addStretch()
        layout_diameter.addWidget(filterButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(group_filter)
        layout_filter = QVBoxLayout()
        layout_filter.addLayout(grid_folder)
        layout_filter.addLayout(grid_check)
        layout_filter.addLayout(layout_diameter)
        group_filter.setLayout(layout_filter)

        mainLayout.addWidget(self.hintTextEdit)

        mainLayout.addWidget(group_radiomics)
        layout_radiomics = QGridLayout()
        layout_radiomics.addWidget(selectFileLabel, 0, 0)
        layout_radiomics.addWidget(self.selectFileLineEdit, 0, 1, 1, 2)
        layout_radiomics.addWidget(selectFileButton, 0, 3)
        layout_radiomics.addWidget(label, 1, 0)
        layout_radiomics.addWidget(self.selectLabelLineEdit, 1, 1, 1, 2)
        layout_radiomics.addWidget(selectLabelButton, 1, 3)
        layout_radiomics.addWidget(jsonFileLabel, 2, 0)
        layout_radiomics.addWidget(self.selectJsonLineEdit, 2, 1, 1, 2)
        layout_radiomics.addWidget(selectJsonButton, 2, 3)
        layout_radiomics.addWidget(saveFileLabel, 3, 0)
        layout_radiomics.addWidget(self.saveFileLineEdit, 3, 1, 1, 2)
        layout_radiomics.addWidget(saveFileButton, 3, 3)
        # layout_radiomics.addWidget(self.checkbox_wavelet, 4, 0)
        # layout_radiomics.addWidget(self.checkbox_log, 4, 1)
        for i, text in enumerate(["firstorder", "glcm", "shape", "glrlm", "glszm", "applyWavelet", "applyLog"]):
            checkbox = QCheckBox(text)
            layout_radiomics.addWidget(checkbox, 4+i//4, i%4)
            self.rad_checkBoxs[text] = checkbox
        layout_radiomics.addWidget(runButton, 5, 3)
        group_radiomics.setLayout(layout_radiomics)

        self.setLayout(mainLayout)

        inputFileButton.clicked.connect(self.inputFileSelect)
        outputFileButton.clicked.connect(self.outputFileSelect)
        filterButton.clicked.connect(self.filterFiles)
        selectFileButton.clicked.connect(self.inputNiiFileSelect)
        selectLabelButton.clicked.connect(self.inputLabelFileSelect)
        selectJsonButton.clicked.connect(self.inputJsonFileSelect)
        saveFileButton.clicked.connect(self.saveFileSelect)
        runButton.clicked.connect(self.run)
        for edit in [self.inputFileLineEdit, self.outputFileLineEdit, self.selectFileLineEdit, self.selectLabelLineEdit, self.selectJsonLineEdit, self.saveFileLineEdit]:
            edit.textChanged.connect(self.lineEditTextChanged)
            # edit.textChanged.connect(partial(self.lineEditTextChanged, edit))

    def lineEditTextChanged(self, text):
        edit = self.sender()
        if edit is self.inputFileLineEdit:
            self.nii_source_path = str(text)
        elif edit is self.outputFileLineEdit:
            self.rad_csv_source_path = str(text)
        elif edit is self.selectFileLineEdit:
            self.rad_nii_source_path = str(text)
            # self.selectLabelLineEdit.setText('')
        elif edit is self.selectLabelLineEdit:
            self.rad_label_source_path = str(text)
            # self.selectFileLineEdit.setText('')
        elif edit is self.selectJsonLineEdit:
            self.rad_json_source_path = str(text)
        elif edit is self.saveFileLineEdit:
            self.save_absolute_path = str(text)

        if edit is self.selectFileLineEdit and text:
            self.selectLabelLineEdit.setText('')
        if edit is self.selectLabelLineEdit and text:
            self.selectFileLineEdit.setText('')
        # self.selectJsonLineEdit.setText(self.rad_nii_source_path or self.rad_label_source_path)

        for checkbox in self.rad_checkBoxs.values():
            checkbox.setVisible(True)

        if self.rad_nii_source_path:
            for text, checkbox in self.rad_checkBoxs.items():
                if text not in ['applyLog', 'applyWavelet']:
                    checkbox.setVisible(False)
        elif self.rad_label_source_path:
            for text, checkbox in self.rad_checkBoxs.items():
                if text in ['applyLog', 'applyWavelet']:
                    checkbox.setVisible(False)

    def run(self):
        features = []
        for text, checkbox in self.rad_checkBoxs.items():
            if checkbox.isChecked():
                features.append(text)
        if not self.rad_nii_source_path and not self.rad_label_source_path or not self.rad_json_source_path:
            print('no source_path!!')
            self.printMsg(' no source_path!!\n Please Select Folder to Run Radiomics', 'red')
            return
        if self.rad_nii_source_path:
            applyLog = 'applyLog' in features
            applyWavelet = 'applyWavelet' in features
            niis_in_current_file = [f for f in os.listdir(self.rad_nii_source_path) if f.endswith('.nii')]
            for json_file in os.listdir(self.rad_json_source_path):
                if not json_file.endswith('.json') or 'CAD_Lung' not in json_file:
                    continue
                nii_name = '{}.nii'.format(json_file.split('_CAD_Lung')[0])
                nii_file = os.path.join(self.rad_nii_source_path, nii_name) if nii_name in niis_in_current_file else os.path.join(self.nii_source_path, nii_name)
                # 如果两个文件夹都不存在，需要处理异常
                self.printMsg('nii file: {}'.format(nii_file))
                if not os.path.exists(nii_file):
                    continue
                # self.save_absolute_path
                if not os.path.exists(r'D:\ExcelResults'):
                    os.makedirs(r'D:\ExcelResults')
                json_file = os.path.join(self.rad_json_source_path, json_file)
                self.printMsg('json File: {}'.format(json_file))
                self.printMsg('run radiomics...')
                print(nii_file, json_file, self.rad_json_source_path, self.save_absolute_path or r'D:\ExcelResults', applyLog, applyWavelet)
                try:
                    run(nii_file, json_file, self.rad_json_source_path, self.save_absolute_path or r'D:\ExcelResults', re_divide=1, applyLog=applyLog, applyWavelet=applyWavelet)
                    print(1111)
                except RuntimeError:
                    try:
                        run(nii_file, json_file, self.rad_json_source_path, self.save_absolute_path or r'D:\ExcelResults',
                            re_divide=2, applyLog=applyLog, applyWavelet=applyWavelet)
                        print(2222)
                    except RuntimeError:
                        try:
                            run(nii_file, json_file, self.rad_json_source_path,
                                self.save_absolute_path or r'D:\ExcelResults', re_divide=4, applyLog=applyLog,
                                applyWavelet=applyWavelet)
                            print(33333)
                        except RuntimeError:
                            pass
                # 如果保存路径未选择，默认路径'D:\ExcelResults'不存在会报错么？？？   会
                self.printMsg('Finish!')
                self.printMsg('-' * 50)
        else:
            radiomics = radiomicsFromLabel()
            currentFilePath = self.rad_json_source_path
            settings = {'binWidth': 25, 'symmetricalGLCM': True}
            enabledImageTypes = {"Original": {}, "Wavelet": {}}
            niiFileList = [x for x in os.listdir(currentFilePath) if os.path.isfile(os.path.join(currentFilePath, x)) and os.path.splitext(x)[-1]=='.nii' and "label" not in x]
            for niiFile in niiFileList:
                print("niiFile = {}".format(niiFile))
                name, _ = os.path.splitext(niiFile)
                labelFile = name + "-label"
                labelImgFile = os.path.join(currentFilePath, labelFile)
                niiImgFile = os.path.join(currentFilePath, niiFile)
                csvFile = os.path.join(currentFilePath, name + "_radiomics.csv")
                if os.path.exists(csvFile):
                    continue
                radiomics.run(niiImgFile, labelImgFile, features, settings, enabledImageTypes, csvFile)

    def printMsg(self, message, color='black'):
        self.hintTextEdit.setStyleSheet('color: {}'.format(color))
        self.hintTextEdit.append(message)

    def inputFileSelect(self):
        nii_source_path = QFileDialog.getExistingDirectory(self, 'Open Dir', os.getcwd())
        self.nii_source_path = str(nii_source_path)
        self.inputFileLineEdit.setText(self.nii_source_path)

    def outputFileSelect(self):
        rad_csv_source_path = QFileDialog.getExistingDirectory(self, 'Open Dir', os.getcwd())
        self.rad_csv_source_path = str(rad_csv_source_path)
        self.outputFileLineEdit.setText(self.rad_csv_source_path)
        self.selectFileLineEdit.setText(self.rad_csv_source_path)
        self.selectJsonLineEdit.setText(self.rad_csv_source_path)

    def inputNiiFileSelect(self):
        rad_nii_source_path = QFileDialog.getExistingDirectory(self, 'Open Dir', os.getcwd())
        self.rad_nii_source_path = str(rad_nii_source_path)
        self.selectFileLineEdit.setText(self.rad_nii_source_path)
        self.selectJsonLineEdit.setText(self.rad_nii_source_path)

    def inputLabelFileSelect(self):
        rad_label_source_path = QFileDialog.getExistingDirectory(self, 'Open Dir', os.getcwd())
        self.rad_label_source_path = str(rad_label_source_path)
        self.selectLabelLineEdit.setText(self.rad_label_source_path)
        self.selectJsonLineEdit.setText(self.rad_label_source_path)

    def inputJsonFileSelect(self):
        rad_json_source_path = QFileDialog.getExistingDirectory(self, 'Open Dir', os.getcwd())
        self.rad_json_source_path = str(rad_json_source_path)
        self.selectJsonLineEdit.setText(self.rad_json_source_path)

    def saveFileSelect(self):
        save_absolute_path = QFileDialog.getExistingDirectory(self, 'Open Dir', os.getcwd())
        self.save_absolute_path = str(save_absolute_path)
        self.saveFileLineEdit.setText(self.save_absolute_path)

    def filterFiles(self):
        print('start...')
        if not self.nii_source_path or not self.rad_csv_source_path:
            # pop-up a messagebox
            # QMessageBox.warning('Please select Folders!!', QMessageBox.Yes|QMessageBox.No)
            self.printMsg('Please Select inputFolder and outputFolder!!', 'red')
            return
        jsons = [f for f in os.listdir(self.nii_source_path) if 'CAD_Lung' in f]
        # jsons = [f for f in os.listdir(self.nii_source_path) if 'CAD_Ziwei' in f]
        for json_file in jsons:
            source_file = os.path.join(self.nii_source_path, json_file)
            out_file = os.path.join(self.rad_csv_source_path, json_file)
            shutil.copy(source_file, out_file)
            # delete items not satisfied
            if not self.getSatifiedResult(out_file):
                print('not satisfied!!')
                os.remove(out_file)
                # pass
            else:
                print('move file >>> {}'.format(out_file))
                self.printMsg('move file {}'.format(json_file))
                nodules = self.getSatifiedResult(out_file)
                dump_duplicate_json(nodules, out_file)
                self.printMsg('-' * 50)

    def getSatifiedResult(self, filename):
        min_val, max_val, checked_list = self.selectedValues()
        origin = load_duplicate_json(filename)
        nodules = origin.get('Nodules', {})
        items = nodules.get('item', [])
        if isinstance(items, dict):
            items = [items]
        new_items = []
        for item in items:
            verified = item.get('VerifiedNodule', {})
            D2 = float(item.get('EllipsoidRadius2')) * 2 or 3.0
            if D2 <= max_val and D2 >= min_val:
                if not checked_list:
                    new_items.append(item)
                elif any([verified.get(checked, 'false') == 'true' for checked in checked_list]):
                    new_items.append(item)
        count = len(new_items)
        if not count:
            return False
        new_nodules = {'Nodules': {'item': new_items}}
        new_nodules['AdditionalDiseases'] = origin.get('AdditionalDiseases', {})
        new_nodules['labelVersion'] = origin.get('labelVersion')
        new_nodules['version'] = origin.get('version')
        new_nodules['count'] = count
        return new_nodules

    def selectedValues(self):
        """requires that user select"""
        list_selected = []
        minLevel = float(self.minLevelLineEdit.text() or 0)
        maxLevel = float(self.maxLevelLineEdit.text() or 99)
        for text, checkbox in self.filter_checkBoxs.items():
            if checkbox.isChecked():
                list_selected.append(text)
        print(minLevel, maxLevel, list_selected)
        return minLevel, maxLevel, list_selected


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


def load_duplicate_json(filename):
    with open(filename) as fp:
        data = json.load(fp, object_pairs_hook=join_duplicate_keys)
        return data


def dump_duplicate_json(obj, filename):
    print(1111)
    for k, v in DuplicateDict(obj).items():
        print(k, ":", v)
    json_str = pretty_json(json.dumps(DuplicateDict(obj), ensure_ascii=False).encode('utf-8'))
    with open(filename, 'w') as fp:
        fp.write(json_str)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
