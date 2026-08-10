import os
from glob import glob
import pandas as pd
from crisprmatch.fasta import Fasta
from subprocess import Popen
from subprocess import PIPE

def prepare(infofile, refname, output, bwabin, samtoolsbin, picardbin,inputdir):
    """

    :param infofile: a description file of details of each sample, example: sample_infor.txt
    :param refname: a fasta format of the sequence in the target region, exaple:Samples_gene.fa
    :param output: folder of temporary files
    :param bwabin: bwa bin path
    :param samtoolsbin: samtools bin bath
    :param picardbin: picard bin path
    :return:
    """
    datainfo=pd.read_csv(infofile,index_col="Index")
    outputname = os.path.join(output, 'bwa_run.sh')
    documentdir = os.path.abspath(inputdir)
    #documentdir = os.path.dirname(os.path.abspath(infofile))
    genomeindex = os.path.join(output, os.path.basename(refname))

    outio = open(outputname,"w")
    for idx in datainfo.index:
        fqname = documentdir+'/'+datainfo.loc[idx]['Sample']+'/'+datainfo.loc[idx]['Sample']+'.extendedFrags.fastq'
        bamfile = output + '/' + datainfo.loc[idx]['Note'] + '.bam'
        bwamemcmd = ' '.join([bwabin, 'mem', genomeindex,fqname, '|', samtoolsbin, 'view','-bS','-', '|', samtoolsbin, 'sort', '-','-o', bamfile])
        samtoolscmd = ' '.join([samtoolsbin, 'index',bamfile])
        print(bwamemcmd)
        print(samtoolscmd)
        bwarun = Popen(bwamemcmd, stdout=PIPE, stderr=PIPE, shell=True)
        bwarun.communicate()
        samtoolsrun = Popen(samtoolscmd, stdout=PIPE, stderr=PIPE, shell=True)
        samtoolsrun.communicate()

        # print(bwabin,' mem ', os.path.basename(refname), ' ', fqname, ' | ',picardbin,' SortSam I=/dev/stdin O=', bamfile,
        #       ' SO=coordinate', sep='', file=outio)
        # print(samtoolsbin,' index ',bamfile, file=outio)
        #print('bwa mem ', os.path.basename(refname), ' ', fqname, ' | picard SortSam I=/dev/stdin O=', bamfile, ' SO=coordinate', sep='',
        #      file=outio)
        #print('samtools index ', bamfile, file=outio)
    # outio.close()
    print("bwa command load!")

    # ###run bwa mem
    # bwacmd="bash bwa_run.sh"
    # print(bwacmd)
    # runbwaalign = Popen(bwacmd, shell=True, cwd=output)
    # runbwaalign.communicate()

    print("bwa mem finished")

    return True
