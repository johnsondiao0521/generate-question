from ModelLoader import *
from EventGenerator import *


class QuestionGenerator:
    def __init__(self):
        self.modelLoader = ModelLoader()
        self.sentenceSplitter = self.modelLoader.sentenceSplitter
        self.segmentor = self.modelLoader.segmentor
        self.postagger = self.modelLoader.postagger
        self.parser = self.modelLoader.parser
        self.recognizer = self.modelLoader.recognizer
        self.labeller = self.modelLoader.labeller

    def generateQuestions(self, events):
        recordName = []
        f = open('./ltp_data/customized.txt')
        for line in f:
            recordName.append(line.strip('\n'))
        f.close()
        questions = []
        for i, event in enumerate(events):
            if self.postagger.postag(event)[0] == 'nh' or event[
                    0] in recordName or self.checkIfPerson(
                        event[0], recordName):
                questions.append(event[0] + event[1] + '什麼?')
        return questions

    #bruteforce
    def checkIfPerson(self, s, recordName):
        for record in recordName:
            if s.find(record) != -1:
                return True
        return False


def test():
    questionGenerator = QuestionGenerator()
    eventGenerator = EventGenerator()
    sentences = '''今年 的 暑假 是 王家明 升上 高中 的 第一 个 暑假 ， 他 的 父母 认为 高中生 也 算是 半 个 大人 了 ， 所以 就 放任 家明 自己 规划 。'''
    events = eventGenerator.generateEvents(sentences)
    questions = questionGenerator.generateQuestions(events)
    print(questions)


#test()