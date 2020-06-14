import os
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller, SentenceSplitter


class ModelLoader:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(ModelLoader, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if (self.__initialized): return
        self.__initialized = True
        LTP_DIR = "./ltp_data"
        #客製化分詞，並且後處理更改詞性
        self.segmentor = Segmentor()
        self.segmentor.load_with_lexicon(
            os.path.join(LTP_DIR, "cws.model"),
            os.path.join(LTP_DIR, 'customized.txt'))

        self.postagger = Postagger()
        self.postagger.load(os.path.join(LTP_DIR, "pos.model"))

        self.parser = Parser()
        self.parser.load(os.path.join(LTP_DIR, "parser.model"))

        self.recognizer = NamedEntityRecognizer()
        self.recognizer.load(os.path.join(LTP_DIR, "ner.model"))

        self.labeller = SementicRoleLabeller()
        self.labeller.load(os.path.join(LTP_DIR, 'pisrl.model'))

        self.sentenceSplitter = SentenceSplitter()


def test():
    modelloader = ModelLoader()
    print("go next step")


#test()