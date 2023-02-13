# -*- coding: UTF-8 -*-
from flask import Flask, render_template
import logging
from argparse import ArgumentParser
from papp.tool import *
from werkzeug.routing import BaseConverter


class WildcardConverter(BaseConverter):
    regex = r'.*?'
    weight = 200


# https://blog.csdn.net/Lin_Hv/article/details/113112527
# https://www.cnblogs.com/DragonFire/p/9255637.html
# pip install flask
app = Flask(__name__)
app.url_map.converters['reg'] = WildcardConverter  # 初始化转换器
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def start(): return index('index')


@app.route('/index/<reg:path>')
@app.route('/admin/<reg:path>')
def index(path):
    module = 'index'
    controller = 'index'
    action = 'index'
    if len(path) > 0:
        paths = path.split('/')
        module = paths[0]
        if len(paths) > 1 and len(paths[1]) > 0:
            controller = paths[1]
            if len(paths) > 2 and len(paths[2]) > 0:
                action = paths[2]
    ret = getMethod('papp.controller.'+module.lower()+'.'+controller.capitalize(), action.lower())
    if ret is None:
        return '', 400
    if type(ret) == render_template:
        # https://www.cnblogs.com/DragonFire/p/9259999.html
        return ret
    if type(ret) != str:
        ret = json_encode(ret)
    return ret, 200


# c = server.test_client()
# res = c.get('/index/').data
# print(str(res, 'UTF-8'))  #res为bytes字节串

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', type=str, help='Server host')
    parser.add_argument('--port', default=5000, type=int, help='Server port')
    args = parser.parse_args()
    # server.run(host=args.host, port=args.port)

    # pip install waitress
    from waitress import serve
    serve(app, host=args.host, port=args.port)
