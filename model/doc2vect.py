import jieba
import jieba.posseg as psg
from scipy.linalg import norm
import gensim
import numpy as np

import sys

sys.path.append('../')
from utils.utils import Utils

INFILE1 = '../data/seg_question.txt'
OUTFILE = '../data/question.doc2vec'


def save_model(input, output):
    q = []
    with open(input, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            q.append(line)
    docs = []
    for i, text in enumerate(q):
        document = gensim.models.doc2vec.TaggedDocument(text.split(' '), [i])
        docs.append(document)
    model = gensim.models.doc2vec.Doc2Vec(docs,min_count=1, window = 3, vector_size = 100, sample=1e-3, negative=5, workers=4,dm=0)
    model.train(docs, total_examples=model.corpus_count, epochs=70)
    model.save(output)


def load_d2v_model(model_file):
    model = gensim.models.doc2vec.Doc2Vec.load(model_file)
    return model


def doc_vector_similarity(s1, s2, model):
    # 取停顿词
    stopwords = Utils.get_stop_words()

    def doc_vector(s):
        # words = jieba.lcut(s)
        Utils.load_user_words()
        words = [x for x in jieba.cut(s, cut_all=False) if x not in stopwords]
        words = list(filter(lambda x: not x.isdigit(), words))
        words = [word.lower().strip() for word in words]
        v = model.infer_vector(words)
        return v

    v1, v2 = doc_vector(s1), doc_vector(s2)
    # 余弦相似度(Cosine Similarity)
    return np.dot(v1, v2) / (norm(v1) * norm(v2))
