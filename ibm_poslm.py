# -*-encoding:utf-8 -*-
__author__ = 'XiaoWanLI'
import codecs
import os
import sys


def s2tdic(al, **arg):
    # print al
    tmpDic = {}
    valSet = set()
    altokens = al.strip().split()
    for at in altokens:
        # print at
        key, val = at.split("-")# source to target
        if 'start' in arg.keys():
            key = str(int(key) - int(arg['start']))
            val = str(int(val) - int(arg['start']))
        if key not in tmpDic.keys():
            tmpDic[key] = []
        tmpDic[key].append(val)# absolute position
        valSet.add(val)
    return tmpDic, valSet

def t2sdic(al, **arg):
    # print al
    tmpDic = {}
    valSet = set()
    altokens = al.strip().split()
    for at in altokens:
        # print at
        val, key = at.split("-")# source to target
        if 'start' in arg.keys():
            key = str(int(key) - int(arg['start']))
            val = str(int(val) - int(arg['start']))
        if key not in tmpDic.keys():
            tmpDic[key] = []
        tmpDic[key].append(val)# absolute position
        valSet.add(val)
    return tmpDic, valSet

# pos as empty, alignmentline as empty, pos is ill formed...not sure the alignment of pos, so skip
def get_projected_pos(postokens, t2sDic, source_posi_set):
    # print postokens, source_posi_set, t2sDic
    if len(postokens) < max([int(x) for x in source_posi_set]):
        return []
    postmp = []
    for i in range(max([int(x) for x in t2sDic.keys()])):# key is target
        if i not in sorted([int(x) for x in t2sDic.keys()]):# target 对空
            postmp.append('non_0 ')# relative position
        else:
            tmp = ''
            for val in sorted([int(x) for x in t2sDic[str(i)]]):
                # tmp += postokens[int(val) - 1] + "_" + str(int(val) - i) + '_'
                # print postokens, val
                tmp += postokens[int(val)] + "_" + str(int(val) - i) + '_'
            postmp.append(tmp[:-1] + ' ')
    return postmp


def get_pos_lm_data(alignment, ch_pos):# 在GIZA++, align 下标从0开始, 青龙同学！！！！！！！！！
    alignment_fr = codecs.open(alignment, 'r')
    ch_pos_fr = codecs.open(ch_pos, 'r')
    pos_lm = codecs.open(alignment + 'poslm', 'w')
    al = alignment_fr.readline()
    cl = ch_pos_fr.readline()
    while al:
        postokens = [x.split("_")[0] for x in cl.strip().split()]
        t2sDic, source_posi_set = t2sdic(al)
        try:# if any ecception, just skip
            if len(postokens) == len(source_posi_set):
                postmp = get_projected_pos(postokens, t2sDic, source_posi_set)
                pos_lm.write(' '.join(postmp) + '\n')
        except Exception, e:
            print e.message
            print al
            print cl
        al = alignment_fr.readline()
        cl = ch_pos_fr.readline()

import re
def parser2pos(path, filen):
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

def getvoc(filen):
    voc_dict = {}
    fr = codecs.open(filen)
    line = fr.readline()
    if len(line.strip().split()) == 3:
        while line:
            tokens = line.strip().split()
            # print tokens[1],'主席',type(tokens[1])
            voc_dict[tokens[1]] = int(tokens[0])# words as key
            line = fr.readline()
    return voc_dict

def getibm(filen):
    voc_dict = {}
    fr = codecs.open(filen)
    line = fr.readline()
    while line:
        tokens = line.strip().split()
        # voc_dict['_'.join(tokens[:-1])] = float(tokens[-1])# words as key
        try:
            voc_dict[tokens[0]][tokens[1]] = float(tokens[2])
        except KeyError:
            voc_dict[tokens[0]] = {tokens[1]:float(tokens[2])}
        line = fr.readline()
    return voc_dict

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

def get_pos_senquence4train(align, trans, pos_ch, bleu, **therest):

    fr = codecs.open(trans, 'r')
    fra = codecs.open(align, 'r')
    frp = codecs.open(pos_ch, 'r')
    frb = codecs.open(bleu, 'r')
    fw2 = codecs.open(trans + '.poslm', 'w')
    line = fr.readline()
    linea = fra.readline()
    linep = frp.readline()
    lineb = frb.readline()
    top = 1
    if 'top' in therest.keys():
        top = int(therest['top'])
    while line:
        # print "while", line, " line.__contains__('Sent Id')",  line.__contains__('Sent Id')
        if line.__contains__('Sent Id'):
            tmphyplist = []
            t2sDiclist = []
            source_posi_setlist = []
            bleulist = []
            postokens = [x.split("_")[0] for x in linep.strip().split()]
            linep = frp.readline()# postag 在每个新句子里读
            lineb = frb.readline()# 只有在sentid一行需要读，在====分割不需要，因为blue并没有这个分割。。
            print line.split(":")[0]
        else:
            while not line.__contains__('========'):
                tmphyplist.append(line.strip().split())
                t2sDic, source_posi_set = t2sdic(linea, start='1')
                t2sDiclist.append(t2sDic)
                source_posi_setlist.append(source_posi_set)
                # print "lineb", lineb,"line", line, "lineb.strip().split(':')[1]",lineb.strip().split(':')[1]
                bleulist.append(float(lineb.strip().split(':')[1]))

                line = fr.readline()
                linea = fra.readline()
                lineb = frb.readline()

            cal_list = get_cal_list(bleulist, construct="4train", top=top)

            if len(cal_list) > 0:
                for index in cal_list:
                    postmp = get_projected_pos(postokens, t2sDiclist[index], source_posi_setlist[index])
                    fw2.write(' '.join(postmp) + '\n')
            # what if the max or min pos is illformed?? then check if there is an empty line!!!

        line = fr.readline()
        linea = fra.readline()

    fr.close()
    fra.close()
    frb.close()
    frp.close()

def get_pos_senquence4test(align, trans, pos_ch, bleu):

    fr = codecs.open(trans, 'r')
    fra = codecs.open(align, 'r')
    frp = codecs.open(pos_ch, 'r')
    frb = codecs.open(bleu, 'r')
    fw2 = codecs.open(trans + '.poslm', 'w')
    line = fr.readline()
    linea = fra.readline()
    linep = frp.readline()
    lineb = frb.readline()
    while line:
        # print "while", line, " line.__contains__('Sent Id')",  line.__contains__('Sent Id')
        if line.__contains__('Sent Id'):
            tmphyplist = []
            t2sDiclist = []
            source_posi_setlist = []
            bleulist = []
            postokens = [x.split("_")[0] for x in linep.strip().split()]
            linep = frp.readline()# postag 在每个新句子里读
            lineb = frb.readline()# 只有在sentid一行需要读，在====分割不需要，因为blue并没有这个分割。。
            # print "line.__contains__('Sent Id'):", line
        else:
            while not line.__contains__('========'):
                tmphyplist.append(line.strip().split())
                t2sDic, source_posi_set = t2sdic(linea, start='1')
                t2sDiclist.append(t2sDic)
                source_posi_setlist.append(source_posi_set)
                # print "lineb", lineb,"line", line, "lineb.strip().split(':')[1]",lineb.strip().split(':')[1]
                bleulist.append(float(lineb.strip().split(':')[1]))

                line = fr.readline()
                linea = fra.readline()
                lineb = frb.readline()

            for i in range(len(t2sDiclist)):
                postmp = get_projected_pos(postokens, t2sDiclist[i], source_posi_setlist[i])
                fw2.write(' '.join(postmp) + '\n')
            # print line, "========", maxindex,max(bleulist), postokens
            # print minindex,min(bleulist)
            # print bleulist
            # what if the max or min pos is illformed?? then check if there is an empty line!!!

        line = fr.readline()
        linea = fra.readline()
    fr.close()
    fra.close()
    frb.close()
    frp.close()
    fw2.close()

def get_voc_index(en_voc_dic, tokens):
    index = []
    for to in tokens:
        if to not in en_voc_dic.keys():
            index.append(en_voc_dic['unk'])
        else:
            index.append(en_voc_dic[to])
    return index

def get_cal_list(bleulist, **therest):
    cal_list = []
    top = 1
    if 'top' in therest.keys():
        top = int(therest['top'])
    if 'construct' in therest.keys():
        if therest['construct'] == '4train':
            if top == 1:
                cal_list.append(bleulist.index(max(bleulist)))# the first one is positive
                cal_list.append(bleulist.index(min(bleulist)))
            elif top > 1:
                sb = sorted(bleulist)
                for i in range(top):
                    cal_list.append(bleulist.index(sb[i]))
                for i in range(top):
                    cal_list.append(bleulist.index(sb[-i]))
    elif therest['construct'] == '4test':
        for i in range(len(bleulist)):# 所有的index都加进去
            cal_list.append(i)
    return cal_list

import math
import time
def get_ibm_bestfueture_in_libin(ch_voc_dic, en_voc_dic, ibm_dic, align, source, trans, bleu, **therest):
    # 得到中英文词，得到matched parentheses（括号。） + matched quotation marks(ratio?)
    fr = codecs.open(trans, 'r')
    frs = codecs.open(source, 'r')
    fra = codecs.open(align, 'r')
    frb = codecs.open(bleu, 'r')
    top = 1
    construct = ''
    if 'top' in therest.keys():
        top = int(therest['top'])
    if 'construct' in therest.keys():
        construct = str(therest['construct'])
        fw = codecs.open(trans + '.addfeat.' + str(therest['construct']) + "top" + str(top), 'w')
    line = fr.readline()
    linea = fra.readline()
    lineb = frb.readline()

    while line:
        # print "while", line, " line.__contains__('Sent Id')",  line.__contains__('Sent Id')
        if line.__contains__('Sent Id'):
            print line.split(':')[0]
            tmphyp_tokens_list = []
            linealist = []
            # senid = line.split(":")[0].replace('Sent Id', '')
            # source_tokens = line[line.find(':') + 1:].strip()# 你这又一次犯傻为哪班啊！！！！！！心累。。。这样这里就变成非Unicode操作了？
            source_line = frs.readline()
            source_tokens = source_line.strip().split()
            # 此处Unicode，你不要随便转成str啊。。。原来的文件格式要一致。。。然后不用各种码转换
            # source_tokens_index = [ch_voc_dic[str(x)] for x in line.strip().split(':')[1].split()]# look up voc table to get index, all in voc table(assume)
            source_tokens_index = get_voc_index(ch_voc_dic, source_tokens)
            bleulist = []
            lineb = frb.readline()# 只有在sentid一行需要读，在====分割不需要，因为blue并没有这个分割。。
        else:
            while not line.__contains__('========'):
                tmphyp_tokens_list.append(line.strip().split())
                # this one is not needed, just waste time
                linealist.append(linea)
                bleulist.append(float(lineb.strip().split(':')[1]))
                line = fr.readline()
                linea = fra.readline()
                lineb = frb.readline()

            # print bleulist, s2tDiclist,  tmphyp_tokens_list, tmphyp_tokens_index_list,
            cal_list = get_cal_list(bleulist, construct=construct, top=top)

            if len(cal_list) > 0:
                for index in cal_list:
                    s2tDic, source_posi_set = s2tdic(linealist[index], start='1')
                    p, r = get_qu_match(source_tokens, tmphyp_tokens_list[index], s2tDic)
                    trans_tokens_index = get_voc_index(en_voc_dic, tmphyp_tokens_list[index])
                    tmpP = get_ibm_sent(s2tDic, source_tokens_index, trans_tokens_index, ibm_dic)
                    fw.write(str(tmpP) +  ' ' + str(p) + ' ' + str(r) + '\n')

        line = fr.readline()
        linea = fra.readline()

    fr.close()
    fra.close()
    frb.close()
    fw.close()
    # 根据align 得到中英文词（通过trans得到）
    # 根据中英文词，找到对应voc下标
    # 生成key,到ibm找概率

def get_ibm_sent(s2tDic,  source_tokens_index, trans_tokens_index, ibm_dic):
    # start = time.time()
    tmpP = 0.0
    for s in s2tDic.keys():# index in sentence
        ta = s2tDic[s]# may be a list with more 2
        for t in ta:
            # use original index in sentence to find the index in voc
            # print index, s, t, source_tokens_index, tmphyp_tokens_index_list[index]
            # key = str(source_tokens_index[int(s)]) + '_' + str(trans_tokens_index[int(t)])
            try:
                tmpP += math.log10(ibm_dic[str(source_tokens_index[int(s)])][str(trans_tokens_index[int(t)])])
            except:
                tmpP += 0
    return tmpP


def get_qu_match(chtokens, entokens, align):
    quotech = ['(', ')', ',', '.', '。', '%', ';', '”','“','·']
    quoteen = ['(', ')', ',', '.', '.', '%', ';', '"','"','·' ]
    totalch = 0.0
    match = 0.0
    totalen = 0.0
    for i in range(len(chtokens)):
        if chtokens[i] in quotech:
            totalch += 1
            if str(i) in align.keys():#if no align, do nothing
                align_indexs = align[str(i)]# maybe a list with more than align, align_indexs are index in entokens
                for index in align_indexs:
                    if entokens[int(index)] == quoteen[quotech.index(chtokens[i])]:

                        match += 1
                        continue
    for et in entokens:
        if et in quoteen:
            totalen += 1
    if match == 0:
        return 0.0, 0.0

    else:
        return match/totalch, match/totalen




def get_ibm_other4train():
    print 'mt02'
    ch_voc_dic = getvoc("IBM\\corpus.ch.vcb.mt02.ce.dev.c")
    print len(ch_voc_dic), "len(ch_voc_dic)",
    en_voc_dic = getvoc("IBM\\corpus.en.vcb")
    print len(en_voc_dic), "len(en_voc_dic)",
    ibm_dic = getibm("IBM\\s2t64.t1.5.filter2")
    print len(ibm_dic), "len(ibm_dic)"
    for i in range(2, 4):
        print i
        get_ibm_bestfueture_in_libin4train(ch_voc_dic, en_voc_dic, ibm_dic,
                                       "decode" + str(i) + "\\run" + str(i) + ".mt02.output.derivation.txt.align",
                                       "IBM\\mt02.ce.dev.c",
                                       "decode" + str(i) + "\\run" + str(i) + ".mt02.output.derivation.txt.trans",
                                       "decode" + str(i) + "\\run" + str(i) + ".mt02.output.derivation.txt.trans2.bleu")

if __name__=="__main__":
    file_n = '3'
    # ch_voc_dic = getvoc("IBM\\corpus.ch.vcb.mt0" + file_n + ".ce.dev.c")
    # print len(ch_voc_dic), "len(ch_voc_dic)",
    # en_voc_dic = getvoc("IBM\\corpus.en.vcb")
    # print len(en_voc_dic), "len(en_voc_dic)",
    # ibm_dic = getibm("IBM\\s2t64.t1.5.filter" + file_n + "")
    # print len(ibm_dic), "len(ibm_dic)"
    for i in range(1, 4):
        print "decode", i
        get_pos_senquence4train("decode" + str(i) + "\\run" + str(i) + ".mt0" + file_n + ".output.derivation.txt.align",
         "decode" + str(i) + "\\run" + str(i) + ".mt0" + file_n + ".output.derivation.txt.trans",
         "M:\\MT100best\\poslm\\MT02-06\\MT0" + file_n + ".ce.tree.dev.berkekeytree.postag",
         "decode" + str(i) + "\\run" + str(i) + ".mt0" + file_n + ".output.derivation.txt.trans2.bleu",
         top=10)
        # get_ibm_bestfueture_in_libin(ch_voc_dic, en_voc_dic, ibm_dic,
        #                                "decode" + str(i) + "\\run" + str(i) + ".mt0" + file_n + ".output.derivation.txt.align",
        #                                "IBM\\mt0" + file_n + ".ce.dev.c",
        #                                "decode" + str(i) + "\\run" + str(i) + ".mt0" + file_n + ".output.derivation.txt.trans",
        #                                "decode" + str(i) + "\\run" + str(i) + ".mt0" + file_n + ".output.derivation.txt.trans2.bleu",
        #                                construct='4train', top=10)
    # calculateBule()
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
    # foldlist = ['1', "2", "3"]
    # for fold in foldlist:
    #     # get_pos_senquence("decode" + fold + "\\run" + fold + ".mt06.output.derivation.txt.align",
        #                     "decode" + fold + "\\run" + fold + ".mt06.output.derivation.txt.trans",
        #                     "M:\\MT100best\\poslm\\MT02-06\\MT06.ce.tree.dev.berkekeytree.postag",
        #                     "decode" + fold + "\\run" + fold + ".mt06.output.derivation.txt.trans2.bleu")
    #
    # get_pos_senquence4train("decode3\\run3.mt03.output.derivation.txt.align",
    #                         "decode3\\run3.mt03.output.derivation.txt.trans",
    #                         "M:\\MT100best\\poslm\\MT02-06\\MT03.ce.tree.dev.berkekeytree.postag",
    #                         "decode3\\run3.mt03.output.derivation.txt.trans2.bleu")

