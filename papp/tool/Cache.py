# -*- coding: UTF-8 -*-
# Developed by @mario 1.1.20230213
from .Common import *


class Cache(object):
    @staticmethod
    def remember(key, callback, expire=0):
        if callback is None or (type(callback) == str and len(callback) == 0):
            return None
        if Config.cache_type == 'redis':
            r = Redis()
            if r.ping():
                ret = r.get(md5(key))
                if ret is not None:
                    return json_decode(ret)
                value = callback() if callable(callback) else callback
                r.set(md5(key), json_encode(value))
                if expire > 0:
                    r.expire(md5(key), expire)
                return value
        filename = md5(key)
        cacheDir = Path(runtime_path() + '/cache')
        if cacheDir.is_dir():
            cacheFile = Path('{}/{}'.format(cacheDir, filename))
            if cacheFile.is_file():
                if expire == 0 or (int(time.time()) - int(os.path.getmtime(cacheFile)) < expire):
                    fo = open('{}'.format(cacheFile), 'r')
                    data = fo.read()
                    fo.close()
                    return json_decode(data)
        value = callback() if callable(callback) else callback
        makedir(cacheDir)
        fo = open('{}/{}'.format(cacheDir, filename), 'w+')
        fo.write(json_encode(value))
        fo.close()
        return value

    @staticmethod
    def delete(key):
        if Config.cache_type == 'redis':
            r = Redis()
            if r.ping():
                if r.exists(md5(key)):
                    r.delete(md5(key))
                return
        filename = md5(key)
        cacheDir = Path(runtime_path() + '/cache')
        if cacheDir.is_dir():
            cacheFile = '{}/{}'.format(cacheDir, filename)
            if os.path.isfile(cacheFile):
                os.remove(cacheFile)
