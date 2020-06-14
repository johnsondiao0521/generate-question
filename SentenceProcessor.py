# coding: utf-8

from ModelLoader import *


class SentenceProcessor:
    def __init__(self):
        self.modelLoader = ModelLoader()
        self.sentenceSplitter = self.modelLoader.sentenceSplitter
        self.segmentor = self.modelLoader.segmentor
        self.postagger = self.modelLoader.postagger
        self.parser = self.modelLoader.parser
        self.recognizer = self.modelLoader.recognizer
        self.labeller = self.modelLoader.labeller

    '''取得NER list'''

    def getNER(self, words, postags):
        persons, places, orgs = set(), set(), set()
        netags = list(self.recognizer.recognize(words, postags))
        # for index in range(len(netags)):
        #     if (netags[index] != 'O'):
        #         print(words[index])
        return netags

    '''語意角色標注'''

    def format_labelrole(self, words, postags):
        arcs = self.parser.parse(words, postags)
        roles = self.labeller.label(words, postags, arcs)
        roles_dict = {}
        #對於每一個謂詞
        for role in roles:
            roles_dict[role.index] = {
                #其他詞對此謂詞的角色(arg)
                arg.name: [arg.name, arg.range.start, arg.range.end]
                for arg in role.arguments
            }
        return roles_dict

    '''句法分析---為句子中的每個詞语維護一個保存句法依存兒子節點的字典'''

    #input : words, postags, arcs
    #output : child_dict_list(有哪些兒子，沒兒子的空白), format_parse_list(每一個詞都有)
    def build_parse_child_dict(self, words, postags, arcs):
        child_dict_list = []
        format_parse_list = []
        text = []  #檢查任意[]
        #time : O(n^2) 對每一個詞查看其他所有詞
        for index in range(len(words)):  #index為父，看index有哪些兒子
            child_dict = dict()
            for arc_index in range(len(arcs)):
                if arcs[arc_index].head == index + 1:  #arcs的索引從1開始
                    #arcs[arc_index].relation：子點與父親index的關係
                    if arcs[arc_index].relation in child_dict:
                        child_dict[arcs[arc_index].relation].append(arc_index)
                    else:
                        child_dict[arcs[arc_index].relation] = []
                        child_dict[arcs[arc_index].relation].append(arc_index)
            child_dict_list.append(child_dict)

        rely_id = [arc.head for arc in arcs]  # 提取依存父節點id
        relation = [arc.relation for arc in arcs]  # 提取依存关系
        heads = ['Root' if id == 0 else words[id - 1]
                 for id in rely_id]  # 匹配依存父節點詞語，把他父親是誰紀錄在heads
        for i in range(len(words)):
            #[與head的關係, 這是什麼, 這是哪裡(從0)，這是什麼詞，父是誰，父在哪，父的詞性]
            a = [
                relation[i], words[i], i, postags[i], heads[i], rely_id[i] - 1,
                postags[rely_id[i] - 1]
            ]
            format_parse_list.append(a)

        return child_dict_list, format_parse_list

    '''parser主函數'''

    def parser_main(self, sentence):
        words = list(self.segmentor.segment(sentence))
        postags = list(self.postagger.postag(words))
        #################################對postags進行後處理：若詞在customized.txt出現，則pos == 'nh'
        recordName = []
        f = open('./ltp_data/customized.txt')
        for line in f:
            recordName.append(line.strip('\n'))
        f.close()

        for idx, word in enumerate(words):
            if word in recordName:
                postags[idx] = 'nh'
        #################################
        netags = list(self.recognizer.recognize(words, postags))
        ##在此將words內為代名詞(r)的以右邊最近的NER:S-Nh代替
        # for index in range(len(words)):
        #     if postags[index] == 'r':
        #         if words[index] == '他' or words[index] == '你' or words[
        #                 index] == '我':
        #             #找右方最近的S-Nh
        #             for i in range(index, -1, -1):
        #                 if (netags[i] == 'S-Nh'):
        #                     words[index] = words[i]

        #################################################
        arcs = self.parser.parse(words, postags)

        child_dict_list, format_parse_list = self.build_parse_child_dict(
            words, postags, arcs)
        #roles_dict針對每個謂詞的語意角色
        roles_dict = self.format_labelrole(words, postags)
        return words, postags, child_dict_list, roles_dict, format_parse_list

    def SentenceSplit(self, sents):
        s = []
        a = ""
        for idx, sen in enumerate(sents):
            #print(idx, sen)
            if sen:
                a += sen
            # print(a)
            if not sen:
                s.append(a)
                a = ""
            #for the last one sentence
            if idx == (len(sents) - 1) and a:
                s.append(a)
        return s


if __name__ == '__main__':
    sentenceProcessor = SentenceProcessor()
    sentences = '''王家明
'''
    #preprocess input sentence
    #先用pyltp作詞分句
    sentences = sentenceProcessor.sentenceSplitter.split(sentences)
    #在把同一個人講的多句話放在同一句後面(放在sentenceProcessor裡的func)
    sentences = sentenceProcessor.SentenceSplit(sentences)

    #在句子前面加入講話者是誰
    catchPerson = {}
    for idx, sentence in enumerate(sentences):
        words = list(sentenceProcessor.segmentor.segment(sentence))
        postags = list(sentenceProcessor.postagger.postag(words))
        for i, postag in enumerate(postags):
            if postag == 'nh':
                catchPerson[idx] = words[idx]  # idx to person

    insertPerson = [None] * len(sentences)
    for i in range(len(sentences)):
        insertPerson[i] = 'None'
    for idx, sentence in enumerate(sentences):  #idx和sentence
        for key, recordPerson in catchPerson.items():  #記錄到的人(key, person)
            if key < idx and recordPerson not in sentence and recordPerson != 'alreadyUsed':
                insertPerson[idx] = recordPerson
                catchPerson[key] = 'alreadyUsed'

    for idx, person in enumerate(insertPerson):
        if idx - 2 >= 0 and insertPerson[idx - 2] != 'None':
            insertPerson[idx] = insertPerson[idx - 2]

    # print(insertPerson)
    # for i, sent in enumerate(sentences):
    #     print(i,sent)

    #用clss SentenceProcessor的object : sentenceProcessor 內的 parser_main   input : sentences
    for idx, sentence in enumerate(sentences):
        words, postags, child_dict_list, roles_dict, format_parse_list = sentenceProcessor.parser_main(
            sentence)

        ### 看NER : Nh:人名  Ni：機構名 Ns:地名（美美：Ns,Ns）
        NER_list = sentenceProcessor.getNER(words, postags)
        print('NER_LIST:', NER_list)
        print('\n')
        ### nh:person name  j:abbreviation(美英：j,j)   r:pronoun(這個, 你, 什麼,我)
        print(words, len(words))
        print('\n')
        print('詞性：', postags, len(postags))
        print('\n')
        #print(text, len(text))
        print('\n')
        print('child_dict_list:', child_dict_list, len(child_dict_list))
        print('\n')
        print('roles_dict:', roles_dict)
        print('\n')
        print(format_parse_list, len(format_parse_list))
        print('===========================================above is sentence',
              idx)
