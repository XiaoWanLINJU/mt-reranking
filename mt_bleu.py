# -*-encoding:utf-8 -*-
__author__ = 'XiaoWanLI'
import codecs
import os
import sys

def baseline_bleu():
    """
    """
    # filelist = ['2', '3', '4', '5', '6']
    filelist = ['6']
    foldlist = ['1', '2', '3']
    for fold in foldlist:
        for fi in filelist:
            print fold, fi
            res_file = "M:\\MT100best\\jhj\\decode" + fold + "\\run" + fold + ".mt0" + fi + ".output.derivation.txt.trans.baseline"
            cmd = "M:\\MT100best\\BLEU_hiro.exe M:\\MT100best\\jhj\\rawdev\\mt0" + fi + ".ce.dev " + res_file + " >> " + res_file + ".bleu"
            print cmd
            os.system(cmd)

def ori2svm(file_name):
    """
    not debuged yet...
    """
    global embedding_list
    getEmbeddingList('CTB_LDC_100.bin')
    print "len(embedding_list)", len(embedding_list)
    fr = codecs.open(file_name, 'r')
    fw = codecs.open(file_name + '.best_worst_embedding_svm', 'w')
    line = fr.readline()

    while line:
        if line.__contains__('Sent Id'):
            currentId = str(line.split(':')[0]).split()[2]
            line = fr.readline()
            scorelist = []
            featureslist = []
            wordlist = []
            while not line.__contains__('==='):
                tokens = line.split()
                scorelist.append(tokens[-1])
                featureslist.append(tokens[-10:-1])
                wordlist.append(tokens[1:-10])
                # fw.write(score + ' ' + 'sid:' + currentId + ' ' + ' '.join(features) + '\n')
                line = fr.readline()
            maxindex = scorelist.index(max(scorelist))
            minindex = scorelist.index(min(scorelist))

            fw.write('1 sid:' + currentId + ' ' + ' '.join(featureslist[maxindex]) + ' ' + ' '.join(getEmbeddings(wordlist, maxindex)) + '\n')
            fw.write('0 sid:' + currentId + ' ' + ' '.join(featureslist[minindex]) + ' ' + ' '.join(getEmbeddings(wordlist, minindex)) + '\n')

            # maxscorelist = scorelist[0:6]
            # minscorelist = scorelist[-6:-1]
            # for i in range(len(featureslist)):
            #     if scorelist[i] in maxscorelist:
            #         fw.write('1 ' + 'sid:' + currentId + ' ' + ' '.join(featureslist[i]) + '\n')
            #     elif scorelist[i] in minscorelist:
            #         fw.write('0 ' + 'sid:' + currentId + ' ' + ' '.join(featureslist[i]) + '\n')
        line = fr.readline()
    fr.close()
    fw.close()

def get_res_list(infor_file):
    """
    infor_file: file with source sentence and hyphothesis
    return: list of hyphothesis list for each source sentence
    """
    reslist = []
    fr = codecs.open(infor_file, 'r')
    line = fr.readline()
    while line:
        if line.__contains__('Sent Id'):
            tmp = line.split(':')[0]
            restmp = []
            line = fr.readline()
            while not line.__contains__('======='):
                restmp.append(line.strip())
                line = fr.readline()
            if len(restmp) != 100:
                print tmp, len(restmp),restmp
        line = fr.readline()
        reslist.append(restmp)
    return reslist

def getEffBule(h, infor_file, res_path, file_index, profix):
    """
    for linear and feedforward nn
    h: hidden layer size
    infor_file: the infor file which include the sentence and hyphothesis
    res_path: the dir which stores the score file
    file_index: which mt file
    profix: profix of score file, such as effsmh, linearh
    """
    reslist = get_res_list(infor_file)
    fwf = codecs.open(infor_file + ".blue", "a")
    fwf.write(profix + '\n')
    res_file = res_path + profix + str(h) + 'srmt0' + str(file_index) + '.cntktest.ScaledLogLikelihood.score'
    fw = codecs.open(res_file + ".res", 'w')
    reslines = codecs.open(res_file, 'r').readlines()

    for i in range(len(reslist)):
        if len(reslist[i]) == 1:
            topres = reslist[i][0]
            fw.write(topres + '\n')
        else:
            score = [float(x) for x in reslines[sum([len(reslist[x]) for x in range(0, i)]):sum([len(reslist[x]) for x in range(0, i + 1)])]]
            topres = reslist[i][score.index(max(score))]
            fw.write(topres + '\n')

    fw.close()
    cmd = "M:\\MT100best\\BLEU_hiro.exe M:\\MT100best\\jhj\\rawdev\\mt0" + file_index + ".ce.dev " + res_file + ".res >> " + res_file + ".res.bleu"
    print cmd
    os.system(cmd)
    bleulines = codecs.open(res_file + ".res.bleu", 'r').readlines()
    fwf.write('h' + str(h) + '\t' + str(bleulines[-1]).split(":")[-1])
    fwf.close()



def getBule(wlist, clist, infor_file, res_path, file_index):
    """
    for cnn
    infor_file: the infor file which include the sentence and res
    res_path: the score of each res
    """
    reslist = get_res_list(infor_file)
    fwf = codecs.open(infor_file + ".blue", "w")
    for w in wlist:
        for c in clist:
            res_file = res_path + 'w' + str(w) + 'c' + str(c) + 'nohiddensmd0mt0' + file_index + '.cntktest.ScaledLogLikelihood.score'
            fw = codecs.open(res_file + ".res", 'w')
            reslines = codecs.open(res_file, 'r').readlines()
            # print "len(reslist)", len(reslist)
            for i in range(len(reslist)):
                if len(reslist[i]) == 1:
                    topres = reslist[i][0]
                    fw.write(topres + '\n')
                else:
                    score = [float(x) for x in reslines[sum([len(reslist[x]) for x in range(0, i)]):sum([len(reslist[x]) for x in range(0, i + 1)])]]
                    topres = reslist[i][score.index(max(score))]
                    fw.write(topres + '\n')

            fw.close()
            cmd = "M:\\MT100best\\BLEU_hiro.exe M:\\MT100best\\jhj\\rawdev\\mt0" + file_index + ".dev " + res_file + ".res >> " + res_file + ".res.bleu"
            print cmd
            os.system(cmd)
            bleulines = codecs.open(res_file + ".res.bleu", 'r').readlines()
            fwf.write('w' + str(w) + 'c' + str(c) + '\t' + str(bleulines[-1]).split(":")[-1])
    fwf.close()

def length_len():
    """
    statistic of the length of hyphothesis
    """
    path = 'M:\\MT100best\\'
    outputfile_list = []
    for i in ['run1', 'run2', 'run3']:
        for j in ['2', '3', '4', '5', '6']:
            file_n = path + i + '\\' + i + '.MT0' + j + '.output.dd.txt'
            outputfile_list.append(file_n)
    output_length = {}
    for outputfile in outputfile_list:
        fr = codecs.open(outputfile)
        line = fr.readline()
        while line:
            if not line.__contains__('Sent Id') and not line.__contains__('====='):# 想清楚再写。。这么简单的逻辑。。
                if len(line.strip().split()) - 11 not in output_length.keys():
                    output_length[len(line.strip().split()) - 11] = 0
                output_length[len(line.strip().split()) - 11] += 1
            line = fr.readline()
    for key in sorted(output_length.keys()):
        print key, output_length[key]

def calculateBule():
    """
    call
    """
    file_index_list = ['2']
    pathlist = ['1', '2', '3']
    # wlist = [9, 9]
    # clist = [32, 8]
    # for path in pathlist:
    # print "4"
    # if_100("M:\\MT100best\\run2\\run2.MT04.output.dd.txt")

    # path = 'run1'
    for path in pathlist:
        for file_index in file_index_list:
            infor_file = "M:\\MT100best\\jhj\\decode" + path + "\\run" + path + ".mt0" + file_index + ".output.derivation.txt.trans"
            res_path = "M:\\MT100best\\jhj\\decode" + path + "\\res\\"
            hlist = [8, 16, 32, 64, 128, 256, 512, 768, 1024, 1280]
            for h in hlist:
                getEffBule(h, infor_file, res_path, file_index, 'effsmh')
            # for h in hlist:
            #     getEffBule(h, infor_file, res_path, file_index, 'linearh')
            # res_path = "M:\\MT100best\\" + path + "\\best_worst\\cnn\\"
            # getBule([5], [8], infor_file, res_path, file_index)



if __name__=="__main__":
    calculateBule()
    # ori2svm("run2\\run2.MT03.output.dd.txt")
    #ori2svm("run2.MT03.output.dd.txt")
    # path = 'M:\\MT100best\\'
    # filelist = ['MT02.ce.tree.dev', 'MT03.ce.tree.dev', 'MT04.ce.tree.dev', 'MT05.ce.tree.dev', 'MT06.ce.tree.dev']
    #(ch_voc, en_voc, ibm, align, trans, bleu)
    # get_ibm_bestfueture_in_libin4train("IBM\\corpus.ch.vcb", "IBM\\corpus.en.vcb", "IBM\\s2t64.t1.5",
    #                                    "IBM\\align.txt", "IBM\\trans.txt", "IBM\\bleu.txt")

    # ch_voc_dic = {}
    # en_voc_dic = {}
    # ibm_dic ={}
    # get_ibm_bestfueture_in_libin4train(ch_voc_dic, en_voc_dic, ibm_dic,
    #                                    "decode1\\test.align",
    #                                    "decode1\\test.source",
    #                                    "decode1\\test.trans",
    #                                    "decode1\\test.bleu")
    # print get_qu_match()
    # foldlist = ['3']
    # filelist = ['2']
    # for fold in foldlist:
    #     for filen in filelist:
    #         get_pos_senquence4test("decode" + fold + "\\run" + fold + ".mt0" + filen + ".output.derivation.txt.align",
    #                         "decode" + fold + "\\run" + fold + ".mt0" + filen + ".output.derivation.txt.trans",
    #                         "M:\\MT100best\\poslm\\MT02-06\\MT0" + filen + ".ce.tree.dev.berkekeytree.postag")
    #
    # get_pos_senquence4train("decode3\\run3.mt03.output.derivation.txt.align",
    #                         "decode3\\run3.mt03.output.derivation.txt.trans",
    #                         "M:\\MT100best\\poslm\\MT02-06\\MT03.ce.tree.dev.berkekeytree.postag",
    #                         "decode3\\run3.mt03.output.derivation.txt.trans2.bleu")
    # for filen in filelist:
    #     print filen
    #     #filter_phrase("mt0" + str(filen) + ".ce.dev.c")
    #     ch_voc_dic = getvoc("IBM\\corpus.ch.vcb.mt0" + str(filen) + ".ce.dev.c")
    #     filteribm("IBM\\s2t64.t1.5", ch_voc_dic, str(filen))
    # filelist =  ['2', '3', '4', '5', '6']
    # foldlist = ['1', '2', '3']
    # for fold in foldlist:
    #     for file_n in filelist:
    #         split_hpy_align_feature("decode" + fold + "\\run" + fold + ".mt0" + file_n + ".output.derivation.txt")
    #     print file_n
    #     get_pos_senquence4test("decode1\\run1.mt0" + file_n + ".output.derivation.txt.align",
    #                                        "decode1\\run1.mt0" + file_n + ".output.derivation.txt.trans",
    #                                        "M:\\MT100best\\poslm\\MT02-06\\MT0" + file_n + ".ce.tree.dev.berkekeytree.postag",
    #                                        "decode1\\run1.mt0" + file_n + ".output.derivation.txt.trans2.bleu")
        # split_hpy_align_feature("decode1\\run1.mt0" + file_n + ".output.derivation.txt")
    #     get_pos_lm_data('Z:\\raw dev\\grow.model4.align', 'Z:\\raw dev\\LDC.ch.berkeleytree.postag')
        # parser2pos("z:\\raw dev\\" + file_n + '.berkekeytree')
    #path = 'raw dev\\'
    #parser2pos(path, '\\LDC.ch.berkeleytree_3')
    # get_pos_lm_data('grow.model4.align_0', 'raw dev\\LDC.ch.berkeleytree_0.postag')

    # parser2pos('Z:\\raw dev\\corpus.ch.berkeleytree')
    #path = 'z:\\decode1\\'
    #file_list = ['2', '3', '4', '5']
    #for fn in file_list:
        #split_hpy_align_feature(path + 'run1.mt0' + fn + '.output.derivation.txt')

    #print len(vocset)
