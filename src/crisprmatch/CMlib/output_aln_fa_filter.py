import os
import pysam
from crisprmatch.fasta import Fasta
import matplotlib
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
from glob import glob
from crisprmatch.CMlib.showprocess import showbarprocess
from PyQt5 import QtWidgets

def alnfile_filter(infofile,groupinfo, refname, output, bamdir):
    """
    :param infofile: a description file of details of each sample, example: sample_infor.txt
    :param groupinfo: a description file of details of each group, example: group_infor.txt
    :param refname: a fasta format of the sequence in the target region, exaple:Samples_gene.fa
    :param output: folder of final result
    :param bamdir: folder of temporary files
    :return:
    """
    fa = Fasta(refname)
    info = pd.read_csv(infofile, index_col="Index")
    groupinfor = pd.read_csv(groupinfo)
    stranddict = dict()
    # outiofile = os.path.join(output,'filter_wt_reads_number.txt')
    # outio = open(outiofile, 'w')
    # print("Sample\tfilter", file=outio)
    for idy in groupinfor.index:
        stranddict[groupinfor.loc[idy].rep1] = groupinfor.loc[idy].strand
        stranddict[groupinfor.loc[idy].rep2] = groupinfor.loc[idy].strand
        stranddict[groupinfor.loc[idy].rep3] = groupinfor.loc[idy].strand
        stranddict[groupinfor.loc[idy].control] = groupinfor.loc[idy].strand

    for idx in info.index:

        note = info.loc[idx].Note
        if note not in stranddict:
            error = ' '.join([note, 'is not involved in group table! Please Check!'])
            showwarnings("Error", error)
            continue

        bamname = os.path.join(bamdir, info.loc[idx].Note + '.bam')
        outfile_del = os.path.join(output, info.loc[idx].Note + '_del_aln.fa')
        outfile_snp = os.path.join(output, info.loc[idx].Note + '_snp_aln.fa')
        alnfile_del = os.path.join(output, info.loc[idx].Note + '_del_aln.txt')
        alnfile_snp = os.path.join(output, info.loc[idx].Note + '_snp_aln.txt')
        print("output", info.loc[idx].Note)
        ################
        tmp = "output " + info.loc[idx].Note
        showbarprocess(tmp)
        ###############

        outfa_del = open(outfile_del, 'w')
        outfa_snp = open(outfile_snp, 'w')
        outlan_del = open(alnfile_del, 'w')
        outlan_snp = open(alnfile_snp, 'w')

        note = info.loc[idx].Note
        strand = stranddict[note]

        if (re.search("gRNA", info.loc[idx].Note)):
            if strand == '+':
                start = info.loc[idx]['start'] - 10
                end = info.loc[idx]['end'] + 10

            else:
                start = info.loc[idx]['start'] - 10
                end = info.loc[idx]['end'] + 10

        elif (re.search("crRNA", info.loc[idx].Note)):
            if strand == '+':
                start = info.loc[idx]['start'] - 10
                end = info.loc[idx]['end'] + 30

            else:
                start = info.loc[idx]['start'] - 30
                end = info.loc[idx]['end'] + 10

        # if (re.search("gRNA", info.loc[idx].Note)):
        #     start = info.loc[idx].start - 10
        #     end = info.loc[idx].end + 10
        # elif (re.search("crRNA", info.loc[idx].Note)):
        #     start = info.loc[idx].start
        #     end = info.loc[idx].end + 30
            #start = info.loc[idx].start - 10
            #end = info.loc[idx].end - 10
        gene = info.loc[idx].gene_name
        samfile = pysam.AlignmentFile(bamname, "rb")
        mtreads = set()
        totalcov = 0
        covage = 0

        replace = set()
        replace_left = set()
        replace_final = set()
        all_tmp = set()
        wt_set = set()
        replace_side = set()
        wt_side_set = set()
        wt_final_set = set()
        filter_set = set()

        insert = set()

        deletion = set()

        reads = dict()

        seq = fa[gene][start - 1:end].upper()  ##reference sequence
        seqlist = list()
        for nt in seq:
            seqlist.append(nt)

        for pileupcolumn in samfile.pileup(gene, max_depth=50000):

            # print (pileupcolumn.pos, pileupcolumn.n)



            totalcov += pileupcolumn.n
            #        print(pileupcolumn.pos, pileupcolumn.n)

            if end > pileupcolumn.pos >= start-1:

                for pileupread in pileupcolumn.pileups:
                    #                print(pileupcolumn.pos, pileupcolumn.n)

                    if pileupread.alignment.query_name not in reads:
                        #                    print(pileupread.alignment.query_name)
                        reads[pileupread.alignment.query_name] = ''

                    if not pileupread.is_del and not pileupread.is_refskip:
                        refbase = fa[gene][pileupcolumn.pos].upper()
                        querybase = pileupread.alignment.query_sequence[pileupread.query_position]
                        all_tmp.add(pileupread.alignment.query_name)
                        if querybase != refbase:
                            replace.add(pileupread.alignment.query_name)

                        reads[pileupread.alignment.query_name] += pileupread.alignment.query_sequence[
                            pileupread.query_position]
                        #                    print(reads[pileupread.alignment.query_name])

                        #                    print(pileupread.query_position)
                        #                     querybase = pileupread.alignment.query_sequence[pileupread.query_position]

                        #         #             refbase = pileupread.alignment.get_reference_sequence()[pileupread.query_position]
                        #                     refbase = fa[gene][pileupcolumn.pos].upper()
                        #                     if querybase !=refbase :
                        # #                         replace += 1
                        #                         mtreads.add(pileupread.alignment.query_name)
                        #                         replace.add(pileupread.alignment.query_name)

                        #                 if pileupread.indel > 0:

                        # #                     insert += 1
                        #                     mtreads.add(pileupread.alignment.query_name)
                        #                     insert.add(pileupread.alignment.query_name)
                        #                     print()

                    if pileupread.indel < 0:
                        reads[pileupread.alignment.query_name] += '-' * abs(pileupread.indel)
                        deletion.add(pileupread.alignment.query_name)
                        #                    print(reads[pileupread.alignment.query_name])
                        #                    print(reads)
                        # #                     deletion += 1
                        #                     mtreads.add(pileupread.alignment.query_name)
                        #                     deletion.add(pileupread.alignment.query_name)

        wt_set = all_tmp - replace
        for pileupcolumn_filter in samfile.pileup(gene, max_depth=50000):  ###两边也无突变

            if start > pileupcolumn_filter.pos >= 0 or pileupcolumn_filter.pos > end:
                for pileupread_filter in pileupcolumn_filter.pileups:
                    # for replace_filter in replace_all:

                    # if replace_filter in str(pileupread_filter) :
                    # replace_side.add(pileupread_filter.alignment.query_name)

                    if pileupread_filter.alignment.query_name not in replace_left:

                        if not pileupread_filter.is_del and not pileupread_filter.is_refskip:
                            querybase_filter = pileupread_filter.alignment.query_sequence[pileupread_filter.query_position]

                            #             refbase = pileupread.alignment.get_reference_sequence()[pileupread_filter.query_position]

                            refbase_filter = fa[gene][pileupcolumn_filter.pos].upper()
                            replace_side.add(pileupread_filter.alignment.query_name)  # 两边无突变
                            if querybase_filter != refbase_filter:
                                #                         replace += 1
                                # mtreads.add(pileupread.alignment.query_name)

                                # replace.add(pileupread.alignment.query_name)
                                replace_left.add(pileupread_filter.alignment.query_name)  # 两边无突变，有错配
                                # break


        wt_side_set = replace_side - replace_left
        wt_final_set = wt_side_set & wt_set
        filter_set = wt_set - wt_side_set
        replace_final = replace - deletion


        lt = end - start + 1
        #    print(lt)
        typdict = dict()
        typdict_snp = dict()
        typdict_del = dict()
        for i in reads:
            if i in filter_set:
                continue
            if len(reads[i]) == lt:
                #            print(reads[i])
                if i in replace_final:
                    if reads[i] in typdict_snp:
                        typdict_snp[reads[i]] += 1
                    else:
                        typdict_snp[reads[i]] = 1
                    continue
                if i in deletion:
                    if reads[i] in typdict_del:
                        typdict_del[reads[i]] += 1
                    else:
                        typdict_del[reads[i]] = 1
                    continue

                if reads[i] in typdict:
                    typdict[reads[i]] += 1
                else:
                    typdict[reads[i]] = 1
        for mutype in typdict:
            print('>', typdict[mutype], sep='', file=outfa_snp)
            print(mutype, file=outfa_snp)
            print(typdict[mutype], '\t'.join(mutype), sep='\t', file=outlan_snp)
            print('>', typdict[mutype], sep='', file=outfa_del)
            print(mutype, file=outfa_del)
            print(typdict[mutype], '\t'.join(mutype), sep='\t', file=outlan_del)
        for mutype_snp in typdict_snp:
            print('>', typdict_snp[mutype_snp], sep='', file=outfa_snp)
            print(mutype_snp, file=outfa_snp)
            print(typdict_snp[mutype_snp], '\t'.join(mutype_snp), sep='\t', file=outlan_snp)
        for mutype_del in typdict_del:
            print('>', typdict_del[mutype_del], sep='', file=outfa_del)
            print(mutype_del, file=outfa_del)
            print(typdict_del[mutype_del], '\t'.join(mutype_del), sep='\t', file=outlan_del)
        print("Refseq",'\t'.join(seqlist), sep='\t',file=outlan_snp)
        print("Refseq", '\t'.join(seqlist), sep='\t', file=outlan_del)


        # print(info.loc[idx].Note, end='\t', file=outio)
        # print(len(filter_set), end='\n', file=outio)
        outfa_snp.close()
        outlan_snp.close()
        outfa_del.close()
        outlan_del.close()
    #outio.close()

# ############## warning message #########
def showwarnings(title, message):
    wBox = QtWidgets.QMessageBox()
    wBox.setIcon(QtWidgets.QMessageBox.Warning)
    wBox.setWindowTitle(title)
    wBox.setText(message)
    wBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    wBox.exec_()
##################################################
