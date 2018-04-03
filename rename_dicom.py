# coding:utf-8

try:
    from PyQt5.QtWidgets import QDialog, QLabel, QApplication, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, \
        QHBoxLayout, QFileDialog
except:
    from PyQt4.QtGui import QDialog, QLabel, QApplication, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QHBoxLayout, \
        QFileDialog
finally:
    import os
    import sys
    try:
        import dicom
    except ImportError:
        import pydicom as dicom


class renameDlg(QDialog):
    def __init__(self, parent=None):
        super(renameDlg, self).__init__(parent)
        self.setWindowTitle('Rename to description')
        self.setui()

    def setui(self):
        inputFileLabel = QLabel('inputFile')
        self.inputFileLineEdit = QLineEdit()
        inputFileButton = QPushButton('inputFileSelect')
        self.resultLineEdit = QLineEdit()
        startButton = QPushButton('Start')

        select_layout = QHBoxLayout()
        start_layout = QHBoxLayout()
        select_layout.addWidget(inputFileLabel)
        select_layout.addWidget(self.inputFileLineEdit)
        select_layout.addWidget(inputFileButton)
        start_layout.addWidget(self.resultLineEdit)
        start_layout.addWidget(startButton)
        main_layout = QVBoxLayout()
        main_layout.addLayout(select_layout)
        main_layout.addLayout(start_layout)
        self.setLayout(main_layout)

        inputFileButton.clicked.connect(self.inputFileSelect)
        startButton.clicked.connect(self.do)

    def inputFileSelect(self):
        source_absolute_path = QFileDialog.getExistingDirectory(self, 'Open Dir', os.getcwd())
        self.inputFileLineEdit.setText(str(source_absolute_path))
        self.path = str(self.inputFileLineEdit.text())

    def do(self):
        """
        将输入路径下一级的文件夹名字改为PatientsName + StudyDate
        """
        for one_dir in os.listdir(self.path):
            for roots, _, files in os.walk(os.path.join(self.path, one_dir)):
                for filename in files:
                    dcm_file = os.path.join(roots, filename)
                    try:
                        data = dicom.read_file(dcm_file)
                    # except(FileNotFoundError, IOError):  # FileNotFoundError in python3, IOError in python2
                    except:
                        continue
                    patient_name = data.PatientsName
                    study_date = data.StudyDate
                    re_name = '{}_{}'.format(patient_name, study_date)
                    rename_dir = os.path.join(self.path, re_name)
                    old_dir = os.path.join(self.path, one_dir)
                    os.rename(old_dir, rename_dir)
                    print('{} --->> {}'.format(old_dir, rename_dir))
                    break
        self.resultLineEdit.setStyleSheet('color: red')
        self.resultLineEdit.setText(u'转换完毕!')

    # def do(self):
    """
    重命名文件夹名为文件夹名+SeriesDescription
    """
    #     for roots, _, files in os.walk(self.path):
    #         for file in files:
    #             dcm_file = os.path.join(roots, file)
    #             try:
    #                 data = dicom.read_file(dcm_file)
    #             # except(FileNotFoundError, IOError):  # FileNotFoundError in python3, IOError in python2
    #             except:
    #                 continue
    #             series_desc = data.SeriesDescription
    #             prefix, old_name = os.path.split(roots)     # roots.split('\\')
    #             if old_name.endswith(series_desc):
    #                 continue
    #             re_name = '{}_{}'.format(old_name, series_desc)
    #             rename_dir = os.path.join(prefix, re_name)
    #             os.rename(roots, rename_dir)
    #             print('{} --->> {}'.format(roots, rename_dir))
    #     self.resultLineEdit.setStyleSheet('color: red')
    #     self.resultLineEdit.setText(u'转换完毕!')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = renameDlg()
    dlg.show()
    sys.exit(app.exec_())
