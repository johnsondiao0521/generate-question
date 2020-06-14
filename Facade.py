# coding: utf-8
from EventGenerator import *
from QuestionGenerator import *
'''
@brief offer user events or questions
@param[in] string  sentences
@return list  events or questions
'''


class Facade:
    def __init__(self):
        self.eventGenerator = EventGenerator()
        self.questionGenerator = QuestionGenerator()

    def generateEvents(self, sentences):
        events = self.eventGenerator.generateEvents(sentences)
        return events

    def generateQuestions(self, sentences):
        events = self.eventGenerator.generateEvents(sentences)
        questions = self.questionGenerator.generateQuestions(events)
        return questions


def test():
    facade = Facade()
    sentences = '''今年 的 暑假 是 王家明 升上 高中 的 第一 个 暑假 ， 他 的 父母 认为 高中生 也 算是 半 个 大人 了 ， 所以 就 放任 家明 自己 规划 。'''
    questions = facade.generateQuestions(sentences)
    print(questions)


#test()