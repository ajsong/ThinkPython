# Developed by @mario 1.0.20220817
from .Common import *
from flask import request, render_template


# https://www.88ksk.cn/blog/22.html
class Request(object):

    def get(self, name, default=''):
        return self.act(name, default, 'get')

    def post(self, name, default=''):
        return self.act(name, default, 'post')

    def request(self, name, default=''):
        return self.act(name, default, 'request')

    def file(self, name, path=''):
        return self.act(name, path, 'file')

    def json(self, name, default=None):
        return self.act(name, default, 'json')

    def data(self, name, default=None):
        return self.act(name, default, 'data')

    def header(self, name, default=''):
        return self.act(name, default, 'header')

    def cookie(self, name, default=''):
        return self.act(name, default, 'cookie')

    def isPost(self):
        return request.method.upper() == 'POST'

    def isAjax(self):
        return request.headers.get('X-Requested-With', '').lower() == 'xmlhttprequest'

    def url(self):
        return request.url

    def host(self):
        return request.url_root

    def path(self):
        return request.path

    def act(self, name, default='', method='get'):
        if method.lower() == 'get':
            return request.args.get(name, default)
        elif method.lower() == 'post':
            return request.form.get(name, default)
        elif method.lower() == 'request':
            return request.values.get(name, default)
        elif method.lower() == 'file':
            storage = request.files.get(name, None)
            if storage is None:
                return None
            path = '/uploads/' + default + date('/%Y/%m/%d')
            makedir(path)
            filepath = path + '/' + generate_sn() + '.' + storage.filename.split('.')[-1]
            storage.save(root_path() + filepath)
            return filepath
        elif method.lower() == 'json':
            res = request.json
            if res is None:
                return default
        elif method.lower() == 'data':
            res = json_decode(request.data)
            if res is None:
                return default
        elif method.lower() == 'header':
            return request.headers.get(name, default)
        elif method.lower() == 'cookie':
            return request.cookies.get(name, default)
        return default
