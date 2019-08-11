import sys
sys.path.append('../')
from es.es_model import ES_Model
from flask_restful import Resource
from model.order import order_by_embed_vector
import conf.config
import re

es_model = ES_Model(conf.config.ES_INIT_INPUT_FILE, conf.config.INDEX_NAME, conf.config.STOP_WORDS, conf.config.ES_INIT)
#根据用户输入的问题及前端传来的问题ID，检索出最相近的问题或该问题ID的子问题
class Questions(Resource):
    def get(self, question):
        es_result = es_model.get_topn_sims_q(str(question))
        result = order_by_embed_vector(es_result, str(question))
        return result

#根据用户输入的问题，问题ID，精确匹配出回答
class Answer(Resource):
    def get(self, question, id):
        pattern = re.compile(r'\d{6}')
        if pattern.match(id):
            result = es_model.get_answer_by_id(str(question), id)
        else:
            es_result = es_model.get_topn_sims_q(str(question))
            temp_result = order_by_embed_vector(es_result, str(question))
            result =[item[2:] for item in temp_result]
        return result

class QuestionsAndAnswers(Resource):
    def get(self, id,question,answer):
        # es_result = es_model.get_topn_sims_anwser(str(question))
        # result = order_by_word2vector(es_result, question)
        return None
    def post(self,id,question,answer):
        es_model.insert_data(id,question,answer)
        return 'success',201




#用户追加专有字典接口
class UserWords(Resource):
    def post(self,word):
        try:
            with open(conf.config.USER_WORDS,'a+',encoding='utf-8') as f:
                f.write(word)
                f.write('\n')
        except Exception as e:
            return str(e),400
        return 'success',201

    def delete(self,word):
        try:
            lines = []
            with open(conf.config.USER_WORDS,'r',encoding='utf-8') as f_in:
                for line in f_in.readlines():
                    if line.strip() != word:lines.append(line)
            with open(conf.config.USER_WORDS,'w',encoding='utf-8') as f_out:
                f_out.writelines(lines)
        except Exception as e:
            return str(e),400
        return 'success',201
#用户追加停用词接口
class StopWords(Resource):
    def post(self,word):
        try:
            with open(conf.config.STOP_WORDS,'a+',encoding='utf-8') as f:
                f.write(word)
                f.write('\n')
        except Exception as e:
            return str(e),400
        return 'success',201

    def delete(self,word):
        try:
            lines = []
            with open(conf.config.STOP_WORDS, 'r', encoding='utf-8') as f_in:
                for line in f_in.readlines():
                    if line.strip() != word: lines.append(line)
            with open(conf.config.STOP_WORDS, 'w', encoding='utf-8') as f_out:
                f_out.writelines(lines)
        except Exception as e:
            return str(e), 400
        return 'success', 201





