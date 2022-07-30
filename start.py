from flask import Flask, render_template
import logging
from papp.tool import *
from werkzeug.routing import BaseConverter


class WildcardConverter(BaseConverter):
    regex = r'.*?'
    weight = 200


# https://www.cnblogs.com/DragonFire/p/9255637.html
server = Flask(__name__)
server.url_map.converters['reg'] = WildcardConverter  # 初始化转换器
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@server.route('/', methods=['GET'])
@server.route('/index', methods=['GET'])
def start(): return index('index')


@server.route('/index/<reg:path>')
@server.route('/admin/<reg:path>')
def index(path):
    module = 'index'
    app = 'index'
    act = 'index'
    if len(path) > 0:
        paths = path.split('/')
        module = paths[0]
        if len(paths) > 1 and len(paths[1]) > 0:
            app = paths[1]
            if len(paths) > 2 and len(paths[2]) > 0:
                act = paths[2]
    ret = getMethod('papp.controller.'+module.lower()+'.'+app.capitalize(), act.lower())
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
    server.run(host='127.0.0.1', port=5000, debug=True)
    # server.run(host='0.0.0.0', port=5000)
