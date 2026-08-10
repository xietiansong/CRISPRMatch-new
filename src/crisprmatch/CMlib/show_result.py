import sys
import pandas as pd
import matplotlib.pyplot as plt
from crisprmatch.fasta import Fasta

from PyQt5 import uic,QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView, QPushButton
import os
from os import path
import numpy as np
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.backends.qt_compat import QtCore
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from crisprmatch.CMlib.plotfigures import Window
from crisprmatch.CMlib.showprocess import showbarprocess
from crisprmatch.resources import ui_path

pathdir = os.getcwd()
qtCreatorFile = ui_path('show_result.ui')

Ui_showtable, QtBaseClass = uic.loadUiType(qtCreatorFile)

class showtable(QtWidgets.QDialog, Ui_showtable):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_showtable.__init__(self)
        self.setupUi(self)

        self.setWindowTitle('Show Results')
        self.closebtn.clicked.connect(self.sampleEdit)
        print("open result table")

    def setuptable(self,sampleinfo,tmpfile,resultfile,refname,groupinfo):

        self.refname = refname
        self.outputtmp = tmpfile
        self.resulttmp = resultfile

        # #######sample table result#################
        self.df=sampleinfo
        #self.refname = refname

        rown = len(self.df.index)
        coln = len(self.df.columns)
        # self.outputtmp = tmpfile
        # self.resulttmp = resultfile
        self.model = QStandardItemModel(rown, 6)
        # labels = list(self.df.columns.values)
        # rown=len(self.df.index)
        # self.model = QStandardItemModel(rown,9)
        labels=['Index','Sample','Note','Del Ratio','Del Align','SNP Align']
        self.model.setHorizontalHeaderLabels(labels)
        # self.tableView.resize(500,300)
        #下面代码让表格100填满窗口
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tableView.setModel(self.model)

        for row in range(rown):
            #print(self.df.loc[row].Sample)
            for column in range(3):
                item = QStandardItem(str(self.df.loc[row][labels[column]]))
                self.model.setItem(row, column, item)

            start = self.df.loc[row].start
            end = self.df.loc[row].end
            genename = self.df.loc[row].gene_name

            self.tableView.setIndexWidget(self.tableView.model().index(row, 3), self.pushbutton("r%sc%s" % (row, 3), self.df.loc[row].Note, "ratio", start, end, genename))
            self.tableView.setIndexWidget(self.tableView.model().index(row, 4), self.pushbutton("r%sc%s" % (row, 4), self.df.loc[row].Note, "delalign", start, end, genename))
            self.tableView.setIndexWidget(self.tableView.model().index(row, 5), self.pushbutton("r%sc%s" % (row, 5), self.df.loc[row].Note, "snpalign", start, end, genename))
        #############################################

        # #######group table result#################
        self.groupdf = groupinfo.fillna("None") ##填充表格中NaN处
        # groupinfor = groupinfor.fillna("UNKNOWN")  ##填充表格中NaN处
        rown = len(self.groupdf.index)
        coln = len(self.groupdf.columns)
        self.modelgrp = QStandardItemModel(rown, 9)
        # labels = list(self.df.columns.values)
        # rown=len(self.df.index)
        # self.model = QStandardItemModel(rown,9)
        labels = ['group','rep1','rep2','rep3','control','gene','strand','Del Ratio','Del Size']
        self.modelgrp.setHorizontalHeaderLabels(labels)
        # self.tableView.resize(500,300)
        # 下面代码让表格100填满窗口
        self.tableView_grp.horizontalHeader().setStretchLastSection(True)
        self.tableView_grp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_grp.setModel(self.modelgrp)
        for row in range(rown):
            # print(self.df.loc[row].Sample)
            for column in range(7):
                item = QStandardItem(str(self.groupdf.loc[row][labels[column]]))
                self.modelgrp.setItem(row, column, item)
            groupname = self.groupdf.loc[row].group
            rep1 = self.groupdf.loc[row].rep1
            rep2 = self.groupdf.loc[row].rep2
            rep3 = self.groupdf.loc[row].rep3
            ck = self.groupdf.loc[row].control
            strand = self.groupdf.loc[row].strand
            # start = self.df.loc[row].start
            # end = self.df.loc[row].end
            # genename = self.df.loc[row].gene_name
            self.tableView_grp.setIndexWidget(self.tableView_grp.model().index(row, 7), self.pushbutton_grp("gr%sc%s" % (row, 7), "ratio", groupname,rep1,rep2,rep3,ck,strand))
            self.tableView_grp.setIndexWidget(self.tableView_grp.model().index(row, 8), self.pushbutton_grp("gr%sc%s" % (row, 8), "size",groupname,rep1,rep2,rep3,ck,strand))
        #############################################




    def sampleEdit(self):
        self.close() ## 关闭窗口

    def pushbutton(self,content,sample,action, start, end, genename):
        self.content = QPushButton()
        self.content.setText("Get")

        if action == "ratio":
            self.content.clicked.connect(lambda: self.deletion_ratio(sample))
            # pyqt信号和槽传递额外参数
            # 使用个who变量，结果不正常，显示 False is pressed
            # but.clicked.connect(lambda who="5": self.on_click(who))

        # if action == "size":
        #     self.content.clicked.connect(lambda: self.deletion_size(sample))
        if action == "delalign":
            self.content.clicked.connect(lambda: self.deletion_alignment(sample, start, end, genename))
        if action == "snpalign":
            self.content.clicked.connect(lambda: self.snp_alignment(sample, start, end, genename))

        # self.content.clicked.connect(lambda: self.deletion_ratio(sample))
        return self.content

    def pushbutton_grp(self,gcontent,action, groupname,rep1,rep2,rep3,ck,strand):
        self.gcontent = QPushButton()
        self.gcontent.setText("Show")

        if action == "ratio":
            self.gcontent.clicked.connect(lambda: self.deletion_group_ratio(groupname,rep1,rep2,rep3,ck))
            # pyqt信号和槽传递额外参数
            # 使用个who变量，结果不正常，显示 False is pressed
            # but.clicked.connect(lambda who="5": self.on_click(who))

        if action == "size":
            self.gcontent.clicked.connect(lambda: self.deletion_size(groupname))

        # self.content.clicked.connect(lambda: self.deletion_ratio(sample))
        return self.gcontent


    def deletion_ratio(self,sample):
        print(sample)

        graphcsv = os.path.join(self.outputtmp, sample + '.graph.csv')
        pamcsv = os.path.join(self.outputtmp, sample + '.pam.csv')


        if path.exists(graphcsv):

            reg=pd.read_csv(graphcsv,index_col="Index")

            # reg = reg.fillna("None")  ##填充表格中NaN处
            regPAM = pd.read_csv(pamcsv,index_col="Index")

            #####plot deletion ratio
            figures = Window()
            figures.deletion_ratio(sample,reg,regPAM)
            figures.show()



            # #####plot deletion ratio
            # fig, ax = plt.subplots(figsize=(8,6))
            # # if self.strand == '-':
            # #     y=y[::-1]
            # ax.bar(reg.index, reg.ratio, color='blue')
            # ax.set_title(sample,fontdict = {'family': 'Arial'}, size = 15)
            # # print(self.seqlistother)
            # # print(self.seqlistother[1])
            # ax.set_xticks(reg.index,minor=True)
            # ax.set_xticklabels(list(reg.label), color="black", minor=True, fontdict = {'family': 'Arial','weight' : 'bold'}, size = 12)  # minor=True表示次坐标轴
            # ax.set_xticks(regPAM.index)
            # ax.set_xticklabels(regPAM.label, color="red", fontdict = {'family': 'Arial','weight' : 'bold'}, size = 12)
            # plt.ylabel('Deletion Ratio', fontdict = {'family': 'Arial'}, size = 15)
            # plt.show()
        else:
            text= sample + "does not exist!"
            self.showwarnings("warning",text)

    def deletion_group_ratio(self,groupname,rep1,rep2,rep3,ck):
        print(groupname)
        rep1csv = os.path.join(self.outputtmp, rep1 + '.graph.csv')
        rep2csv = os.path.join(self.outputtmp, rep2 + '.graph.csv')
        rep3csv = os.path.join(self.outputtmp, rep3 + '.graph.csv')
        ckcsv = os.path.join(self.outputtmp, ck + '.graph.csv')
        pam1csv = os.path.join(self.outputtmp, rep1 + '.pam.csv')
        pam2csv = os.path.join(self.outputtmp, rep2 + '.pam.csv')
        pam3csv = os.path.join(self.outputtmp, rep3 + '.pam.csv')
        pamckcsv = os.path.join(self.outputtmp, ck + '.pam.csv')
        if (path.exists(rep1csv) and path.exists(rep2csv) and path.exists(rep3csv)):

            #print(repbam1, repbam2, ckbam, start, end, genename, namenow)
            print("There are three repeats!")

            rep1reg = pd.read_csv(rep1csv, index_col="Index")
            rep2reg = pd.read_csv(rep2csv, index_col="Index")
            rep3reg = pd.read_csv(rep3csv, index_col="Index")

            reg = pd.concat([rep1reg.ratio,rep2reg.ratio,rep3reg.ratio], axis=1)
            regmean = reg.mean(axis=1)
            stdrr = reg.sem(axis=1)
            glabels = list(rep1reg.fillna(" ").label) ##填充表格中NaN处

            regPAM = pd.read_csv(pam1csv, index_col="Index")

            if path.exists(ckcsv):
                regck = pd.read_csv(ckcsv, index_col="Index")
                ckname = groupname + ' Control'
                y_ck = regck.ratio
            else:
                ckname = groupname + ' Contron_Unknown'
                regck = regmean
                y_ck = regmean - regmean

            #####plot deletion group ratio
            figures = Window()
            figures.deletion_group_ratio(groupname,regmean,stdrr,glabels,regPAM,regck,y_ck,ckname)
            figures.show()
        elif (path.exists(rep1csv) and path.exists(rep2csv)):

            #print(repbam1, repbam2, ckbam, start, end, genename, namenow)
            print("Rep3 is missing!")

            rep1reg = pd.read_csv(rep1csv, index_col="Index")
            rep2reg = pd.read_csv(rep2csv, index_col="Index")

            reg = pd.concat([rep1reg.ratio,rep2reg.ratio], axis=1)
            regmean = reg.mean(axis=1)
            stdrr = reg.sem(axis=1)
            glabels = list(rep1reg.fillna(" ").label) ##填充表格中NaN处

            regPAM = pd.read_csv(pam1csv, index_col="Index")

            if path.exists(ckcsv):
                regck = pd.read_csv(ckcsv, index_col="Index")
                ckname = groupname + ' Control'
                y_ck = regck.ratio
            else:
                ckname = groupname + ' Contron_Unknown'
                regck = regmean
                y_ck = regmean - regmean

            #####plot deletion group ratio
            figures = Window()
            figures.deletion_group_ratio(groupname,regmean,stdrr,glabels,regPAM,regck,y_ck,ckname)
            figures.show()
        elif (path.exists(rep1csv) and path.exists(rep3csv)):
            print("Rep2 is missing!")

            #print(repbam1, repbam2, ckbam, start, end, genename, namenow)

            rep1reg = pd.read_csv(rep1csv, index_col="Index")
            rep3reg = pd.read_csv(rep3csv, index_col="Index")

            reg = pd.concat([rep1reg.ratio,rep3reg.ratio], axis=1)
            regmean = reg.mean(axis=1)
            stdrr = reg.sem(axis=1)
            glabels = list(rep1reg.fillna(" ").label) ##填充表格中NaN处

            regPAM = pd.read_csv(pam1csv, index_col="Index")

            if path.exists(ckcsv):
                regck = pd.read_csv(ckcsv, index_col="Index")
                ckname = groupname + ' Control'
                y_ck = regck.ratio
            else:
                ckname = groupname + ' Contron_Unknown'
                regck = regmean
                y_ck = regmean - regmean

            #####plot deletion group ratio
            figures = Window()
            figures.deletion_group_ratio(groupname,regmean,stdrr,glabels,regPAM,regck,y_ck,ckname)
            figures.show()
        elif (path.exists(rep2csv) and path.exists(rep3csv)):

            print("Rep1 is missing!")

            #print(repbam1, repbam2, ckbam, start, end, genename, namenow)

            rep2reg = pd.read_csv(rep2csv, index_col="Index")
            rep3reg = pd.read_csv(rep3csv, index_col="Index")

            reg = pd.concat([rep2reg.ratio,rep3reg.ratio], axis=1)
            regmean = reg.mean(axis=1)
            stdrr = reg.sem(axis=1)
            glabels = list(rep2reg.fillna(" ").label) ##填充表格中NaN处

            regPAM = pd.read_csv(pam2csv, index_col="Index")

            if path.exists(ckcsv):
                regck = pd.read_csv(ckcsv, index_col="Index")
                ckname = groupname + ' Control'
                y_ck = regck.ratio
            else:
                ckname = groupname + ' Contron_Unknown'
                regck = regmean
                y_ck = regmean - regmean

            #####plot deletion group ratio
            figures = Window()
            figures.deletion_group_ratio(groupname,regmean,stdrr,glabels,regPAM,regck,y_ck,ckname)
            figures.show()
        elif path.exists(rep1csv):

            #print(repbam1, repbam2, ckbam, start, end, genename, namenow)
            print("Rep2 and Rep3 are missing!")

            rep1reg = pd.read_csv(rep1csv, index_col="Index")

            reg = pd.concat([rep1reg.ratio], axis=1)
            regmean = reg.mean(axis=1)
            stdrr = reg.sem(axis=1)
            glabels = list(rep1reg.fillna(" ").label) ##填充表格中NaN处

            regPAM = pd.read_csv(pam1csv, index_col="Index")

            if path.exists(ckcsv):
                regck = pd.read_csv(ckcsv, index_col="Index")
                ckname = groupname + ' Control'
                y_ck = regck.ratio
            else:
                ckname = groupname + ' Contron_Unknown'
                regck = regmean
                y_ck = regmean - regmean

            #####plot deletion group ratio
            figures = Window()
            figures.deletion_group_ratio(groupname,regmean,stdrr,glabels,regPAM,regck,y_ck,ckname)
            figures.show()
        elif path.exists(rep2csv):

            print("Rep1 and Rep3 are missing!")

            #print(repbam1, repbam2, ckbam, start, end, genename, namenow)

            rep2reg = pd.read_csv(rep2csv, index_col="Index")

            reg = pd.concat([rep2reg.ratio], axis=1)
            regmean = reg.mean(axis=1)
            stdrr = reg.sem(axis=1)
            glabels = list(rep2reg.fillna(" ").label) ##填充表格中NaN处

            regPAM = pd.read_csv(pam1csv, index_col="Index")

            if path.exists(ckcsv):
                regck = pd.read_csv(ckcsv, index_col="Index")
                ckname = groupname + ' Control'
                y_ck = regck.ratio
            else:
                ckname = groupname + ' Contron_Unknown'
                regck = regmean
                y_ck = regmean - regmean

            #####plot deletion group ratio
            figures = Window()
            figures.deletion_group_ratio(groupname,regmean,stdrr,glabels,regPAM,regck,y_ck,ckname)
            figures.show()
        elif path.exists(rep3csv):

            print("Rep1 and Rep2 are missing!")

            #print(repbam1, repbam2, ckbam, start, end, genename, namenow)

            rep3reg = pd.read_csv(rep3csv, index_col="Index")

            reg = pd.concat([rep3reg.ratio], axis=1)
            regmean = reg.mean(axis=1)
            stdrr = reg.sem(axis=1)
            glabels = list(rep3reg.fillna(" ").label) ##填充表格中NaN处

            regPAM = pd.read_csv(pam3csv, index_col="Index")

            if path.exists(ckcsv):
                regck = pd.read_csv(ckcsv, index_col="Index")
                ckname = groupname + ' Control'
                y_ck = regck.ratio
            else:
                ckname = groupname + ' Contron_Unknown'
                regck = regmean
                y_ck = regmean - regmean

            #####plot deletion group ratio
            figures = Window()
            figures.deletion_group_ratio(groupname,regmean,stdrr,glabels,regPAM,regck,y_ck,ckname)
            figures.show()
        else:
            text= "No repeats in "+groupname
            self.showwarnings("warning",text)




    def deletion_size(self,groupname):
        print(groupname)
        csvname = os.path.join(self.resulttmp, groupname + '_deletion_size.csv')
        if path.exists(csvname):

            sizereg = pd.read_csv(csvname)
            # fig, ax = plt.subplots(figsize=(8,6))
            x = np.array(range(1, 22))
            # ymajorFormatter = FormatStrFormatter('%1.1f') ## 设置坐标轴格式
            # ax.yaxis.set_major_formatter(ymajorFormatter)
            # ax.bar(x, sizereg.ratio_mean, color='red')
            # # add errorbar, elinewidth：errorbar line with; capsize/capthick:上下横线长短／粗细，ls:linestyle='None'去掉连接线。 ecolor: errorbar line color
            # ax.errorbar(x, sizereg.ratio_mean, yerr=sizereg.ratio_stdrr, fmt='', elinewidth=0.5, capsize=2, capthick=0.5, ls='None',ecolor='black')
            # ax.set_title(groupname, size=15, fontdict={'family': 'Times New Roman'})
            # ax.set_ylabel('Deletion Size (%)', size=15, fontdict={'family': 'Times New Roman'})
            # ax.set_xticks(x)
            # ax.set_xticklabels(sizereg.Index, rotation=35, fontdict={'family': 'Arial'}, size=12)
            # plt.show()

            #####plot deletion size ratio
            figures = Window()
            figures.deletion_size(groupname, x,sizereg)
            figures.show()

        else:
            text= "No repeats in " + groupname
            self.showwarnings("warning",text)



    def deletion_alignment(self,sample,start, end, genename):
        print(sample)
        fa = Fasta(self.refname)


        delfile= os.path.join(self.resulttmp, sample + '_del_aln.txt')
        pdffile = os.path.join(self.resulttmp, sample + '_del_aln.pdf')

        #print("start output", alnfile, "figure")
        if path.exists(delfile) and os.path.getsize(delfile):  ## check aln file
            print("start output", delfile, "figure")
            tmp = 'Plot '+sample+'_del_aln.pdf'
            showbarprocess(tmp)

            data = pd.read_table(delfile, header=None)  # nrows=400,只读前400行，usecols=(0,1,2,5,6)只提取0，1，2，5，6列
            #    print(len(data.columns)) ##统计列数
            #    print(len(data.index)) ##统计行数
            withset = len(data.columns) * 2 + 10
            heightset = len(data.index) * 2 + 10
            row = len(data.index) - 1 #固定reference sequence
            #    print(withset)
            #    print(heightset)
            fig, ax = plt.subplots()
            fig.set_size_inches(0.01 * withset, 0.01 * heightset)
            #fig.set_size_inches(12, 18)
            ax.set_title(sample, size=2,fontdict={'family': 'sans-serif'})
            ax.set_ylim(0, heightset)
            ax.set_xlim(0, withset)
            ax.set_yticks([])  ##去掉刻度线
            ax.set_xticks([])
            ax.spines['left'].set_visible(False)  ##设置边框可见性 ax.spines['left'].set_linewidth(0)可设置边框粗细
            ax.spines['bottom'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)

            ypos = 5

            for x in data.index:  # 逐行读取txt 序列
                #        print(x,len(data.loc[x]))
                n = 1
                xpos = 5
                ax.text(4, ypos + 1, data.loc[x][0], size=1, horizontalalignment='right', verticalalignment='center', )

                while n < len(data.loc[x]):
                    if (data.loc[x][n] == data.loc[row][n]):
                        if (data.loc[x][n] == "A"):
                            color = "red"
                        elif (data.loc[x][n] == "T"):
                            color = "blue"
                        elif (data.loc[x][n] == "G"):
                            color = "green"
                        elif (data.loc[x][n] == "C"):
                            color = "orange"
                        else:
                            color = "white"
                    # print("n=",n, "data=",data.loc[x][n], "color=", color)
                    else:
                        color = "white"

                    ax.broken_barh([(xpos, 2)], (ypos, 2), facecolors=color, alpha=0.2)
                    ax.text(xpos + 1, ypos + 1, data.loc[x][n], size=1, horizontalalignment='center',
                            verticalalignment='center')
                    n += 1
                    xpos += 2
                ypos += 2
            plt.savefig(pdffile, dpi=300, format="pdf")
            self.showMessageBox("Deletion Alignment","Figure Done. Please click detail button for outputfile",pdffile)
            #plt.show()
            #plt.close(fig)
        else:
            text = sample + "does not exist!"
            self.showwarnings("warning", text)


    def snp_alignment(self,sample,start, end, genename):
        print(sample)
        fa = Fasta(self.refname)


        delfile= os.path.join(self.resulttmp, sample + '_snp_aln.txt')
        pdffile = os.path.join(self.resulttmp, sample + '_snp_aln.pdf')

        #print("start output", alnfile, "figure")
        if path.exists(delfile) and os.path.getsize(delfile):  ## check aln file
            print("start output", delfile, "figure")

            tmp = 'Plot ' + sample + '_snp_aln.pdf'
            showbarprocess(tmp)

            data = pd.read_table(delfile, header=None)  # nrows=400,只读前400行，usecols=(0,1,2,5,6)只提取0，1，2，5，6列
            #    print(len(data.columns)) ##统计列数
            #    print(len(data.index)) ##统计行数
            withset = len(data.columns) * 2 + 10
            heightset = len(data.index) * 2 + 10
            row = len(data.index) - 1 #固定reference sequence
            #    print(withset)
            #    print(heightset)
            fig, ax = plt.subplots()
            fig.set_size_inches(0.01 * withset, 0.01 * heightset)
            #fig.set_size_inches(12, 18)
            ax.set_title(sample, size=2,fontdict={'family': 'sans-serif'})
            ax.set_ylim(0, heightset)
            ax.set_xlim(0, withset)
            ax.set_yticks([])  ##去掉刻度线
            ax.set_xticks([])
            ax.spines['left'].set_visible(False)  ##设置边框可见性 ax.spines['left'].set_linewidth(0)可设置边框粗细
            ax.spines['bottom'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)

            ypos = 5

            for x in data.index:  # 逐行读取txt 序列
                #        print(x,len(data.loc[x]))
                n = 1
                xpos = 5
                ax.text(4, ypos + 1, data.loc[x][0], size=1, horizontalalignment='right', verticalalignment='center', )

                while n < len(data.loc[x]):
                    if (data.loc[x][n] == data.loc[row][n]):
                        if (data.loc[x][n] == "A"):
                            color = "red"
                        elif (data.loc[x][n] == "T"):
                            color = "blue"
                        elif (data.loc[x][n] == "G"):
                            color = "green"
                        elif (data.loc[x][n] == "C"):
                            color = "orange"
                        else:
                            color = "white"
                    # print("n=",n, "data=",data.loc[x][n], "color=", color)
                    else:
                        color = "white"

                    ax.broken_barh([(xpos, 2)], (ypos, 2), facecolors=color, alpha=0.2)
                    ax.text(xpos + 1, ypos + 1, data.loc[x][n], size=1, horizontalalignment='center',
                            verticalalignment='center')
                    n += 1
                    xpos += 2
                ypos += 2
            plt.savefig(pdffile, dpi=300, format="pdf")
            self.showMessageBox("SNP Alignment","Figure Done. Please click detail button for outputfile",pdffile)
            #plt.show()
        else:
            text = sample + "does not exist!"
            self.showwarnings("warning", text)


    def showMessageBox(self, title, message,detail):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setDetailedText(detail)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()

    # ############## warning message #########
    def showwarnings(self, title, message):
        wBox = QtWidgets.QMessageBox()
        wBox.setIcon(QtWidgets.QMessageBox.Warning)
        wBox.setWindowTitle(title)
        wBox.setText(message)
        wBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        wBox.exec_()
    ##################################################


if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    window = showtable()
    window.show()
    sys.exit(app.exec_())
