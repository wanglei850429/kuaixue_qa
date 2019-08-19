import sys
import numpy as np
import jieba
import jieba.posseg as psg
from scipy.special import perm
sys.path.append('../')

from model.word2vect import load_model, vector_similarity
from model.doc2vect import load_d2v_model, doc_vector_similarity
from utils.utils import Utils
from model.seq2seq import Seq2seq
import conf.config

word_vector_model = load_model(conf.config.W2V_MODEL)
doc_vector_model = load_d2v_model(conf.config.D2V_MODEL)
seq2seq = Seq2seq()

def eval_by_vector_simliarity(es_question, question):
    # 根据已经学习好的词向量，对结果进行重排序
    if conf.config.VEC_MODE == 'DOC2VEC':
        score = doc_vector_similarity(question, es_question, doc_vector_model)
    else:
        score = vector_similarity(question, es_question, word_vector_model)
    return score

def get_sentence_segment(sentence):
    sent = jieba.lcut(sentence)
    sent = [s for s in sent if s not in Utils.get_stop_words()]
    return sent

def eval_by_sentence_length(es_question, question):
    question_len = float(len(get_sentence_segment(question)))
    es_result_len = float(len(get_sentence_segment(es_question)))
    if question_len+es_result_len == 0:return 0
    score = 1.0 - (abs(question_len-es_result_len)/(question_len+es_result_len))
    return score

def get_key_words(text):
    return [w for w,t in psg.cut(text) if t in ['ng','n','nr','ns','nt','nz','v','vg','vd','vn','eng']]

def get_inverse_num(pos_array):
    number = 0

    def sort(a, b):
        ll = len(a)
        lr = len(b)
        nonlocal number
        a.append(float('inf'))
        b.append(float('inf'))
        c = []
        i, j = 0, 0
        for _ in range(ll + lr):
            if a[i] <= b[j]:
                c.append(a[i])
                i += 1
            else:
                c.append(b[j])
                j += 1
                number += ll - i
        return c

    def div(l):
        if len(l) <= 1:
            return l
        mid = len(l) // 2
        left = div(l[:mid])
        right = div(l[mid:])
        return sort(left, right)

    div(pos_array)
    return number

def eval_by_inverse_rate(es_question, question):
    question_key_word = get_key_words(question)
    word_pos_dict = {}
    for pos,word in enumerate(question_key_word):
        if word not in word_pos_dict.keys():
            word_pos_dict[word] = pos
    es_result_key_word = get_key_words(es_question)
    pos_array = []
    processed_word = []
    for word in es_result_key_word:
        if word in word_pos_dict.keys() and word not in processed_word:
            pos_array.append(word_pos_dict[word])
            processed_word.append(word)
    duplicate_word = len(list(set(question_key_word).intersection(set(es_result_key_word))))
    inverse_num = get_inverse_num(pos_array)
    score = 1.0 - (float(inverse_num)/float(perm(duplicate_word,duplicate_word)))
    return score

def eval_by_key_word_num(es_question, question):
    query_key_words = get_key_words(question)
    query_key_words = list(set(query_key_words))
    es_result_key_words = get_key_words(es_question)
    es_result_key_words = list(set(es_result_key_words))
    num = 0
    for word in query_key_words:
        if word in es_result_key_words:
            num+=1
    if len(query_key_words)==0:return 0
    score = float(num)/float(len(query_key_words))
    return score


def order_by_embed_vector(es_result, question,n=5):
    order_result = []
    for key,item in es_result['result2'].items():
        r = {}
        r['index'] = item['index']
        r['title'] = item['title']
        r['answer'] = item['answer']
        # r.append(item['index'])
        # r.append(item['title'])
        # r.append(item['answer'])
        vec_score = eval_by_vector_simliarity(item['title'], question)
        len_score = eval_by_sentence_length(item['title'], question)
        inv_score = eval_by_inverse_rate(item['title'], question)
        kv_score = eval_by_key_word_num(item['title'], question)
        score = 0.3*vec_score + 0.2*len_score +0.3*kv_score+ 0.2*inv_score
        r['score'] = round(score,3)
        order_result.append(r)
    order_result = sorted(order_result, key=lambda x: x['score'], reverse=True)
    order_result = order_result[:n]
    if conf.config.DEBUG:
        print('\n---------------------------------------------------------')
        print('词向量重排后的结果：')
        for i in order_result:
            print('---------------------------------------------------------')
            print('问题: %s' % (i[1]))
            print('答案:%s' % (i[2]))
            print('相似度:%f' % (i[3]))
    if len(order_result) ==0 or order_result[0]['score'] < 0.4:
        predict = seq2seq.predict(es_result['result1']['title'])
        order_result = []
        r = {}
        r['index'] = ' '
        r['title'] = es_result['result1']['title']
        r['answer'] = predict
        r['score'] = '自动生成回复'
        order_result.append(r)
    return order_result