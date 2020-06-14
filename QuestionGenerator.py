from ModelLoader import *


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
