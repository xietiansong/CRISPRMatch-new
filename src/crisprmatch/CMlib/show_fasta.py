import sys

from PyQt5 import uic,QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView
import os
from crisprmatch.resources import ui_path

path = os.getcwd()
qtCreatorFile = ui_path('show_fasta.ui')

Ui_showfasta, QtBaseClass = uic.loadUiType(qtCreatorFile)

class showfasta(QtWidgets.QDialog, Ui_showfasta):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_showfasta.__init__(self)
        self.setupUi(self)

        self.setWindowTitle('Gene Sequence')
        self.checkbtn.clicked.connect(self.sampleEdit)
        print("open gene fasta")

    def setuptext(self,fasta):

        self.fasta=fasta
        if '>' in self.fasta[0]:
            self.string=str()
            for i in self.fasta:
                self.string +=str(i)
                self.textEdit.setText(self.string)
            return "yes"
        else:
            self.showMessageBox("warning", "This is not a Fasta file")
            return "wrong"
        # rown = len(self.df.index)
        # coln = len(self.df.columns)
        # self.model = QStandardItemModel(rown, 8)
        # # labels = list(self.df.columns.values)
        # # rown=len(self.df.index)
        # # self.model = QStandardItemModel(rown,9)
        # labels=['group','rep1','rep2','control','gene','strand','start','end']
        # self.model.setHorizontalHeaderLabels(labels)
        # # self.tableView.resize(500,300)
        # #下面代码让表格100填满窗口
        # self.tableView.horizontalHeader().setStretchLastSection(True)
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #
        # for row in range(rown):
        #     #print(self.df.loc[row].Sample)
        #     for column in range(8):
        #         item = QStandardItem(str(self.df.loc[row][labels[column]]))
        #         self.model.setItem(row, column, item)
        #
        # self.tableView.setModel(self.model)

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
    window = showfasta()
    window.show()
    sys.exit(app.exec_())
