# Developed by @mario 1.4.20220730
import decimal
import hashlib
import json
import shutil
import sys
import os
import random
import re
import time
from decimal import *
from pathlib import Path
import requests
from ..Config import *


# 修复json_encode的时候对象内有Decimal值报错的问题
class JSONDecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(JSONDecimalEncoder, self).default(o)


# 获取根目录
def root_path():
    return str(Path(__file__).resolve().parents[2])


# 获取运行时目录
def runtime_path():
    return root_path() + '/runtime'


# 正则匹配
def preg_match(pattern, string):
    return re.compile(pattern).match(str(string)) is not None


# 正则替换
def preg_replace(pattern, repl, string):
    return re.compile(pattern).sub(repl, str(string))


# 正则分割
def preg_split(pattern, string):
    return re.compile(pattern).split(str(string))


# 获取文件内容
def file_get_contents(file):
    if os.path.isfile(file) is False:
        print('The abi file does not exist')
        return None
    if os.access(file, os.R_OK) is False:
        print('The abi file does not read')
        return None
    fo = open(file, 'r')
    content = fo.read()
    fo.close()
    return content


# 写入文件内容, mode=a 追加
def file_put_contents(file, content='', mode='w'):
    fo = open(file, mode)
    fo.write(content)
    fo.close()


# 字符串日期转时间戳
def strtotime(dateStr):
    timeArray = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")  # 时间字符串解析为时间元组
    return int(time.mktime(timeArray))  # 将时间元组转换为时间戳


# 当前时间戳
def timestamp():
    return int(time.time())


# 时间戳转日期字符串
def date(formatStr="%Y-%m-%d %H:%M:%S", timeStamp=None):
    if timeStamp is None:
        timeStamp = time.localtime()
    else:
        timeStamp = time.localtime(timeStamp)
    return time.strftime(formatStr, timeStamp)


# json_encode
def json_encode(obj):
    if type(obj) == str:
        return obj
    return json.dumps(obj, ensure_ascii=False, cls=JSONDecimalEncoder)


# json_decode
def json_decode(jsonStr):
    try:
        return json.loads(jsonStr)
    except json.decoder.JSONDecodeError:
        return None


# json美化打印
def format_json(obj):
    if type(obj) == str:
        obj = json.loads(obj)
    print(json.dumps(obj, indent=4, ensure_ascii=False, sort_keys=True))


# md5
def md5(string):
    obj = hashlib.md5()
    obj.update(string.encode("utf-8"))
    return obj.hexdigest()


# sha1
def sha1(string):
    sha = hashlib.sha1(string.encode('utf-8'))
    return sha.hexdigest()


# 文件是否存在
def file_exist(file):
    return os.path.isfile(file)


# 创建多级目录,对应根目录
def makedir(path):
    path = root_path() + path.replace(root_path(), '')
    if not Path(path).is_dir():
        os.makedirs(path, 0o777)


# 删除目录,支持非空目录
def deletedir(path):
    path = root_path() + path.replace(root_path(), '')
    shutil.rmtree(path)


# 历遍目录
def listdir(path):
    path = root_path() + path.replace(root_path(), '')
    tups = os.walk(path)  # 函数walk()的返回值为三元组
    for root, dirs, files in tups:  # 遍历这个三元组
        for name in dirs:  # 遍历存放目录值的元组
            print('dir：', os.path.join(root, name))
        for name in files:  # 遍历存放文件名值的元组
            print('file：', os.path.join(root, name))


# 是否数字
def is_numeric(num):
    return re.compile(r'^-?\d+(\.\d+)?$').match(str(num)) is not None


# 验证手机号
def is_mobile(mobile):
    return re.compile(r'^13\d{9}$|^14[5,7]\d{8}$|^15[^4]\d{8}$|^17[03678]\d{8}$|^18\d{9}$').match(str(mobile)) is not None


# 验证座机
def is_tel(tel):
    return re.compile(r'^((\d{3,4}-)?\d{8}(-\d+)?|(\(\d{3,4}\))?\d{8}(-\d+)?)$').match(str(tel)) is not None


# 验证电话号码(包括手机号与座机)
def is_phone(phone):
    result = is_mobile(phone)
    if result:
        result = is_tel(phone)
    return result


# 验证邮箱
def is_email(email):
    return re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$').match(email) is not None


# 验证日期
def is_date(dateStr):
    return re.compile(r'^(?:(?!0000)\d{4}[/-](?:(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|1\d|2[0-8])|(?:0?[13-9]|1[0-2])[/-](?:29|30)|(?:0?[13578]|1[02])[/-]31)|(?:\d{2}(?:0[48]|[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)[/-]0?2[/-]29)$').match(str(dateStr)) is not None


# 生成随机字母数字
def random_str(length=4):
    string = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length_ = len(base_str) - 1
    for i in range(length):
        string += base_str[random.randint(0, length_)]
    return string


# 下划线转驼峰, small:小驼峰
def camelize(value, small=False, delimiter='_'):
    return re.sub(r'(%s\w)' % delimiter, lambda x: x.group(1)[1].upper(), ('' if small else delimiter) + value)


# 驼峰转下划线
def uncamelize(value, delimiter='_'):
    return re.sub(re.compile(r'([a-z]|\d)([A-Z])'), r'\1%s\2' % delimiter, value).lower()


# 写log文件
def write_log(content, filename="log.txt"):
    path = runtime_path()
    if not Path(path).is_dir():
        os.makedirs(path)
    file = Path("%s/%s" % (path, filename))
    if type(content) != str and type(content) != int and type(content) != float:
        content = json.dumps(content)
    fo = open("%s" % file, "a+")
    fo.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" + content + "\n\n")
    fo.close()


# 写error文件
def write_error(content):
    write_log(content, "error.txt")


# 网络请求
def requestUrl(method, url, params=None, returnJson=False, postJson=False, headers=None):
    method = method.upper()
    if url.startswith('https:') is False and url.startswith('http:') is False:
        url = apiUrl.rstrip('/') + '/' + url.lstrip('/')
    if headers is None:
        headers = {}
    if postJson:
        headers['Content-type'] = 'application/json;charset=UTF-8'
    if method == 'GET':
        res = requests.get(url=url, params=params, headers=headers)
    else:
        res = requests.post(url=url, data=params, headers=headers)
    if res.status_code == 301 or res.status_code == 302:
        return requestUrl(method, url, params, returnJson, postJson, headers)
    if res is None:
        return None
    if returnJson:
        return json.loads(res.text)
    return res.text


# 区块链数量去精度
def round_amount(value, scale=8, decimals=0):
    if decimals <= 0:
        decimals = scale
    amount = Decimal(str(value)) / Decimal('1'+'0'*decimals)
    if is_numeric(amount):
        amounts = str(amount).split('.')
        amount = amounts[0]
        if len(amounts) > 1:
            amount += '.' + amounts[1][:decimals]
    else:
        if preg_match(r'\d{'+str(decimals)+r'}$', value):
            amount = preg_replace(r'(\d{'+str(decimals)+r'})$', r'.\1', value)
        else:
            amount = '0' * decimals + value
            amount = preg_replace(r'(\d{'+str(decimals)+r'})$', r'.\1', amount)
            amount = '0' + preg_replace(r'^0+', '', amount)
    amounts = str(amount).split('.')
    amount = amounts[0]
    if len(amounts) > 1:
        amount += '.' + amounts[1][:scale]
    return amount


# 动态实例化对象
def instance(clazz):
    try:
        __import__(clazz)
    except ModuleNotFoundError:
        return None
    modules = clazz.split('.')
    return sys.modules.get(clazz).__getattribute__(modules[-1])


# 运行对象方法
def getMethod(clazz, method):
    obj = instance(clazz)
    if obj is not None:
        if hasattr(obj, method):
            return getattr(obj(), method)()
    return None


# 生成序列号
def generate_sn():
    return date('%y%m%d%H%M%S') + str(random.randint(10000, 99999))


# 随机范围内整数
def random_num(minNum=0, maxNum=sys.maxsize):
    return random.randint(minNum, maxNum)


# 随机范围内小数
def random_float(minNum=0, maxNum=1):
    return random.uniform(minNum, maxNum)


# success
def success(data=None, msg='success'):
    res = {
        'code': 0,
        'message': msg
    }
    if data is not None and len(data) > 0:
        res['data'] = data
    return res


# error
def error(msg='error', code=1):
    res = {
        'code': code,
        'message': msg,
    }
    return res
