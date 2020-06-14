# coding: utf-8
from SentenceProcessor import *
import re
from pyltp import SentenceSplitter


class EventGenerator:
    def __init__(self):
        self.parser = SentenceProcessor()

    '''對找出的主語或者賓語進行擴展'''

    def completeEvent(self, words, postags, child_dict_list, word_index):
        child_dict = child_dict_list[word_index]
        prefix = ''
        if 'ATT' in child_dict:
            for i in range(len(child_dict['ATT'])):
                prefix += self.completeEvent(words, postags, child_dict_list,
                                             child_dict['ATT'][i])
        postfix = ''
        if postags[word_index] == 'v':
            if 'VOB' in child_dict:
                postfix += self.completeEvent(words, postags, child_dict_list,
                                              child_dict['VOB'][0])
            if 'SBV' in child_dict:
                prefix = self.completeEvent(words, postags, child_dict_list,
                                            child_dict['SBV'][0]) + prefix

        return prefix + words[word_index] + postfix

    '''利用語義角色標註,直接獲取主謂賓三元组,基於A0,A1,A2'''

    def ruler1(self, words, postags, roles_dict, role_index):
        # ###紀錄NER，人   直接在sentence_parser.parser_main將word改成NER
        # NER_list = self.parser.getNER(words, postags)
        # ###
        v = words[role_index]
        role_info = roles_dict[role_index]
        if 'A0' in role_info.keys() and 'A1' in role_info.keys():
            s = ''.join([
                words[word_index] for word_index in range(
                    role_info['A0'][1], role_info['A0'][2] + 1)
                if postags[word_index][0] not in ['w', 'u', 'x']  #確認詞性非w,u,x
                and words[word_index]  #確認head有word
            ])

            o = ''.join([
                words[word_index] for word_index in range(
                    role_info['A1'][1], role_info['A1'][2] + 1)
                if postags[word_index][0] not in ['w', 'u', 'x']
                and words[word_index]
            ])
            if s and o:
                return '1', [s, v, o]
        # elif 'A0' in role_info:
        #     s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2] + 1) if
        #                  postags[word_index][0] not in ['w', 'u', 'x']])
        #     if s:
        #         return '2', [s, v]
        return '3', []

    '''三元組抽取主函数'''

    def ruler2(self, words, postags, child_dict_list, arcs, roles_dict):
        svos = []
        for index in range(len(postags)):
            tmp = 1
            # 先借助語義角色標註的结果，進行三元組抽取
            if index in roles_dict:
                flag, triple = self.ruler1(words, postags, roles_dict, index)
                if flag == '1':
                    svos.append(triple)
                    tmp = 0
            # 如果語意角色標記為空，則使用依存句法進行抽取
            if tmp == 1:
                ###紀錄NER，人
                NER_list = self.parser.getNER(words, postags)
                ###
                # if postags[index] == 'v':
                if postags[index]:
                    # 抽取以謂詞為中心的事實三元组
                    child_dict = child_dict_list[index]
                    # 主謂賓
                    if 'SBV' in child_dict and 'VOB' in child_dict:
                        r = words[index]
                        e1 = self.completeEvent(words, postags,
                                                child_dict_list,
                                                child_dict['SBV'][0])
                        e2 = self.completeEvent(words, postags,
                                                child_dict_list,
                                                child_dict['VOB'][0])
                        svos.append([e1, r, e2])
                    # 含有介賓關(不及物v + 介詞 + 賓語)的主謂動補關係
                    if 'SBV' in child_dict and 'CMP' in child_dict:
                        e1 = self.completeEvent(words, postags,
                                                child_dict_list,
                                                child_dict['SBV'][0])

                        cmp_index = child_dict['CMP'][0]
                        r = words[index] + words[cmp_index]

                        if 'POB' in child_dict_list[cmp_index]:
                            e2 = self.completeEvent(
                                words, postags, child_dict_list,
                                child_dict_list[cmp_index]['POB'][0])
                            svos.append([e1, r, e2])
                    # 定語後置(村中少年好事者 =>原本是村中好事者少年)，動賓關係

                    relation = arcs[index][0]
                    head = arcs[index][2]
                    if relation == 'ATT':
                        if 'VOB' in child_dict:
                            e1 = self.completeEvent(words, postags,
                                                    child_dict_list, head - 1)
                            r = words[index]
                            e2 = self.completeEvent(words, postags,
                                                    child_dict_list,
                                                    child_dict['VOB'][0])
                            ###########################################
                            ##########################################
                            temp_string = r + e2
                            if temp_string == e1[:len(temp_string)]:
                                e1 = e1[len(temp_string):]
                            if temp_string not in e1:
                                svos.append([e1, r, e2])
        return svos

    '''接口函数'''

    def generateEvents(self, sentences):
        #preprocess input sentence  #####################
        #####################################
        #先用pyltp作詞分句
        sentences = SentenceSplitter.split(sentences)
        #在把同一個人講的多句話放在同一句後面(放在parse裡的func)
        sentences = self.parser.SentenceSplit(sentences)

        #在句子前面加入講話者是誰
        catchPerson = {}
        for idx, sentence in enumerate(sentences):
            words = list(self.parser.segmentor.segment(sentence))
            postags = list(self.parser.postagger.postag(words))
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
        #####################
        #給出insertPerson : 人名 or None
        #####################
        #sentences = self.split_sents(sentences)

        events = []
        #對每一個句子
        for idx, sentence in enumerate(sentences):
            #sentence_parser定義的func，format_parse_list沒用到             #self.parser = LtpParser()
            words, postags, child_dict_list, roles_dict, arcs = self.parser.parser_main(
                sentence)
            #######################指代解析寫法           這裡要修改！！！！
            isChange = 0
            for index in range(len(words)):
                if postags[index] == 'r':
                    if words[index] == '我' and insertPerson[idx] != 'None':
                        words[index] = insertPerson[idx]
                        isChange = 1
                    if words[index] == '你' and idx - 1 >= 0 and insertPerson[
                            idx - 1] != 'None':
                        words[index] = insertPerson[idx - 1]
                        isChange = 1
            ######################
            svo = self.ruler2(words, postags, child_dict_list, arcs,
                              roles_dict)
            events += svo
        return events


def test():
    sentences = """今年 的 暑假 是 王家明 升上 高中 的 第一 个 暑假 ， 他 的 父母 认为 高中生 也 算是 半 个 大人 了 ， 所以 就 放任 家明 自己 规划 。"""
    eventGenerator = EventGenerator()
    events = eventGenerator.generateEvents(sentences)
    print('events', events)


#test()
