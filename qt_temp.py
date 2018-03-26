# coding:utf-8

from PyQt4.QtGui import QApplication, QCheckBox, QDialog, QGroupBox, QGridLayout, QVBoxLayout
import sys

# overall = [
#     "Atelectasis",
#     "Cardiomegaly",
#     "Effusion",
#     "Infiltration",
#     "Pneumonia",
#     "Pneumothorax",
#     "Consolidation",
#     "Edema",
#     "Emphysema",
#     "Fibrosis",
#     "Pleural_Thickening",
#     "Hernia",
#     "Tuberculosis",
#     "Mass",
#     "Nodule"
# ]


class WinDialog(QDialog):
    def __init__(self, parent=None):
        super(WinDialog, self).__init__(parent)
        self.overall = ["Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Pneumonia", "Pneumothorax",
                   "Consolidation", "Edema", "Emphysema", "Fibrosis", "Pleural_Thickening", "Hernia", "Tuberculosis",
                   "Mass", "Nodule"]
        self.checkboxs = []
        self.set_ui()

    def set_ui(self):
        main_layout = QVBoxLayout()
        group_box = QGroupBox()
        grid = QGridLayout()
        for i, text in enumerate(self.overall):
            checkbox = QCheckBox(text)
            checkbox.setTristate(True)
            # checkbox.setStyleSheet('''QCheckBox::indicator:checked {image: url(D:/GitHub/siyong/images/test.png);}''')
            checkbox.stateChanged.connect(self.state_changed)
            checkbox.setStyleSheet('''::indicator:checked {image: url(D:/GitHub/siyong/images/test.png);}''')
            grid.addWidget(checkbox, i//2, i%2)
            self.checkboxs.append(checkbox)
        group_box.setLayout(grid)
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

    def state_changed(self, state):
        widget = self.sender()
        print(widget)
        print(widget.text())
        print(widget.checkState())
        print(state)

    def get_checked_state(self):
        for checkbox in self.checkboxs:
            print(checkbox.checkState())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = WinDialog()
    dlg.show()
    # dlg.get_checked_state()
    sys.exit(app.exec_())
