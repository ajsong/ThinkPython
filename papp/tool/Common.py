# Developed by @mario 2.6.20230111
import base64
import decimal
import hashlib
import json
import math
import shutil
import sys
import os
import random
import re
import time
import datetime
import calendar
from urllib import parse
from decimal import *
from pathlib import Path
import requests
from ..Config import *


# 修复json.dumps的时候is not JSON serializable报错的问题
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if obj.__class__.__name__ == 'DbList':
            return getattr(obj, 'data')
        super(JSONEncoder, self).default(obj)


# 获取根目录
def root_path():
    return str(Path(__file__).resolve().parents[2])


# 获取运行时目录
def runtime_path():
    return root_path() + '/runtime'


# 生成序列号
def generate_sn():
    return date('%y%m%d%H%M%S') + str(random.randint(10000, 99999))


# 随机范围内整数
def random_num(minNum=0, maxNum=sys.maxsize):
    return random.randint(minNum, maxNum)


# 随机范围内小数
def random_float(minNum=0, maxNum=1):
    return random.uniform(minNum, maxNum)


# 正则匹配
def preg_match(pattern, string, flags=0):
    return re.compile(pattern, flags).match(str(string)) is not None


# 正则替换
def preg_replace(pattern, repl, string, flags=0):
    return re.compile(pattern, flags).sub(repl, str(string))


# 正则分割
def preg_split(pattern, string, flags=0):
    return re.compile(pattern, flags).split(str(string))


# 获取文件内容
def file_get_contents(file):
    if os.path.isfile(file) is False:
        print('The file does not exist\n' + file)
        return None
    if os.access(file, os.R_OK) is False:
        print('The file can not read\n' + file)
        return None
    fo = open(file, 'r')
    content = fo.read()
    fo.close()
    return content


# 写入文件内容, mode=a+ 追加
def file_put_contents(file, content='', mode='w'):
    if type(content) != str and type(content) != int and type(content) != float and type(content) != complex and type(content) != bool:
        content = json_encode(content)
    fo = open(file, mode)
    fo.write(content)
    fo.close()


# pip install pandas
# pip install xlrd
# pip install xlwt
# pip install openpyxl
# 导入Excel
# columns = ['id', 'name', 'age']
def import_excel(file, columns=None, has_header=True, sheet_name='Sheet1'):
    import pandas
    res = []
    data = pandas.read_excel(file, sheet_name=sheet_name) if has_header else pandas.read_excel(file, sheet_name=sheet_name, header=None)
    # data.shape[0]  # 行数
    # data.shape[1]  # 列数
    if data.shape[1] == 0:
        print('Excel is empty')
        return []
    if columns is None:
        columns = []
        for i in range(data.shape[1]):
            columns.append('column' + str(i + 1))
    for row in data.itertuples():
        d = {}
        for index, key in enumerate(columns):
            value = row[index + 1]
            if type(value) == int or type(value) == float:
                d[key] = value if math.isnan(value) is False else ''
            else:
                d[key] = value
        res.append(d)
    return res


# 导出Excel
# columns = {'id': 'ID', 'name': '姓名', 'age': '年龄'}
def export_excel(file, data, columns=None):
    import pandas
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
    book = Workbook()
    sheet = book.active
    df = pandas.DataFrame(data)  # 将字典列表转换为DataFrame
    if type(columns) == dict:
        df = df[dict(columns).keys()]
        df.rename(columns=columns, inplace=True)
    df.fillna('', inplace=True)  # 替换空单元格
    for row in dataframe_to_rows(df, index=False, header=True):
        sheet.append(row)
    book.save(file)


# 当前时间戳
def timestamp():
    return int(time.time())


# 时间戳转日期字符串
def date(formatStr='%Y-%m-%d %H:%M:%S', timeStamp=None):
    if timeStamp is None:
        timeStamp = time.localtime()
    else:
        timeStamp = time.localtime(int(timeStamp))
    if '%t' in formatStr:
        weekDay, monthCountDay = calendar.monthrange(timeStamp.tm_year, timeStamp.tm_mon)
        formatStr = formatStr.replace('%t', str(monthCountDay))
    return time.strftime(formatStr, timeStamp)


# 字符串日期转时间戳
# https://www.runoob.com/python3/python3-date-time.html
def strtotime(dateStr, timeStamp=None):
    if type(dateStr) == int:
        return dateStr
    if timeStamp is None:
        timeStamp = timestamp()
    timeStamp = int(timeStamp)
    mark = dateStr.upper()
    if mark == 'TODAY':
        return timestamp()
    elif mark == 'BEFORE':
        return timeStamp - 60 * 60 * 24 * 2
    elif (mark == 'YESTERDAY') | (mark == 'LAST DAY'):
        return timeStamp - 60 * 60 * 24
    elif mark == 'TOMORROW':
        return timeStamp + 60 * 60 * 24
    elif (mark == 'ACQUIRED') | (mark == 'AFTER'):
        return timeStamp + 60 * 60 * 24 * 2
    elif mark == 'LAST WEEK':
        mark = '-1 WEEK'
    elif mark == 'LAST MONTH':
        mark = '-1 MONTH'
    elif mark == 'LAST YEAR':
        mark = '-1 YEAR'
    if preg_match(r'^\s*([+-]?\d+)\s*\w+\s*$', mark) is False:
        if is_date(dateStr):
            if preg_match(r'^\d{4}-\d{1,2}-\d{1,2}$', dateStr):
                timeArray = time.strptime(dateStr, '%Y-%m-%d')
            else:
                timeArray = time.strptime(dateStr, '%Y-%m-%d %H:%M:%S')  # 时间字符串解析为时间元组
            return int(time.mktime(timeArray))  # 将时间元组转换为时间戳
        return timeStamp
    matcher = re.compile(r'^\s*([+-]?\d+)\s*(\w+)\s*$', re.I).match(mark)
    if matcher is not None:
        interval = int(matcher.group(1).replace('+', ''))
        m = matcher.group(2).upper()
        if (m == 'SECOND') | (m == 'SECONDS'):
            return timeStamp + interval
        elif (m == 'MINUTE') | (m == 'MINUTES'):
            return timeStamp + interval * 60
        elif (m == 'HOUR') | (m == 'HOURS'):
            return timeStamp + interval * 60 * 60
        elif (m == 'DAY') | (m == 'DAYS'):
            return timeStamp + interval * 60 * 60 * 24
        elif (m == 'WEEK') | (m == 'WEEKS'):
            return timeStamp + interval * 60 * 60 * 24 * 7
        elif (m == 'MONTH') | (m == 'MONTHS'):
            timeDate = datetime.date(int(date('%Y', timeStamp)), int(date('%m', timeStamp)), int(date('%d', timeStamp)))
            year = timeDate.year
            month = timeDate.month
            for _ in range(abs(interval)):
                if interval < 0:
                    if month == 1:
                        year -= 1
                        month = 12
                    else:
                        month -= 1
                else:
                    if month == 12:
                        year += 1
                        month = 1
                    else:
                        month += 1
            timeArray = time.strptime(date(str(year)+'-'+str(month)+'-%d %H:%M:%S', timeStamp), '%Y-%m-%d %H:%M:%S')
            return int(time.mktime(timeArray))
        elif (m == 'YEAR') | (m == 'YEARS'):
            timeDate = datetime.date(int(date('%Y', timeStamp)), int(date('%m', timeStamp)), int(date('%d', timeStamp)))
            timeArray = time.strptime(date(str(int(timeDate.strftime('%Y')) + interval)+'-%m-%d %H:%M:%S', timeStamp), '%Y-%m-%d %H:%M:%S')
            return int(time.mktime(timeArray))


# md5
def md5(string):
    obj = hashlib.md5()
    obj.update(string.encode('utf-8'))
    return obj.hexdigest()


# sha1
def sha1(string):
    sha = hashlib.sha1(string.encode('utf-8'))
    return sha.hexdigest()


# json_encode
def json_encode(obj):
    if type(obj) == str:
        return obj
    return json.dumps(obj, ensure_ascii=False, cls=JSONEncoder)


# json_decode
def json_decode(jsonStr):
    if jsonStr.startswith('[') is False and jsonStr.startswith('{') is False:
        return jsonStr
    try:
        return json.loads(jsonStr)
    except json.decoder.JSONDecodeError:
        return None


# json美化打印
def format_json(obj):
    if type(obj) == str:
        obj = json_decode(obj)
    print(json.dumps(obj, indent=4, ensure_ascii=False, sort_keys=True, cls=JSONEncoder))


# base64_encode
def base64_encode(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


# base64_decode
def base64_decode(string):
    return base64.b64decode(string).decode('utf-8')


# url_encode
def url_encode(string):
    return parse.quote(string, safe='', encoding=None, errors=None)


# url_decode
def url_decode(string):
    return parse.unquote(string, encoding='utf-8', errors='replace')


# 文件是否存在
def file_exists(file):
    return os.path.isfile(file)


# 创建多级目录,对应根目录
def makedir(path):
    path = root_path() + '{}'.format(path).replace(root_path(), '')
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
    # https://zhidao.baidu.com/question/1822455991691849548.html
    # 中国联通号码：130、131、132、145（无线上网卡）、155、156、185（iPhone5上市后开放）、186、176（4G号段）、175（2015年9月10日正式启用，暂只对北京、上海和广东投放办理）,166,146
    # 中国移动号码：134、135、136、137、138、139、147（无线上网卡）、148、150、151、152、157、158、159、178、182、183、184、187、188、198
    # 中国电信号码：133、153、180、181、189、177、173、149、199
    # 中国广电号段：192
    return re.compile(r'^1[34578]\d{9}$|^19[289]\d{8}$|^166\d{8}$').match(str(mobile)) is not None


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
    return re.compile(r'^\d{4}-\d{1,2}-\d{1,2}( \d{1,2}:\d{1,2}:\d{1,2})?$').match(str(dateStr)) is not None


# 获取ip
def ip():
    return requests.get('https://api.ipify.org', timeout=5).text
    # res = requests.get('https://myip.ipip.net', timeout=5).text
    # res = re.findall(r'(\d+\.\d+\.\d+\.\d+)', res)
    # return res[0] if res else ''


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
    return re.sub(r'({}\w)'.format(delimiter), lambda x: x.group(1)[1].upper(), ('' if small else delimiter) + value)


# 驼峰转下划线
def uncamelize(value, delimiter='_'):
    return re.sub(re.compile(r'([a-z]|\d)([A-Z])'), r'\1{}\2'.format(delimiter), value).lower()


# 科学计数法还原数值字符串
def enumToStr(num, scale=8):
    if 'e' not in str(num).lower():
        return num
    formats = '%.{}f'.format(scale)
    return formats % num


# 把列表分割成小列表
def array_chunk(array, length):
    group = zip(*(iter(array),) *length)
    arr = [list(i) for i in group]
    count = len(array) % length
    arr.append(array[-count:]) if count != 0 else arr
    return arr


# 写文件
def write_file(content, filename, path=''):
    if len(path) == 0:
        path = runtime_path()
    if not Path(path).is_dir():
        os.makedirs(path)
    file = Path('{}/{}'.format(path, filename))
    if type(content) != str and type(content) != int and type(content) != float and type(content) != complex and type(content) != bool:
        content = json_encode(content)
    fo = open('{}'.format(file), 'w')
    fo.write(content)
    fo.close()


# 写log文件
def write_log(content, filename='log.txt'):
    path = runtime_path()
    if not Path(path).is_dir():
        os.makedirs(path)
    file = Path('{}/{}'.format(path, filename))
    if type(content) != str and type(content) != int and type(content) != float and type(content) != complex and type(content) != bool:
        content = json_encode(content)
    fo = open('{}'.format(file), 'a+')
    fo.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\n' + content + '\n\n')
    fo.close()


# 写error文件
def write_error(content):
    write_log(content, 'error.txt')


# 计时器, 开始时调用 start = timing(), 结束时调用 timing(start)
def timing(start=0):
    if start == 0:
        print('Start: {}'.format(date()))
        return timestamp()
    print('End: {}'.format(date()))
    between = timestamp() - start
    print('Used {:.1f} minute'.format(float(between/60)))


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


# Redis
def Redis(host='localhost', port=6379, db=0):
    import redis
    pool = redis.ConnectionPool(host=host, port=port, db=db, decode_responses=True)
    return redis.StrictRedis(connection_pool=pool)


# 网络请求
def requestUrl(method, url, data=None, returnJson=False, postJson=False, headers=None, proxies=None):
    method = method.upper()
    if url.startswith('https:') is False and url.startswith('http:') is False:
        url = Config.api_url.rstrip('/') + '/' + url.lstrip('/')
    if headers is None:
        headers = {}
    if postJson:
        headers['Content-type'] = 'application/json;charset=UTF-8'
    if type(proxies) == str:
        proxies = {'http': proxies, 'https': proxies}  # 127.0.0.1:7890
    if method == 'FILE':
        # data = {'image': open('test.jpg', 'rb')}
        # data = {'file': ('test.jpg', open('test.jpg', 'rb'), 'image/jpeg'), 'dir': (None, 'pic')}
        res = requests.post(url=url, files=data, headers=headers, timeout=10, proxies=proxies)
    elif method == 'POST':
        res = requests.post(url=url, data=data, headers=headers, timeout=5, proxies=proxies)
    else:
        res = requests.get(url=url, params=data, headers=headers, timeout=5, proxies=proxies)
    if res.status_code == 301 or res.status_code == 302:
        return requestUrl(method, url, data, returnJson, postJson, headers, proxies)
    if res is None:
        return None
    if returnJson:
        return json_decode(res.text)
    return res.text


# success
def success(data=None, msg='success', extend=None, **kwargs):
    res = {
        'code': 0,
        'message': msg
    }
    if len(kwargs) > 0:  # 第4个参数合并到data(data为字典有效)
        if data is not None:
            data = {}
        if type(data) == dict:
            data.update(kwargs)
    if data is not None and len(data) > 0:
        res['data'] = data
    if type(extend) == dict:  # 第3个参数合并到res
        res.update(extend)
    return res


# error
def error(msg='error', code=1):
    res = {
        'code': code,
        'message': msg,
    }
    return res
