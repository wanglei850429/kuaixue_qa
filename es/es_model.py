import jieba
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import re

class ES_Model():
    def __init__(self, input_file, index_name, stop_words_file, index, model_name='es'):
        self.input_file = input_file
        self.index_name = index_name
        self.stop_words_file = stop_words_file
        with open(self.stop_words_file, 'r',encoding='utf-8') as f:
            lines = f.readlines()
            self.stopwords = [line.strip() for line in lines]
        self.index = index
        self.build_model()

    def build_model(self):
        if self.index:
            self.es = Elasticsearch()
            # self.es = Elasticsearch([{'host':'192.168.99.100','port':9200}])
            self.set_mapping(self.es)
            print("Index data success")
            self.set_data(self.es, self.input_file)
            print("build mode success")
        else:
            self.es = Elasticsearch()
            # self.es = Elasticsearch([{'host': '192.168.99.100', 'port': 9200}])
            print("build mode success")

    #创建表 
    def set_mapping(self, es):
        my_mapping = {
            'settings':{
                'number_of_shards': 1,
                'number_of_replicas': 0,
                # 'analysis':{
                #     'filter':{
                #         'my_syno_filter':{
                #             'type':'synonym',
                #             'synonyms_path':'analysis/synonyms.txt'
                #         }
                #     },
                #     'char_filter':{
                #         'my_char_filter':{
                #             'type':'mapping',
                #             'mappings' : ['| => |']
                #         }
                #     },
                #     'analyzer':{
                #         'ik_syno_smart':{
                #             'type':'custom',
                #             'tokenizer':'ik_smart',
                #             'filter': ['my_syno_filter'],
                #             'char_filter' : ['my_char_filter']
                #         },
                #         'ik_syno_max_word': {
                #             'type': 'custom',
                #             'tokenizer': 'ik_max_word',
                #             'filter': ['my_syno_filter'],
                #             'char_filter': ['my_char_filter']
                #         }
                #     }
                # }
            },
            'mappings': {
                'properties': {
                    'question_id': {
                        'type': 'text'
                    },
                    'question': {
                        'type': 'text',
                        'analyzer': 'ik_max_word',
                        'search_analyzer': 'ik_smart',
                        'similarity': 'BM25'
                    },
                    'answer': {
                        'type': 'text'
                    },
                    'question_seg': {
                        'type': 'text',
                        'similarity': 'BM25'
                    },
                }
            }
        }
        #创建index之前先删除下
        es.indices.delete(index=self.index_name, ignore=[400, 404])
        #创建index
        result = es.indices.create(index=self.index_name, body=my_mapping)
        if not result['acknowledged']:
            print('create index failed')

    #插入数据
    def set_data(self, es, input_file):
        with open(input_file, "r", encoding='utf-8') as line_list:
            ACTIONS = []
            for line in line_list:
                fields = line.split('|')
                if len(fields) != 4:continue
                # print("fields:", fields)
                action = {
                    "_index" : self.index_name,
                    "_source":{
                        "question_id":fields[0],
                        "question":fields[1].rstrip(),
                        "anwser":fields[2].rstrip(),
                        "question_seg":fields[3].rstrip(),
                    },
                }
                ACTIONS.append(action)
            #批量处理
            success, _ = bulk(
                    es, ACTIONS, index=self.index_name, raise_on_error=True,request_timeout=100)
            print("Performed %d actions" % success)

    def insert_data(self,id,question,answer):
        data = {'question_id':id,'question':question,'answer':answer,'question_seg':' '.join(jieba.lcut(question))}
        self.es.index(self.index_name,body=data)

    @staticmethod
    def split_word(query, stopwords):
        words = jieba.cut(query)
        result = ' '.join(list(filter(lambda x: x not in stopwords, words)))
        return result


    def get_topn_sims_q(self, sentences, n=50):
        # split_sent = self.split_word(sentences, self.stopwords)
        split_sent = sentences
        results_1 = {'title': sentences, 'split_title': split_sent}
        query = {'query': {'match': {'question': split_sent}},'size':n}
        allDoc = self.es.search(index=self.index_name, body=query)
        results_2 = {}
        items = allDoc['hits']['hits']

        iter_num = min(n,len(items))
        for i in range(iter_num):
            each_results_2 = {'index': str(items[i]['_source']['question_id']),
                              'similarity': str(items[i]['_score']),
                              'title': items[i]['_source']['question'],
                              'answer':items[i]['_source']['anwser']}
            results_2[i] = each_results_2
        results = {'result1': results_1, 'result2': results_2}
        return results

    def get_answer_by_id(self,question,id):
        query = {'query':
                     {'bool':
                          {'must':[
                              {'match':{'question_id':id}},
                              {'match':{'question': question}}
                            ]}
                    }
                }
        allDoc = self.es.search(index=self.index_name, body=query)
        items = allDoc['hits']['hits']
        results = {'index': str(items[0]['_source']['question_id']),
                   'question': str(items[0]['_source']['question']),
                   'answer': str(items[0]['_source']['answer'])}
        return results

    def get_topn_sims_anwser(self, sentences, n = 5):
        split_sent = self.split_word(sentences, self.stopwords)
        results_1 = {'title':sentences, 'split_title':split_sent}

        query = {"query": 
                    {"bool": 
                        {"must": 
                            [{"query_string": 
                                {"default_field": "question", 
                                "query": split_sent
                                }
                            }]
                        }
                    }, 
                    "size": n
                }

        allDoc = self.es.search(index = self.index_name, body=query)
        if DEBUG:
            print(allDoc)

        results = []
        items = allDoc["hits"]["hits"]

        for item in items:
            record = []
            if DEBUG:
                print(item["_source"]["question_id"] + "\t" + item["_source"]["question"] + "\t" + item["_source"]["anwser"])
            record.append(item["_source"]["question_id"])
            record.append(item["_source"]["question"])
            record.append(item["_source"]["anwser"])
            results.append(record)
        return items