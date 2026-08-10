import sys
import pandas as pd
import matplotlib.pyplot as plt

from PyQt5 import uic,QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QDialog, QHeaderView, QProgressDialog
import os

from crisprmatch.CMlib.show_sampletable import showtable
from crisprmatch.CMlib.show_grouptable import showtable as showgrouptable
from crisprmatch.CMlib.show_result import showtable as showresult
from crisprmatch.CMlib.show_fasta import showfasta
from crisprmatch.analysis import mainprogram
from crisprmatch.resources import ui_path

from subprocess import Popen
from subprocess import PIPE
# from CRISPRMatch import main as startrunning

path = os.getcwd()
qtCreatorFile = ui_path('start.ui')

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)




class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle('CRISPRMatch Start Page')

        # Aquí van los botones
        self.load1btn.clicked.connect(self.getsampleCSV)
        self.load2btn.clicked.connect(self.getgenefa)
        self.load3btn.clicked.connect(self.getgroupCSV)
        self.Show1btn.clicked.connect(self.showsampletable)
        self.Show2btn.clicked.connect(self.showgenefa)
        self.Show3btn.clicked.connect(self.showgrouptable)


        self.tbnin.clicked.connect(self.inputdir)
        self.tbnout.clicked.connect(self.outputdir)

        self.startButton.clicked.connect(self.startrun)
        self.resultButton.clicked.connect(self.showresults)




        self.prosstext = str()  ###step information list
        self.path1 = ""   ###Check loading information
        self.path2 = ""
        self.path3 = ""
        self.path1check = ""
        self.path2check = ""
        self.path3check = ""
        self.outputdirpath = ""
        self.inputdirpath = ""
        self.resultcheck = ""
        self.step = ""




    ##############get sampleCSV and show table#########
    def getsampleCSV(self):
        filePath1, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', path)
        if filePath1 != "":
            print("Direction", filePath1)  # Opcional imprimir la dirección del archivo
            self.dfsample = pd.read_csv(str(filePath1))
            tmp = ' '.join(['load sample information table:',filePath1,';\n'])
            self.prosstext +=tmp
            self.processinfo.setText(self.prosstext)
            self.path1=filePath1

    def showsampletable(self):
        if self.path1 !="":
            self.ui = showtable()  ##打开showtable新窗口
            result = self.ui.setuptable(self.dfsample)  ##传递倒入sample csv
            tmp = ' '.join(['check sample table', ';\n'])
            self.prosstext += tmp
            self.processinfo.setText(self.prosstext)
            if result == "yes":
                self.ui.show()  ##显示窗
                self.path1check = self.path1
            else:
                self.path1check = ""
        else:
            self.showMessageBox('Warning', 'Please load Sample information Table first')
            self.path1=""





    # ##################################################

    # ##############get genefa and show fasta#########
    def getgenefa(self):
        filePath2, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', path)
        if filePath2 != "":
            print("Fasta Direction", filePath2)
            p = open(filePath2,'r')
            self.fafile = p.readlines()
            tmp = ' '.join(['load gene file:', filePath2, ';\n'])
            self.prosstext += tmp
            self.processinfo.setText(self.prosstext)
            self.path2 = filePath2

    def showgenefa(self):
        if self.path2 != "":
            self.ui = showfasta()  ##打开showfasta新窗口
            result=self.ui.setuptext(self.fafile)  ##传递倒入fasta
            tmp = ' '.join(['check gene sequence', ';\n'])
            self.prosstext += tmp
            self.processinfo.setText(self.prosstext)
            if result == "yes":
                self.ui.show()  ##显示窗
                self.path2check = self.path2
            else:
                self.path2check = ""
        else:
            self.showMessageBox('Warning', 'Please load Gene fasta first')
            self.path2=""
    # ##################################################

    # ##############get groupCSV and show table#########
    def getgroupCSV(self):
        filePath3, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', path)
        if filePath3 != "":
            print("Direction", filePath3)  # Opcional imprimir la dirección del archivo
            self.dfgroup = pd.read_csv(str(filePath3))


            stripstr = lambda x: x.strip() if isinstance(x, str) else x  ##去除前后空格
            self.dfgroup = self.dfgroup.applymap(stripstr)


            tmp = ' '.join(['load gene file:', filePath3, ';\n'])
            self.prosstext += tmp
            self.processinfo.setText(self.prosstext)
            self.path3 = filePath3

    def showgrouptable(self):
        if self.path3 != "":
            self.ui = showgrouptable()  ##打开showtable新窗口
            result = self.ui.setuptable(self.dfgroup)  ##传递倒入sample csv
            tmp = ' '.join(['check group table', ';\n'])
            self.prosstext += tmp
            self.processinfo.setText(self.prosstext)
            ###判断格式
            if result == "yes":
                self.ui.show()  ##显示窗
                self.path3check = self.path3
            else:
                self.path3check = ""
        else:
            self.showMessageBox('Warning', 'Please load Group information Table first')
            self.path3 = ""
    ##################################################

    # ##############set input and output file directory#########
    def inputdir(self):
        inputdirpath = QtWidgets.QFileDialog.getExistingDirectory(self,'open directory',path)
        if inputdirpath !="":
            print("Direction", inputdirpath)
            self.inputdirpath = inputdirpath

            self.lineEdit_input.setText(inputdirpath)
            tmp = ' '.join(['input directory:', inputdirpath, ';\n'])
            self.prosstext += tmp
            self.processinfo.setText(self.prosstext)

    def outputdir(self):
        outputdirpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'open directory', path)
        if outputdirpath != "":
            print("Direction", outputdirpath)
            self.outputdirpath = outputdirpath

            self.lineEdit_output.setText(outputdirpath)
            tmp = ' '.join(['output directory:', outputdirpath, ';\n'])
            self.prosstext += tmp
            self.processinfo.setText(self.prosstext)
    ##################################################

    # ############## warning message #########
    def showMessageBox(self, title, message):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()
    ##################################################

    # ############## start running ###################
    def startrun(self):
        if self.path1 != "" and self.path2 != "" and self.path3 != "":
            if self.path1check !="" and self.path2check !="" and self.path3check !="":
                sample = self.path1
                gene = self.path2
                group = self.path3
                input = self.inputdirpath
                self.output_tmp = self.outputdirpath + '/' + 'tmpfiles'
                self.output_result = self.outputdirpath + '/' + 'result'

                #self.ui.startrun(sample, gene, group, input, self.output_tmp, self.output_result)
                mainprogram(sample, gene, group, input, self.output_tmp, self.output_result)


                # x=startrunning(sample,gene,group,input,self.output_tmp,self.output_result)
                # tmp = ' '.join([x, ';\n'])
                # self.prosstext += tmp
                # self.processinfo.setText(self.prosstext)
                # self.step="done"

                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("Information")
                msgBox.setIcon(QtWidgets.QMessageBox.Information)
                msgBox.setText("Project Done!")
                msgBox.setDetailedText("The project has finished, please click ok to show result!")
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Open)

                #msgBox.information(self,"Information","Project Done!")
                # msgBox.addButton("Show Result",QtWidgets.QMessageBox.ActionRole)
                # msgBox.clickedButton()
                msgBox.exec_()
                self.resultcheck = "done"
                self.showresults()
            else:
                self.showMessageBox('Warning', 'Please click show buttons for information checking')
                self.resultcheck = ""
        else:
            self.showMessageBox('Warning', 'Please load information first')
            self.resultcheck = ""

    ##################################################

    # ############## show results ###################
    def showresults(self):
        if self.path1 != "" and self.resultcheck =="done":
            self.ui = showresult()  ##打开showtable新窗口
            self.ui.setuptable(self.dfsample,self.output_tmp,self.output_result,self.path2,self.dfgroup)  ##传递倒入sample csv
            tmp = ' '.join(['check sample table', ';\n'])
            self.prosstext += tmp
            self.processinfo.setText(self.prosstext)
            self.ui.show()  ##显示窗口
        else:
            self.showMessageBox('Warning', 'Please load Sample information Table first')
            self.path1 = ""

        # crispr = path + '/CRISPRMatch.py'
        # cmd = ' '.join(['python',crispr, '-g', gene, '-i', sample, '-gi', group, '-s', output_tmp, '-r', output_result])
        # print(cmd)
        # cmd_run = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        # cmd_run.communicate()
    ##################################################

    # ############## show bar ###################
    def showbarprocess(self):
        if self.step != "done":
            num = int(100000)
            progress = QProgressDialog(self)
            progress.setWindowTitle("请稍等")
            progress.setLabelText("正在操作...")
            # progress.setCancelButtonText("取消")
            progress.setMinimumDuration(5)
            progress.setWindowModality(Qt.WindowModal)
            progress.setRange(0, num)
            for i in range(num):
                progress.setValue(i)
                if progress.wasCanceled():
                    QtWidgets.QMessageBox.warning(self, "提示", "操作失败")
                    break
            else:
                progress.setValue(num)
                #QtWidgets.QMessageBox.information(self, "提示", "操作成功")
            #self.showbarprocess()
        else:
            pass



    #     self.boton2.clicked.connect(self.plot)
    #     self.boton3.clicked.connect(self.showCSV)
    #     self.boton4.clicked.connect(self.show_table)
    #
    #     self.tableWidget.setAlternatingRowColors(True)  # 隔行改变颜色
    #     rown=self.tableWidget.rowCount()  # 返回表格的行数
    #     coln=self.tableWidget.columnCount()  # 返回表格的列数
    #     print(rown)
    #
    #     #self.tableWidget.setHorizontalHeaderLabels('abcdef')  # 设置表格表头数据
    #     # self.tableWidget.setColumnCount(5)  # 设置表格的列数
    #     # self.tableWidget.setRowCount(3)  # 设置表格的行数
    #     # self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)  # 表格设置成大小随内容改变
    #     # self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    #     self.tableWidget.setItem(3, 3, QTableWidgetItem("insert3,3")) # 设置表格内容为字符串"content"
    #     self.timeEdit = QtWidgets.QTimeEdit()  # 创建一个timeEdit
    #     self.tableWidget.setCellWidget(0, 0, self.timeEdit)  # 把timeedit添加进tableWidget内
    #     self.spinBox = QtWidgets.QSpinBox()
    #     self.spinBox.setValue(10)
    #     self.tableWidget.setCellWidget(2, 1, self.spinBox)
    #
    #     ###set tableView
    #     self.model = QStandardItemModel(4,4)
    #     self.model.setHorizontalHeaderLabels(['标题1', '标题2', '标题3', '标题4'])
    #     #下面代码让表格100填满窗口
    #     self.tableView.horizontalHeader().setStretchLastSection(True)
    #     self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    #     for row in range(4):
    #         for column in range(4):
    #             item = QStandardItem("row %s, column %s" % (row, column))
    #             self.model.setItem(row, column, item)
    #     self.tableView.setModel(self.model)
    #     self.model.appendRow([
    #         QStandardItem("row %s, column %s" % (11, 11)),
    #         QStandardItem("row %s, column %s" % (11, 11)),
    #         QStandardItem("row %s, column %s" % (11, 11)),
    #         QStandardItem("row %s, column %s" % (11, 11)),
    #     ])
    #     # 取当前选中的所有行
    #     index = self.tableView.currentIndex()
    #     print(index.row())
    #     self.model.removeRow(index.row())
    #     ###########
    #
    #
    #
    #
    # # Aquí van las nuevas funciones
    # # Esta función abre el archivo CSV
    # def getCSV(self):
    #     filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/Users/qyou/GitLab/pyQttest')
    #     if filePath != "":
    #         print("Dirección", filePath)  # Opcional imprimir la dirección del archivo
    #         self.df = pd.read_csv(str(filePath))
    #
    # def plot(self):
    #     x=self.df['col1']
    #     y=self.df['col2']
    #     plt.plot(x,y)
    #     plt.show()
    #     estad_st="Estadisticas de col2: " +str(self.df['col2'].describe())
    #     self.resultado.setText(estad_st)
    #
    # def showCSV(self):
    #     ###set tableView
    #     rown=len(self.df.index)
    #     coln=len(self.df.columns)
    #     self.model = QStandardItemModel(rown,coln)
    #     labels = list(self.df.columns.values)
    #     #labels=['Index','Sample','Vector','Note','gRNA_PAM','start','end','Type','gene_name']
    #     self.model.setHorizontalHeaderLabels(labels)
    #     #下面代码让表格100填满窗口
    #     # self.tableView_csv.horizontalHeader().setStretchLastSection(True)
    #     # self.tableView_csv.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    #
    #     for row in range(rown):
    #         #print(self.df.loc[row].Sample)
    #         for column in range(len(labels)):
    #             item = QStandardItem(str(self.df.loc[row][labels[column]]))
    #             self.model.setItem(row, column, item)
    #     self.tableView_csv.setModel(self.model)
    #     estad_st=str(self.df)
    #     self.resultado.setText(estad_st)
    # def show_table(self):
    #     #self.showtableWindow = QtWidgets.QDialog()
    #     self.ui = showtable()  ##打开showtable新窗口
    #     self.ui.setuptable(self.df)  ##传递倒入sample csv
    #     self.ui.show()  ##显示窗口





def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
