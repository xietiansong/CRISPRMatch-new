from PyQt5.QtWidgets import QHeaderView, QPushButton,QProgressDialog
from PyQt5.QtCore import Qt

def showbarprocess(content):
    num = int(100000)
    progress = QProgressDialog()
    progress.setWindowTitle("Please waiting")
    progress.setLabelText(content)
    progress.setCancelButton(None)  ##不显示cancel button
    #progress.setCancelButtonText("")
    progress.setMinimumDuration(5)
    progress.setWindowModality(Qt.WindowModal)
    progress.setRange(0, num)
    for i in range(num):
        progress.setValue(i)

    else:
        progress.setValue(num)