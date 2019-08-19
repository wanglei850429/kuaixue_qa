#!/usr/bin/python
from flask import Flask,make_response
from flask_restful import reqparse, Api
import sys
import os
import time
sys.path.append('../')
from api.qa_api import Questions,Answer,QuestionsAndAnswers,UserWords,StopWords
import conf.config

app = Flask(__name__)
#供elasticsearch ik插件监听调用，如用户更新了停用词表，ES监听并调用此接口完成热更新
@app.route("/update/stop_word")
def updateStopWord():
    resp = make_response()
    resp.headers['Last-Modified'] = str(time.ctime(os.path.getmtime(conf.config.STOP_WORDS)))
    resp.headers['ETag'] = str(time.ctime(os.path.getmtime(conf.config.STOP_WORDS)))
    resp.headers['content_type'] = 'text/plain;charset=utf-8'
    stopwords=''
    if os.path.exists(conf.config.STOP_WORDS):
        with open(conf.config.STOP_WORDS, 'r', encoding='utf-8') as f:
            stopwords = f.read()
    resp.response = stopwords
    return resp
#供elasticsearch ik插件监听调用，如用户更新了专有词表，ES监听并调用此接口完成热更新
@app.route("/update/user_word")
def updateUserWord():
    resp = make_response()
    resp.headers['Last-Modified'] = str(time.ctime(os.path.getmtime(conf.config.USER_WORDS)))
    resp.headers['ETag'] = str(time.ctime(os.path.getmtime(conf.config.USER_WORDS)))
    resp.headers['content_type'] = 'text/plain;charset=utf-8'
    userwords=''
    if os.path.exists(conf.config.USER_WORDS):
        with open(conf.config.USER_WORDS, 'r', encoding='utf-8') as f:
            userwords = f.read()
    resp.response = userwords
    return resp

# 跨域支持
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = '*'
    return resp

if __name__ == '__main__':
    app.after_request(after_request)
    api = Api(app)
    api.add_resource(Questions, '/QA/q/<question>')
    api.add_resource(Answer, '/QA/a/<question>/<id>')
    api.add_resource(UserWords, '/QA/user_word/<word>')
    api.add_resource(StopWords, '/QA/stop_word/<word>')
    api.add_resource(QuestionsAndAnswers, '/QA/add/<question>/<answer>')

    parser = reqparse.RequestParser()
    parser.add_argument('arg', type=str)

    app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
    app.run(debug=True)