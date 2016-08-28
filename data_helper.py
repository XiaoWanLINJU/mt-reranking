# -*-encoding:utf-8 -*-
__author__ = 'XiaoWanLI'
import codecs
import os
import sys
import mt_bleu

def baseline(file_name):
    """
    get baseline system, and the file in correct format
    """
    fr = codecs.open(file_name, 'r')
    fw = codecs.open(file_name + '.baseline', 'w')
    line = fr.readline()
    # print line
    while line:
        if line.__contains__("Sent Id"):
            # print line
            line = fr.readline()
            # tolens = line.split()
            fw.write(line.strip() + '\n')
        line = fr.readline()
    fr.close()
    fw.close()

def if_100(file):
    """
    dev file should have top N res, check which ones are not
    """
    fr = codecs.open(file)
    line = fr.readline()
    while line:
        if line.__contains__('Sent Id'):
            count = 0
            tmp = line.split(':')[0]
            line = fr.readline()
            while not line.__contains__('======='):
                count += 1
                line = fr.readline()
            if count != 100:
                print tmp, count
        line = fr.readline()


def get_res_list(infor_file):
    reslist = []
    fr = codecs.open(infor_file, 'r')
    line = fr.readline()
    while line:
        if line.__contains__('Sent Id'):
            tmp = line.split(':')[0]
            restmp = []
            line = fr.readline()
            while not line.__contains__('======='):
                restmp.append(' '.join(line.strip().split()[1:-10]))
                line = fr.readline()
            if len(restmp) != 100:
                print tmp, len(restmp),restmp
        line = fr.readline()
        reslist.append(restmp)
    return reslist


def split_dev(file_n):
    lines = codecs.open(file_n, 'r').readlines()
    cfw = codecs.open(file_n + '.berkekeytree', "w")
    rf1fw = codecs.open(file_n + '.rf1', "w")
    rf2fw = codecs.open(file_n + '.rf2', "w")
    rf3fw = codecs.open(file_n + '.rf3', "w")
    rf4fw = codecs.open(file_n + '.rf4', "w")
    for i in range(len(lines)):
        if i%7 == 1:
            cfw.write(lines[i])
        elif i%7 == 2:
            rf1fw.write(lines[i])
        elif i%7 == 3:
            rf2fw.write(lines[i])
        elif i%7 == 4:
            rf3fw.write(lines[i])
        elif i%7 == 5:
            rf4fw.write(lines[i])
    rf1fw.close()
    rf2fw.close()
    rf3fw.close()
    rf4fw.close()


def filteribm(filen, ch_voc_dic, mt):
    # voc_dic = {}
    ch_tokens = set()
    fw = codecs.open(filen + '.filter' + mt, 'w')
    for key in ch_voc_dic.keys():
        ch_tokens.add(ch_voc_dic[key])# get the index of all ch_voc
    print len(ch_tokens)
    fr = codecs.open(filen)
    line = fr.readline()
    while line:
        tokens = line.strip().split()
        if int(tokens[0]) in ch_tokens:
            fw.write(line.strip() + '\n')
            # voc_dic['_'.join(tokens[:-1])] = float(tokens[-1])# words as key
        line = fr.readline()
    # return voc_dic
    fw.close()



def get_voc_index(en_voc_dic, tokens):
    index = []
    for to in tokens:
        if to not in en_voc_dic.keys():
            index.append(en_voc_dic['unk'])
        else:
            index.append(en_voc_dic[to])
    return index



def split_hpy_align_feature(file_n):
    print file_n
    transfw = codecs.open(file_n + '.trans', 'w')
    trans2fw = codecs.open(file_n + '.trans2', 'w')
    alignfw = codecs.open(file_n + '.align', 'w')
    featurefw = codecs.open(file_n + '.feat', 'w')
    fr = codecs.open(file_n)
    line = fr.readline().strip()
    while line:
        if line.__contains__('========='):
            transfw.write(line + ' \n')
            alignfw.write(line + ' \n')
            featurefw.write(line + ' \n')
            trans2fw.write(line + ' \n')
        elif line.__contains__('Sent Id'):
            transfw.write(line + ' \n')
            alignfw.write(line + ' \n')
            featurefw.write(line + '\n')
        elif line.startswith('Trans: '):
            transfw.write(line.replace('Trans: ','') + ' \n')# 这种写法有风险啊你妹的。。。你怎么知道句子里没有分号。。
            trans2fw.write(line.replace('Trans: ','') + ' \n')
        elif line.startswith('Feat: '):
            featurefw.write(line.replace('Feat: ','') + ' \n')
        elif line.startswith('Align: '):
            alignfw.write(line.replace('Align: ','') + ' \n')
        line = fr.readline().strip()
    transfw.close()
    trans2fw.close()
    alignfw.close()
    featurefw.close()
    fr.close()

def filter_phrase(chfile):
    lines = codecs.open("IBM\\" + chfile, 'r').readlines()
    vocset = set()
    for line in lines:
        vocset = vocset | set(line.strip().split())
    fr = codecs.open("IBM\\corpus.ch.vcb", 'r')
    fw = codecs.open("IBM\\corpus.ch.vcb." + chfile, 'w')
    line = fr.readline()
    while line:
        if line.strip().split()[1] in vocset:
            fw.write(line)
        line = fr.readline()
    fr.close()
    fw.close()

def split_logp():
    path = "M:\\MT100best\\poslm\\testdata\\"
    filel = ['2', '3']
    fold = ['1', '2', '3']
    for fo in fold:
        for fi in filel:
            filen = path + "run" + fo + ".mt0" + fi + ".output.derivation.txt.trans.poslmtop10.res"
            lines = codecs.open(filen, 'r').readlines()
            fw = codecs.open(filen.replace('.res', '.score'), 'w')
            for line in lines:
                if line.__contains__('logprob'):
                    fw.write(line.strip().split('=')[1].replace('ppl', '') + '\n')
            fw.close()

def get_feat4train(fold, index, top):
    """
    use the index of mt data to get best and worst instance

    """
    # fold_list = ['1', '2', '3']
    # for fold in fold_list:
    print fold
    bleu_f = "decode" + fold + "\\" + "run" + fold + ".mt0" + index + ".output.derivation.txt.trans2.bleu"
    feat_f = "decode" + fold + "\\" + "run" + fold + ".mt0" + index + ".output.derivation.txt.feat"# the first oen is mert score

    ffr = codecs.open(feat_f, 'r')
    frb = codecs.open(bleu_f, 'r')
    fw2 = codecs.open("decode" + fold + "\\" + "run" + fold + ".mt0" + index + ".output.derivation.txt.feat4traintop" + str(top), 'w')
    line = ffr.readline()
    lineb = frb.readline()

    while line:
        # print "while", line, " line.__contains__('Sent Id')",  line.__contains__('Sent Id')
        if line.__contains__('Sent Id'):
            bleulist = []
            lineb = frb.readline()# 只有在sentid一行需要读，在====分割不需要，因为blue并没有这个分割。。
            feat_list = []

        else:
            while not line.__contains__('========'):
                bleulist.append(float(lineb.strip().split(':')[1]))
                feat_list.append(' '.join(line.strip().split()[1:]))
                line = ffr.readline()
                lineb = frb.readline()
            sb = sorted(bleulist)
            for i in range(top):
                fw2.write(feat_list[bleulist.index(sb[i])] + '\n')#这个是从小到大啊
            for i in range(top):
                fw2.write(feat_list[bleulist.index(sb[-i])] + '\n')#这个是从小到大啊
            # maxindex = bleulist.index(max(bleulist))
            # minindex = bleulist.index(min(bleulist))
            # fw2.write(feat_list[maxindex] + '\n')
            # fw2.write(feat_list[minindex] + '\n')
        line = ffr.readline()
    ffr.close()
    frb.close()

def empty_poslm20(fold, index, suffix):
    path = "M:\\MT100best\\poslm\\testdata\\"
    pos_f = path + "run" + fold + ".mt0" + index + ".output.derivation.txt.trans.poslm" + suffix
    score_f = pos_f + '.score'
    fr = codecs.open(pos_f, 'r')
    frs = codecs.open(score_f, 'r')
    fw = codecs.open(score_f + 'clean', 'w')

    line = fr.readline()
    lines = frs.readline()
    while line:
        if len(line.strip().split()) > 0:
            fw.write(lines.strip() + '\n')
            lines = frs.readline()
        else:
            fw.write('0.0 \n')
        line = fr.readline()
    fr.close()
    frs.close()
    fw.close()


def get_cntk4train(top):
    """
    use the best and worst instance to create cntk format file
    """
    filelist = ['3']
    foldlist = ['1', '2', '3']
    for fold in foldlist:
        for fi in filelist:
            print fold, fi
            get_feat4train(fold, fi, top)

            addfe = "M:\\MT100best\\jhj\\decode" + fold + "\\run" + fold + ".mt0" + fi + ".output.derivation.txt.trans.addfeat.4traintop10"
            fe = "M:\\MT100best\\jhj\\decode" + fold + "\\run" + fold + ".mt0" + fi + ".output.derivation.txt.feat4traintop10"
            poslm = "M:\\MT100best\\poslm\\testdata\\run" + fold + ".mt0" + fi + ".output.derivation.txt.trans.poslmtop10.scoreclean"
            addfelines = codecs.open(addfe, 'r').readlines()
            felines = codecs.open(fe, 'r').readlines()
            pllines = codecs.open(poslm, 'r').readlines()
            fw = codecs.open("M:\\MT100best\\jhj\\decode" + fold + "\\run" + fold + ".mt0" + fi + ".cntk", 'w')
            print len(addfelines), len(felines), len(pllines)
            for i in range(0, len(addfelines)/20):
                for j in range(top):
                    for k in range(top, 2 * top):# 先负例
                        # print i * 20 + k, i * 20 + k
                        fw.write(addfelines[i * 20 + k].strip() + ' ' + felines[i * 20 + k].strip() +  ' ' + pllines[i * 20 + k].strip() +  ' '
                        + addfelines[i * 20 + j].strip() + ' ' + felines[i * 20 + j].strip() +  ' ' + pllines[i * 20 + j].strip() + ' 1.0\n')
                        fw.write(addfelines[i * 20 + j].strip() + ' ' + felines[i * 20 + j].strip() +  ' ' + pllines[i * 20 + j].strip()  +  ' '
                        + addfelines[i * 20 + k].strip() + ' ' + felines[i * 20 + k].strip() +  ' ' + pllines[i * 20 + k].strip() + ' 0.0\n')
            fw.close()

def get_svm4test():
    """
    combine ibm feature, baseline feature and poslm fearure as svm format
    """
    filelist = ['6']
    foldlist = ['1', '2', '3']
    for fold in foldlist:
        for fi in filelist:
            print fold, fi
            addfe = "M:\\MT100best\\jhj\\decode" + fold + "\\run" + fold + ".mt0" + fi + ".output.derivation.txt.trans.addfeat.4test"
            bf = "M:\\MT100best\\jhj\\decode" + fold + "\\run" + fold + ".mt0" + fi + ".output.derivation.txt.trans2.bleu"
            fe = "M:\\MT100best\\jhj\\decode" + fold + "\\run" + fold + ".mt0" + fi + ".output.derivation.txt.feat"
            poslm = "M:\\MT100best\\poslm\\testdata\\run" + fold + ".mt0" + fi + ".output.derivation.txt.trans.poslm4test.scoreclean"
            addfefr = codecs.open(addfe, 'r')
            fefr = codecs.open(fe, 'r')
            plfr = codecs.open(poslm, 'r')
            bfr = codecs.open(bf, 'r')
            fw = codecs.open("M:\\MT100best\\jhj\\decode" + fold + "\\run" + fold + ".mt0" + fi + ".bleusvm", 'w')
            # print len(addfelines), len(felines), len(pllines)
            # fe has sepete sentence
            line = fefr.readline()
            bline = bfr.readline()
            while line:
                if line.__contains__('Sent Id'):
                    currentId = str(line.split(':')[0]).split()[2]
                    line = fefr.readline()
                    bline = bfr.readline()
                    while not line.__contains__('==='):
                        lineadd = addfefr.readline()
                        linepl = plfr.readline()
                        if not lineadd:
                            print "empty lineadd"

                        if not linepl:
                            print "empty linepl"
                        fw.write(bline.strip().split(':')[1] + ' sid:' + currentId + ' ' + lineadd.strip() + ' ' + ' '.join(line.strip().split()[1:]) +  ' ' + linepl.strip() + ' \n')
                        # fw.write(score + ' ' + 'sid:' + currentId + ' ' + ' '.join(features) + '\n')
                        line = fefr.readline()
                        bline = bfr.readline()
                line = fefr.readline()
                # bleu file has no "======" line
            fefr.close()
            plfr.close()
            fw.close()
            addfefr.close()


def check_tocken(file_index):
    """
    dev files inconsistent, check it out
    """
    notree = "M:\\MT100best\\jhj\\rawdev\\mt0" + file_index + ".ce.dev"
    tree = "M:\\MT100best\\poslm\\MT02-06\\MT0" + file_index + ".ce.tree.dev"
    fn = codecs.open(notree, 'r').readlines()
    ft = codecs.open(tree, 'r').readlines()
    for i in range(len(fn)):
        if i %7 == 0:
            ttokens = fn[i].split()
            ntokens = ft[i].split()
            if len(ttokens) != len(ntokens):
                print i, len(ttokens),len(ntokens), "len(ttokens),len(ntokens)"
            else:
                for j in range(len(ttokens)):
                    if ttokens[j] != ntokens[j]:
                        print i, "ttokens[j] != ntokens[j]:"

import re
def parser2pos(path, filen):
    """
    maybe somebugs...
    """
    fr = codecs.open(path + filen, 'r')
    fw = codecs.open(filen + '.postag', 'w')
    line = fr.readline()
    # re_words = re.compile(u"[\u4e00-\u9fa5]+")
    while line:
        # print re.findall('\(\w*\s\w*\)', line) # \w 并不能匹配中文，
        fw.write(' '.join([x.replace('(', '').replace(')', '').replace(' ', '_')for x in re.findall("\(\w*\s[^\(\)]*\)", line)]) + '\n')
        line = fr.readline()
    fr.close()
    fw.close()


if __name__=="__main__":
    get_svm4test()
    # get_cntk4train(10)
    # for i in range(1, 4):
    #     empty_poslm20(str(i), '3', 'top10')
    #     empty_poslm20(str(i), '6', '4test')

    # split_logp()
    # get_svm4test()
     # baseline_bleu()
    # filelist = ['2', '3', '4', '5', '6']
    # foldlist = ['1', '2', '3']
    # for fold in foldlist:
    #     baseline("decode" + fold + "\\" + "run" + fold + ".mt06.output.derivation.txt.trans")
    # mt_bleu.baseline_bleu()
        # split_hpy_align_feature("decode" + fold + "\\" + "run" + fold + ".mt06.output.derivation.txt")
    #     for fi in filelist:
    #         print fold, fi
    #         filen = "M:\\MT100best\\jhj\\decode" + fold + "\\run" + fold + ".mt0" + fi + ".output.derivation.txt.trans.baseline"
    #         preprocess(filen)
    #                                    "decode1\\test.bleu")
    # print get_qu_match()
    # foldlist = ['1']
    # for fold in foldlist:
    #     get_pos_senquence4train("decode" + fold + "\\run" + fold + ".mt06.output.derivation.txt.align",
    #                         "decode" + fold + "\\run" + fold + ".mt06.output.derivation.txt.trans",
    #                         "M:\\MT100best\\poslm\\MT02-06\\MT06.ce.tree.dev.berkekeytree.postag",
    #                         "decode" + fold + "\\run" + fold + ".mt06.output.derivation.txt.trans2.bleu")
    #
    # if_100("M:\\MT100best\\jhj\\decode1\\run1.mt06.output")
    # get_feat4train('3')
    # get_feat4train('2')
    # split_logp()
    # for i in range(2,7):
    #     print i
    #     check_tocken(str(i))