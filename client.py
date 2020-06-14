#coding=UTF-8

from Facade import *

sentences = '''今年 的 暑假 是 王家明 升上 高中 的 第一 个 暑假 ， 他 的 父母 认为 高中生 也 算是 半 个 大人 了 ， 所以 就 放任 家明 自己 规划 。'''

facade = Facade()
events = facade.generateEvents(sentences)
questions = facade.generateQuestions(sentences)

print('generate question:')
print(events)
print('\ngenerate question:')
print(questions)