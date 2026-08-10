import os, sys
import pysam
from crisprmatch.fasta import Fasta
import matplotlib
from scipy import stats
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets



def caldel(samfilename, start, end, genename, filter):
    """

    :param samfilename: path and name of each bam file
    :param start: setting the start site of deletion calculation
    :param end: setting the end site of deletion calculation
    :param genename: the name of genome-editing target region
    :return:
    """
    n = 0

    mutateinfor = dict()

    deletelent = dict()
    samfile = pysam.AlignmentFile(samfilename, 'r')
    for read in samfile.fetch(genename):

        # print(read.cigartuples, read.cigarstring, read.reference_start, read.cigartuples[0][1], read.cigartuples[0][1]+read.reference_start)


        nowsite = read.reference_start
        #     print(read.cigarstring)
        for cigarnow in read.cigartuples:
            # print(cigarnow)
            cigartype = cigarnow[0]
            #         print(cigartype)
            cigarlenght = cigarnow[1]

            cigarend = nowsite + cigarlenght

            if start < nowsite < end:

                if cigartype == 2:

                    if cigarlenght < (end - start):

                        if cigarlenght in deletelent:

                            deletelent[cigarlenght] += 1
                        else:
                            deletelent[cigarlenght] = 1

            for i in range(nowsite, cigarend):

                if i in mutateinfor:

                    if cigartype in mutateinfor[i]:

                        mutateinfor[i][cigartype] += 1

                    else:

                        mutateinfor[i][cigartype] = 1

                else:

                    mutateinfor[i] = dict()

                    mutateinfor[i][cigartype] = 1

            nowsite += cigarlenght

        n += 1

    mutateinforpd = pd.DataFrame.from_dict(mutateinfor, orient='index').fillna(value=0)
    mutateinforpd['sum'] = mutateinforpd.sum(axis=1)
    #    print(mutateinforpd[2],mutateinforpd['sum'])
    mutateinforpd['delrate'] = mutateinforpd[2]/(mutateinforpd['sum']-filter) * 100
    deletelentpd = pd.DataFrame.from_dict(deletelent, orient='index')

    return (mutateinforpd, deletelentpd)

def barchart_filter(infofile,groupinfo,refname, output, bamdir):
    """

    :param infofile: a description file of details of each sample, example: sample_infor.txt
    :param groupinfo: a description file of details of each group, example: group_infor.txt
    :param refname:  a fasta format of the sequence in the target region, exaple:Samples_gene.fa
    :param output: folder of final result
    :param bamdir: folder of temporary files
    :return:
    """
    datainfo = pd.read_csv(infofile, index_col="Index")
    groupinfor = pd.read_csv(groupinfo)
    filterfile = os.path.join(output, 'filter_wt_reads_number.txt')
    filterinfor= pd.read_table(filterfile)
    stranddict = dict()
    filter_dict = dict()
    for idz in filterinfor.index:
        filter_dict[filterinfor.loc[idz]['Sample']] = filterinfor.loc[idz]['filter']

    for idy in groupinfor.index:
        stranddict[groupinfor.loc[idy].rep1] = groupinfor.loc[idy].strand
        stranddict[groupinfor.loc[idy].rep2] = groupinfor.loc[idy].strand
        stranddict[groupinfor.loc[idy].rep3] = groupinfor.loc[idy].strand
        stranddict[groupinfor.loc[idy].control] = groupinfor.loc[idy].strand
    fa = Fasta(refname)
    for idx in datainfo.index:
        note = datainfo.loc[idx].Note

        if note not in stranddict:
            error = ' '.join([note, 'is not involved in group table! Please Check!'])
            showwarnings("Error", error)
            continue

        strand = stranddict[note]
        type = ''
        if (re.search("gRNA", datainfo.loc[idx].Note)):
            if strand == '+':
                start = datainfo.loc[idx]['start'] - 10
                end = datainfo.loc[idx]['end'] + 10
                type = "gf"
            else:
                start = datainfo.loc[idx]['start'] - 10
                end = datainfo.loc[idx]['end'] + 10
                type = "gr"
        elif (re.search("crRNA", datainfo.loc[idx].Note)):
            if strand == '+':
                start = datainfo.loc[idx]['start'] - 10
                end = datainfo.loc[idx]['end'] + 30
                type = "cf"
            else:
                start = datainfo.loc[idx]['start'] - 30
                end = datainfo.loc[idx]['end'] + 10
                type = "cr"
        # if (re.search("gRNA", datainfo.loc[idx].Note)):
        #     start = datainfo.loc[idx].start - 10
        #     end = datainfo.loc[idx].end + 10
        # elif (re.search("crRNA", datainfo.loc[idx].Note)):
        #     start = datainfo.loc[idx].start
        #     end = datainfo.loc[idx].end + 30
        #print(start, end)
        bamfile = os.path.join(bamdir, note + '.bam')
        pdffile = os.path.join(output, note + '.pdf')
        graphcsv= os.path.join(bamdir,note + '.graph.csv')
        pamcsv = os.path.join(bamdir, note + '.pam.csv')


        #print(bamfile)
        genename = datainfo.loc[idx].gene_name
        seq = fa[genename][start - 1:end].upper()
        if strand == '-':
            seq=DNA_reverse(DNA_complement(seq))
        seqlist = list()
        seqlistPAM = list()
        seqlistother = list()

        for nt in seq:
            seqlist.append(nt)

        filter_read = filter_dict[datainfo.loc[idx].Note]
        (mutateinforpd, deletelentpd) = caldel(samfilename=bamfile, start=start, end=end, genename=genename, filter=filter_read)

        #print(mutateinforpd)
        #print(filter_read)
        reg = mutateinforpd.loc[start:end]
        regPAM = list()
        regother = list()

        if type == 'gf':
            seqlistPAM = seqlist[-13:-10]
            seqlistother = seqlist
            seqlistother[-13:-10] = ['', '', '']
            regPAM = reg[-13:-10]
        if type == 'gr':
            seqlistPAM = seqlist[-13:-10]
            seqlistother = seqlist
            seqlistother[-13:-10] = ['', '', '']
            regPAM = reg[-13:-10]
        # if type == 'gr':
        #     seqlistPAM = seqlist[10:13]
        #     seqlistother = seqlist
        #     seqlistother[10:13] = ['', '', '']
        #     regPAM = reg[10:13]
        lenth = end - start
        if (type == 'cf' or type == 'cr') and lenth == 65:
            seqlistPAM = seqlist[10:13]
            seqlistother = seqlist
            seqlistother[10:13] = ['', '', '']
            regPAM = reg[10:13]
        if (type == 'cf' or type == 'cr') and lenth == 66:
            seqlistPAM = seqlist[10:14]
            seqlistother = seqlist
            seqlistother[10:14] = ['', '', '', '']
            regPAM = reg[10:14]
        # if type == 'cf':
        #     seqlistPAM = seqlist[0:4]
        #     seqlistother = seqlist
        #     seqlistother[0:4] = ['', '', '', '']
        #     regPAM = reg[0:4]
        # if type == 'cr':
        #     seqlistPAM = seqlist[0:4]
        #     seqlistother = seqlist
        #     seqlistother[0:4] = ['', '', '', '']
        #     regPAM = reg[0:4]
        # if type == 'cr':
        #     seqlistPAM = seqlist[-4:]
        #     seqlistother = seqlist
        #     seqlistother[-4:] = ['', '', '', '']
        #     regPAM = reg[-4:]
        #print(reg)
        fig, ax = plt.subplots()
        y=reg.delrate
        if strand == '-':
            y=y[::-1]
        ax.bar(reg.index, y, color='blue')
        ax.set_title(note)
        ax.set_xticks(reg.index, minor=True)
        ax.set_xticklabels(seqlistother, color="black", minor=True, fontdict = {'family': 'Arial'}, size = 5)  # minor=True表示次坐标轴
        ax.set_xticks(regPAM.index)
        ax.set_xticklabels(seqlistPAM, color="red", fontdict = {'family': 'Arial'}, size = 5)
        # ax.set_xticks(reg.index)
        # ax.set_xticklabels(seqlist)
        #    plt.show()
        plt.savefig(pdffile, dpi=300, format="pdf")
        plt.close(fig)
        print(pdffile, "done!")


        ####output cvs in tmpfile
        reg['label'] = seqlistother ##合并X横坐标到reg 框架中
        reg['ratio'] = y
        reg.to_csv(graphcsv,index=True, index_label="Index")
        regPAM['label'] = seqlistPAM
        regPAM.to_csv(pamcsv,index=True, index_label="Index")
        # print('seqlistother =',seqlistother,sep=' ', file=graphfile)
        # print('regPAM =', list(regPAM.index), sep=' ', file=graphfile)
        # print('seqlistPAM =', seqlistPAM, sep=' ', file=graphfile)
        # print('strand =',strand, sep=' ',file=graphfile)
        # graphfile.close()




def DNA_complement(sequence):
    sequence = sequence.upper()
    sequence = sequence.replace('A', 't')
    sequence = sequence.replace('T', 'a')
    sequence = sequence.replace('C', 'g')
    sequence = sequence.replace('G', 'c')
    return sequence.upper()


def DNA_reverse(sequence):
    sequence = sequence.upper()
    return sequence[::-1]


# ############## warning message #########
def showwarnings(title, message):
    wBox = QtWidgets.QMessageBox()
    wBox.setIcon(QtWidgets.QMessageBox.Warning)
    wBox.setWindowTitle(title)
    wBox.setText(message)
    wBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    wBox.exec_()
##################################################
