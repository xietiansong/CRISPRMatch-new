import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
import random
from os import path
import pandas as pd
import numpy as np
import os


class Changecolor(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Changecolor, self).__init__(parent)




    def deletion_ratio(self,sample,reg,regPAM,colorstring):

        self.color = colorstring


        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        glabels = list(reg.fillna(" ").label)

        self.ax = self.figure.add_subplot(111)
        self.ax.bar(reg.index, reg.ratio, color =self.color.name())
        self.ax.set_title(sample,fontdict = {'family': 'Arial'}, size = 15)
        # print(self.seqlistother)
        # print(self.seqlistother[1])
        self.ax.set_xticks(reg.index,minor=True)
        self.ax.set_xticklabels(glabels, color="black", minor=True, fontdict = {'family': 'Arial','weight' : 'bold'}, size = 12)  # minor=True表示次坐标轴
        self.ax.set_xticks(regPAM.index)
        self.ax.set_xticklabels(regPAM.label, color="red", fontdict = {'family': 'Arial','weight' : 'bold'}, size = 12)
        plt.ylabel('Deletion Ratio', fontdict = {'family': 'Arial'}, size = 15)
        self.setLayout(self.layout)
        self.show()

    def deletion_group_ratio(self, groupname, regmean, stdrr, glabels, regPAM, regck, y_ck, ckname, colorstring):
        print(groupname)

        self.color = colorstring


        self.figure = plt.figure(figsize=(16, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        self.ax0 = self.figure.add_subplot(1, 2, 1)
        y = regmean
        y_std = stdrr
        self.ax0.bar(regmean.index, y, color=self.color.name())
        # add errorbar, elinewidth：errorbar line with; capsize/capthick:上下横线长短／粗细，ls:linestyle='None'去掉连接线。 ecolor: errorbar line color
        self.ax0.errorbar(regmean.index, y, yerr=y_std, fmt='', elinewidth=0.5, capsize=2, capthick=0.5, ls='None',
                          ecolor='black')
        self.ax0.set_title(groupname, fontdict={'family': 'Times New Roman'}, size=15)

        self.ax0.set_xticks(regmean.index, minor=True)
        self.ax0.set_xticklabels(glabels, color="black", minor=True, fontdict={'family': 'Arial', 'weight': 'bold'},
                                 size=12)  # minor=True表示次坐标轴
        self.ax0.set_xticks(regPAM.index)
        self.ax0.set_xticklabels(regPAM.label, color="red", fontdict={'family': 'Arial', 'weight': 'bold'}, size=12)

        self.ax0.set_ylabel('Deletion Ratio', fontdict={'family': 'Times New Roman'}, size=15)

        self.ax1 = self.figure.add_subplot(1, 2, 2)
        v = self.ax0.axis()  ##返回子图1的坐标范围
        self.ax1.axis(v)  ##设置子图2的坐标范围

        self.ax1.bar(regck.index, y_ck, color='grey')
        self.ax1.set_title(ckname, fontdict={'family': 'Times New Roman'}, size=15)
        self.ax1.set_xticks(regck.index, minor=True)
        self.ax1.set_xticklabels(glabels, color="black", minor=True, fontdict={'family': 'Arial', 'weight': 'bold'},
                                 size=12)
        self.ax1.set_xticks(regPAM.index)
        self.ax1.set_xticklabels(regPAM.label, color="red", fontdict={'family': 'Arial', 'weight': 'bold'}, size=12)

        self.setLayout(self.layout)
        self.show()

    def deletion_size(self, groupname, x, sizereg,colorstring):

        self.color = colorstring


        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)


        self.ax = self.figure.add_subplot(111)
        ymajorFormatter = FormatStrFormatter('%1.1f')  ## 设置坐标轴格式
        self.ax.yaxis.set_major_formatter(ymajorFormatter)
        self.ax.bar(x, sizereg.ratio_mean, color=self.color.name())
        # add errorbar, elinewidth：errorbar line with; capsize/capthick:上下横线长短／粗细，ls:linestyle='None'去掉连接线。 ecolor: errorbar line color
        self.ax.errorbar(x, sizereg.ratio_mean, yerr=sizereg.ratio_stdrr, fmt='', elinewidth=0.5, capsize=2,
                         capthick=0.5, ls='None', ecolor='black')
        self.ax.set_title(groupname, size=15, fontdict={'family': 'Times New Roman'})
        self.ax.set_ylabel('Deletion Size (%)', size=15, fontdict={'family': 'Times New Roman'})
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(sizereg.Index, rotation=35, fontdict={'family': 'Arial'}, size=12)

        self.setLayout(self.layout)
        self.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Changecolor()
    main.setWindowTitle('Change Color Window')
    main.show()
    sys.exit(app.exec_())