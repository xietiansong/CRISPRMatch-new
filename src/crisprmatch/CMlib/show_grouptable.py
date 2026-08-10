import sys
import pandas as pd
import matplotlib.pyplot as plt

from PyQt5 import uic,QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView
import os
from crisprmatch.resources import ui_path

path = os.getcwd()
qtCreatorFile = ui_path('show_sampletable.ui')

Ui_showtable, QtBaseClass = uic.loadUiType(qtCreatorFile)

class showtable(QtWidgets.QDialog, Ui_showtable):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_showtable.__init__(self)
        self.setupUi(self)

        self.setWindowTitle('Group Information Table')
        self.checkbtn.clicked.connect(self.sampleEdit)
        print("open group table")

    def setuptable(self,pd):

        self.df = pd
        self.df = self.df.fillna("None")
        rown = len(self.df.index)
        coln = len(self.df.columns)
        self.model = QStandardItemModel(rown, 9)
        # labels = list(self.df.columns.values)
        # rown=len(self.df.index)
        # self.model = QStandardItemModel(rown,9)

        labels=['group','rep1','rep2','rep3','control','gene','strand','start','end']
        ###判断格式
        if list(self.df.columns.values) != labels:
            self.showMessageBox("warning","wrong table!")
            return "wrong"
        else:

            self.model.setHorizontalHeaderLabels(labels)
            # self.tableView.resize(500,300)
            #下面代码让表格100填满窗口
            self.tableView.horizontalHeader().setStretchLastSection(True)
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row in range(rown):
                #print(self.df.loc[row].Sample)
                for column in range(9):
                    item = QStandardItem(str(self.df.loc[row][labels[column]]))
                    self.model.setItem(row, column, item)

            self.tableView.setModel(self.model)
            return "yes"

    def sampleEdit(self):
        self.close() ## 关闭窗口
    # ############## warning message #########
    def showMessageBox(self, title, message):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()
    ##################################################




if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    window = showtable()
    window.show()
    sys.exit(app.exec_())
