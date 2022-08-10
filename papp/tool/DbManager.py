import sqlite3
import pymysql.cursors
from dbutils.pooled_db import PooledDB
from .Common import *


class DbManager(object):
    _table = ''
    _alias = ''
    _left = []
    _right = []
    _inner = []
    _cross = []
    _where = ''
    _field = []
    _group = ''
    _having = ''
    _order = ''
    _offset = 0
    _pagesize = 0
    _cache = 0
    _whereParam = []
    _setParam = []
    _replace = False
    _fetchSql = False

    _sybmol = '%s'

    # 构造函数
    def __init__(self, **kwargs):
        self.version = '2.1.20220810'
        self.sqlite = kwargs.get('sqlite', '')
        if len(self.sqlite) > 0:
            self.prefix = ''
            self._sybmol = '?'
            path = root_path() + '/db/'
            makedir(path)
            self.conn = sqlite3.connect(path + self.sqlite)  # 建立一个基于硬盘的数据库实例
            self.conn.row_factory = self._dict_factory
            self.cur = self.conn.cursor()
            return
        self.conn = None
        self.cur = None
        self.prefix = kwargs.get('prefix', '')
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=20,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=5,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=0,  # 链接池中最多闲置的链接，0和None不限制
            maxusage=1,  # 一个链接最多被重复使用的次数，None表示无限制
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            setsession=[],
            host=kwargs.get('host', 'localhost'),
            port=kwargs.get('port', 3306),
            user=kwargs.get('user', 'root'),
            password=kwargs.get('password', ''),
            database=kwargs.get('database', ''),
            charset=kwargs.get('charset', 'utf8'),
        )

    @staticmethod
    def _dict_factory(cursor, row):
        data = DbDict()
        for index, item in enumerate(cursor.description):
            data[item[0]] = row[index]
        return data

    @staticmethod
    def instance(item):
        if type(item) != dict:
            raise Exception('Connection param is invalid')
        sqlite = item.get('sqlite')
        if sqlite is not None:
            return DbManager(sqlite=sqlite)
        return DbManager(
            host=item.get('host', 'localhost'),
            post=item.get('port', 3306),
            user=item.get('user', 'root'),
            password=item.get('password', ''),
            database=item.get('database', ''),
            prefix=item.get('prefix', ''),
            charset=item.get('charset', 'utf8')
        )

    def __getattr__(self, name):
        curMethods = uncamelize(name).split('_', 1)

        def fn(*args):
            method = getattr(self, curMethods[0])
            part = curMethods[1]

            if curMethods[0] == 'where':
                if preg_match(r'^(not_)?in$', part):
                    return method(args[0], part.replace('_', ' '), args[1])
                elif preg_match(r'^(not_)?like$', part):
                    return method(args[0], part.replace('_', ' '), args[1])
                elif preg_match(r'^(not_)?null$', part):
                    return method(args[0], part.replace('_', ' '))
                else:
                    return method(part, args[0])
            else:
                return method(part, args[0])

        return fn

    # 连接数据库
    def connect(self):
        if len(self.sqlite) > 0:
            return True
        try:
            self.conn = self.pool.connection()
            self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            return True
        except Exception as e:
            print('Connect database failed:')
            print(str(e))
            return False

    # 关闭数据库
    def close(self):
        if self.conn and self.cur:
            self.cur.close()
            self.conn.close()

    # 恢复初始化
    def restore(self):
        self._table = ''
        self._alias = ''
        self._left = []
        self._right = []
        self._inner = []
        self._cross = []
        self._where = ''
        self._field = []
        self._group = ''
        self._having = ''
        self._order = ''
        self._offset = 0
        self._pagesize = 0
        self._cache = 0
        self._whereParam = []
        self._setParam = []
        self._replace = False
        self._fetchSql = False

    # 执行SQL方法
    def execute(self, sql, params=None, exe_many=False):
        res = self.connect()
        if not res:
            return False
        cnt = 0
        try:
            if self.conn and self.cur:
                if exe_many:
                    cnt = self.cur.executemany(sql, params)
                else:
                    cnt = self.cur.execute(sql, params)
                self.conn.commit()
        except Exception as e:
            print('Execute failed:')
            print(sql)
            print(str(e))
            return False
        if len(self.sqlite) == 0:
            self.close()
        return cnt

    # 表名(自动加前缀)
    def name(self, name):
        return self.table(self.prefix + name.replace(self.prefix, ''))

    # 表名
    def table(self, table):
        restore = True
        if type(table) == dict:
            tables = table
            key = tables.keys()[0]
            table = key
            self.alias(tables.get(key))
        if re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if " " in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = tables[0]
                if table.startswith('!'):  # 表名前加!代表不restore
                    restore = False
                    table = '`{}`'.format(table[1:])
                else:
                    table = '`{}`'.format(tables[0])
                self.alias(tables[1])
        else:
            table = '({})'.format(table)
        if restore:
            self.restore()
        self._table = table
        return self

    # 表别名
    def alias(self, alias):
        self._alias = ' `' + alias + '`' if len(alias) > 0 else ''
        return self

    # 左联接
    def leftJoin(self, table, on=''):
        alias = ''
        if type(table) == dict:
            tables = table
            key = tables.keys()[0]
            table = key
            alias = ' `' + tables.get(key) + '`'
        if re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if ' ' in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = '`{}{}`'.format(self.prefix, tables[0].replace(self.prefix, ''))
                alias = ' `' + tables[1] + '`'
        else:
            table = '({})'.format(table)
        sql = ' LEFT JOIN %s%s' % (table, alias)
        if len(on) > 0:
            sql += ' ON ' + preg_replace(r'(\w+)', r'`\1`', on)
        self._left.append(sql)
        return self

    # 右联接
    def rightJoin(self, table, on=''):
        alias = ''
        if type(table) == dict:
            tables = table
            key = tables.keys()[0]
            table = key
            alias = ' `' + tables.get(key) + '`'
        if re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if ' ' in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = '`{}{}`'.format(self.prefix, tables[0].replace(self.prefix, ''))
                alias = ' `' + tables[1] + '`'
        else:
            table = '({})'.format(table)
        sql = ' RIGHT JOIN %s%s' % (table, alias)
        if len(on) > 0:
            sql += ' ON ' + preg_replace(r'(\w+)', r'`\1`', on)
        self._right.append(sql)
        return self

    # 等值联接
    def innerJoin(self, table, on=''):
        alias = ''
        if type(table) == dict:
            tables = table
            key = tables.keys()[0]
            table = key
            alias = ' `' + tables.get(key) + '`'
        if re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if ' ' in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = '`{}{}`'.format(self.prefix, tables[0].replace(self.prefix, ''))
                alias = ' `' + tables[1] + '`'
        else:
            table = '({})'.format(table)
        sql = ' INNER JOIN %s%s' % (table, alias)
        if len(on) > 0:
            sql += ' ON ' + preg_replace(r'(\w+)', r'`\1`', on)
        self._inner.append(sql)
        return self

    # 多联接
    def crossJoin(self, table):
        alias = ''
        if type(table) == dict:
            tables = table
            key = tables.keys()[0]
            table = key
            alias = ' `' + tables.get(key) + '`'
        if re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if ' ' in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = '`{}{}`'.format(self.prefix, tables[0].replace(self.prefix, ''))
                alias = ' `' + tables[1] + '`'
        else:
            table = '({})'.format(table)
        self._cross.append(', %s%s' % (table, alias))
        return self

    # 条件
    def where(self, where, param1='', param2=''):
        return self.whereAdapter(where, ' AND ', param1, param2)

    def whereOr(self, where, param1='', param2=''):
        return self.whereAdapter(where, ' OR ', param1, param2)

    def whereAdapter(self, where, andOr=' AND ', param1='', param2=''):
        _where = ''
        if callable(where):
            _where += '{}('.format(andOr)
            _where += where(self)
            _where += ')'
        elif re.compile(r'^\d+$').match(str(where)) is not None:
            _where = '{}`id`={}'.format(andOr, self._sybmol)
            self._whereParam.append(where)
        elif type(where) == list:
            if len(where) > 0:
                _where += '{}('.format(andOr)
                _where_ = ''
                for item in where:
                    value = item[2]
                    isRaw = False
                    if isinstance(value, DbRaw):
                        isRaw = True
                        value = value.data
                    _where_ += ' AND %s' % preg_replace(r'(\w+)', r'`\1`', item[0])
                    where_ = str(item[1]).lower().strip()
                    if where_ in ['=', '>', '>=', '<', '<=', '<>', '!=']:
                        _where_ += where_ if where_ != '!=' else '<>'
                        if isRaw:
                            _where_ += value
                        else:
                            _where_ += self._sybmol
                            self._whereParam.append(str(value))
                    elif where_ in ['in', 'not in']:
                        _where_ += ' {} ('.format(where_.upper())
                        if type(value) == list:
                            for _item in value:
                                _where_ += self._sybmol + ', '
                                self._whereParam.append(_item)
                            _where_ = _where_.rstrip(', ')
                        else:
                            _where_ += value
                        _where_ += ')'
                    elif where_ in ['like', 'not like']:
                        _where_ += ' {} {}'.format(where_.upper(), self._sybmol)
                        self._whereParam.append(str(value).replace('%', '%%'))
                _where += _where_.lstrip(' AND ') + ')'
        elif type(where) == dict:
            _where += '{}('.format(andOr)
            _where_ = ''
            for k, v in where.items():
                value = v
                isRaw = False
                if isinstance(value, DbRaw):
                    isRaw = True
                    value = value.data
                _where_ += ' AND %s=' % preg_replace(r'(\w+)', r'`\1`', k)
                if isRaw:
                    _where_ += value
                else:
                    _where_ += self._sybmol
                self._whereParam.append(str(value))
            _where += _where_.lstrip(' AND ') + ')'
        elif type(where) == str and len(where) > 0:
            _where += '%s%s' % (andOr, preg_replace(r'(\w+)', r'`\1`', where))
            if len(str(param2).strip()) > 0:
                value = param2
                isRaw = False
                if isinstance(value, DbRaw):
                    isRaw = True
                    value = value.data
                where_ = str(param1).lower().strip()
                if where_ in ['=', '>', '>=', '<', '<=', '<>', '!=']:
                    _where += where_ if where_ != '!=' else '<>'
                    if isRaw:
                        _where += value
                    else:
                        _where += self._sybmol
                        self._whereParam.append(str(value))
                elif where_ in ['in', 'not in']:
                    _where += ' {} ('.format(where_.upper())
                    if type(value) == list:
                        for _item in value:
                            _where += self._sybmol + ', '
                            self._whereParam.append(_item)
                        _where = _where.rstrip(', ')
                    else:
                        _where += value
                    _where += ')'
                elif where_ in ['like', 'not like']:
                    _where += ' {} {}'.format(where_.upper(), self._sybmol)
                    self._whereParam.append(str(value).replace('%', '%%'))
            elif len(str(param1)) > 0:
                value = param1
                isRaw = False
                if isinstance(value, DbRaw):
                    isRaw = True
                    value = value.data
                if type(value) == list:
                    _where += ' IN ('
                    for _item in value:
                        _where += self._sybmol + ', '
                        self._whereParam.append(_item)
                    _where = _where.rstrip(', ')
                    _where += ')'
                else:
                    where_ = str(value).lower().strip()
                    if where_ in ['null', 'not null']:
                        _where += ' IS {}'.format(where_.upper())
                    else:
                        _where += '='
                        if isRaw:
                            _where += value
                        else:
                            _where += self._sybmol
                            self._whereParam.append(str(value))
        if len(_where) > 0:
            self._where += ' WHERE ' + _where.lstrip(andOr) if len(self._where) == 0 else _where
        return self

    # 时间对比查询
    # whereDay('add_time', 'today') //查询add_time今天的记录
    def whereDay(self, field, value='today'):
        return self.whereTime(field, '=', date('%Y-%m-%d %H:%M:%S', strtotime(value)))

    # whereTime('add_time', '2022-7-10') //查询add_time等于指定日期的记录
    # whereTime('add_time', '<=', '2022-7-10') //查询add_time小于或等于指定日期的记录
    # whereTime('add_time', ['2022-7-10', '2022-9-10']) //查询add_time在两个日期内的记录
    def whereTime(self, field, operator, value=''):
        if len(str(value)) == 0:
            value = operator
            operator = '='
        if type(value) == list and len(value) == 0:
            print('value is list and len is 0')
            exit(0)
        if '<' in operator:
            if type(value) == list:
                value = value[0]
            timeStamp = strtotime(date('%Y-%m-%d 00:00:00', strtotime(value)))
            where = '`{}`{}{}'.format(field, operator, self._sybmol)
            self._whereParam.append(str(timeStamp))
        elif '>' in operator:
            if type(value) == list:
                value = value[0]
            timeStamp = strtotime(date('%Y-%m-%d 23:59:59', strtotime(value)))
            where = '`{}`{}{}'.format(field, operator, self._sybmol)
            self._whereParam.append(str(timeStamp))
        else:
            if type(value) == list and len(value) == 1:
                value = value[0]
            if type(value) == list:
                start = strtotime(date('%Y-%m-%d 00:00:00', strtotime(value[0])))
                end = strtotime(date('%Y-%m-%d 23:59:59', strtotime(value[1])))
            else:
                start = strtotime(date('%Y-%m-%d 00:00:00', strtotime(value)))
                end = strtotime(date('%Y-%m-%d 23:59:59', strtotime(value)))
            where = '`{0}`>={1} AND `{0}`<={1}'.format(field, self._sybmol)
            self._whereParam.extend([str(start), str(end)])
        self._where += ' WHERE ' + where if len(self._where) == 0 else where
        return self

    # 字段
    def field(self, field):
        if type(field) == list:
            fields = field if len(field) > 0 else ['*']
            for item in fields:
                self._field.append(preg_replace(r'\b([a-z_]+)\b', DbManager.fieldMatcher, item))
        elif type(field) == dict:
            if type(self._field) != list:
                self._field = []
            for k, v in field.items():
                self._field.append('`%s` AS `%s`' % (k, v))
        elif type(field) == str:
            fields = field.split(',') if len(field) > 0 else ['*']
            for item in fields:
                self._field.append(preg_replace(r'\b([a-z_]+)\b', DbManager.fieldMatcher, item.strip()))
        return self

    @staticmethod
    def fieldMatcher(matcher):
        if matcher.group(1).upper() in 'AS,IF,IFNULL,ABS,CEIL,FLOOR,RAND,PI,POW,EXP,MOD,CONCAT,UPPER,LOWER,LEFT,RIGHT,LRTIM,RTRIM,TRIM,REPEAT,REPLACE,REVERSE,CURDATE,CURTIME,NOW,FROM_UNIXTIME,UNIX_TIMESTAMP,DATE_FORMAT,MONTH,WEEK,HOUR,MINUTE,SECOND'.split(','):
            return matcher.group(1)
        else:
            return '`%s`' % matcher.group(1)

    # 去重分组
    def distinct(self, field):
        self._field = ['DISTINCT `%s`' % field]
        return self

    # 分组(聚合)
    def group(self, group):
        self._group = ' GROUP BY ' + preg_replace(r'(\w+)', r'`\1`', group) if len(group) > 0 else ''
        return self

    # 聚合筛选, 语法与where一样
    def having(self, having):
        self._having = ' HAVING ' + having if len(having) > 0 else ''
        return self

    # 排序
    def order(self, field, order=''):
        if type(field) == list:
            self._order = ' ORDER BY'
            for item in field:
                self._order += ' %s ASC,' % preg_replace(r'(\w+)', r'`\1`', item)
            self._order = self._order.rstrip(', ')
        elif type(field) == dict:
            self._order = ' ORDER BY'
            for k, v in field.items():
                self._order += ' %s %s,' % (preg_replace(r'(\w+)', r'`\1`', k), v.upper())
            self._order = self._order.rstrip(', ')
        else:
            self._order = ' ORDER BY ' + (preg_replace(r'(\w+)', r'`\1`', field) if len(field) > 0 else '') + (
                " " + order.upper() if len(order) > 0 else '')
        return self

    # 按字段排序, 如: ORDER BY FIELD(`id`, 1, 9, 8, 4)
    def orderField(self, field, value):
        self._order = ' ORDER BY FIELD(`' + field + '`, ' + value + ')' if len(field) > 0 else ''
        return self

    # 记录偏移量, 返回记录数
    def limit(self, offset, pagesize=-100):
        if pagesize == -100:
            pagesize = int(offset)
            offset = 0
        if int(offset) < 0:
            offset = 0
        self._offset = int(offset)
        self._pagesize = int(pagesize)
        return self

    # 第n页记录, 返回记录数
    def page(self, page, pagesize):
        self._offset = (int(page) - 1) * int(pagesize)
        self._pagesize = int(pagesize)
        return self

    # 缓存, 单位秒
    def cache(self, cache):
        self._cache = int(cache)
        return self

    # 插入数据使用ON DUPLICATE KEY UPDATE方式(存在索引字段即替换,否则插入)
    def replace(self, replace=True):
        self._replace = replace
        return self

    # 打印sql
    def fetchSql(self, fetchSql=True):
        self._fetchSql = fetchSql
        return self

    # 递增(update用)
    def inc(self, field, step=1):
        self._setParam = {field: DbRaw('%s + %d' % (preg_replace(r'(\w+)', r'`\1`', field), step) if type(step) == int else '%s + %f' % (preg_replace(r'(\w+)', r'`\1`', field), step))}
        return self

    # 递减(update用)
    def dec(self, field, step=1):
        self._setParam = {field: DbRaw('%s - %d' % (preg_replace(r'(\w+)', r'`\1`', field), step) if type(step) == int else '%s - %f' % (preg_replace(r'(\w+)', r'`\1`', field), step))}
        return self

    # 记录是否存在
    def exist(self):
        return self.count() > 0

    # 记录数
    def count(self):
        if len(self._field) == 0 or 'as db_tmp' not in self._field[0] or (len(self._field) == 1 and self._field[0] == '*'):
            self._field = ['COUNT(*) as db_tmp']
        else:
            if 'DISTINCT ' in ''.join(self._field):
                self._field = ['COUNT(%s) as db_tmp' % ''.join(self._field)]
        data = self.find()
        return data.get('db_tmp', 0)

    # 最大值
    def max(self, field):
        self._field = ['MAX(%s) as db_tmp' % field]
        return self.count()

    # 最小值
    def min(self, field):
        self._field = ['MIN(%s) as db_tmp' % field]
        return self.count()

    # 平均值
    def avg(self, field):
        self._field = ['AVG(%s) as db_tmp' % field]
        return self.count()

    # 集合值
    def sum(self, field):
        self._field = ['SUM(%s) as db_tmp' % field]
        return self.count()

    # 分组连接
    def groupConcat(self, field):
        self._field = ['GROUP_CONCAT(%s) as db_tmp' % preg_replace(r'(\w+)', r'`\1`', field)]
        return self.count()

    # 数据字段值
    def value(self, field):
        self.field(field)
        data = self.find()
        if data is None:
            return None
        return data.get(field)

    # 列
    def column(self, field):
        column = []
        self._field = []
        self.field(field)
        list_ = self.select()
        for item in list_:
            column.append(item.get(field))
        return column

    # 单个数据
    def find(self, field=None):
        if field is not None:
            self.field(field)
        self.limit(1)
        sql = self.buildSql('SELECT')
        if self._cache > 0:
            res = self._cacheSql(sql)
            if res is not None:
                return res
        self._whereParam = tuple(self._whereParam)
        if self._fetchSql:
            print('{}\n{}\n'.format(sql, self._whereParam))
        self.execute(sql, self._whereParam)
        res = self.cur.fetchone()
        if self._cache > 0:
            self._cacheSql(sql, res)
        return DbDict(res)

    # 数据集
    def select(self, field=None):
        if field is not None:
            self.field(field)
        sql = self.buildSql('SELECT')
        if self._cache > 0:
            res = self._cacheSql(sql)
            if res is not None:
                return res
        self._whereParam = tuple(self._whereParam)
        if self._fetchSql:
            print('{}\n{}\n'.format(sql, self._whereParam))
        self.execute(sql, self._whereParam)
        ret = self.cur.fetchall()
        if self._cache > 0:
            self._cacheSql(sql, ret)
        res = []
        for item in ret:
            res.append(DbDict(item))
        return res

    # 新增并返回新增ID, data: 字典类型{} 数组类型[{}]
    def insert(self, data):
        if type(data) == list and len(data) == 0:
            return 0
        if type(data) != list:
            data = [data]
        self._setParam = []
        fields = []
        for k, v in data[0].items():
            fields.append(k)
        self._field = []
        self.field(fields)
        for item in data:
            param = []
            for k, v in item.items():
                param.append(str(v))
            self._setParam.append(param)
        sql = self.buildSql('INSERT')
        if self._fetchSql:
            print('{}\n{}\n'.format(sql, self._setParam))
        try:
            self.execute(sql, self._setParam)
            return self.cur.lastrowid
        except Exception as e:
            print(str(e))
            self.conn.rollback()
            exit(0)

    # 修改数据并返回影响的行数, data: 字典类型{}
    def update(self, data=None):
        if data is not None and type(data) != dict:
            return 0
        if data is None and type(self._setParam) == dict:
            pass
        else:
            self._setParam = data
        sql = self.buildSql('UPDATE')
        if self._fetchSql:
            print('{}\n{}\n'.format(sql, self._setParam))
        try:
            self.execute(sql, self._setParam)
            return self.cur.rowcount
        except Exception as e:
            print(str(e))
            self.conn.rollback()
            exit(0)

    # 删除并返回影响行数
    def delete(self, where=None):
        if where is not None:
            self.where(where)
        sql = self.buildSql('DELETE')
        if self._fetchSql:
            print('{}\n{}\n'.format(sql, self._setParam))
        try:
            self.execute(sql, self._setParam)
            return self.cur.rowcount
        except Exception as e:
            print(str(e))
            self.conn.rollback()
            exit(0)

    # 执行原生SQL语句
    def query(self, sql, params=None):
        if sql.upper().startswith('SELECT '):
            self.execute(sql, params)
            ret = self.cur.fetchall()
            res = []
            for item in ret:
                res.append(DbDict(item))
            return res
        else:
            try:
                self.execute(sql, params)
                if sql.upper().startswith('INSERT '):
                    return self.cur.lastrowid
                else:
                    return self.cur.rowcount
            except Exception as e:
                print(str(e))
                self.conn.rollback()
                exit(0)

    # 获取/设置sql缓存
    def _cacheSql(self, sql, res=None):
        if self._cache == 0:
            return None
        obj = hashlib.md5()
        obj.update(sql.encode('utf-8'))
        filename = obj.hexdigest()
        cacheDir = Path(runtime_path() + '/sql')
        if res is None:
            if cacheDir.is_dir():
                cacheFile = Path('%s/%s' % (cacheDir, filename))
                if cacheFile.is_file():
                    if int(time.time()) - int(os.path.getmtime(cacheFile)) < self._cache:
                        fo = open('%s' % cacheFile, 'r')
                        data = fo.read()
                        fo.close()
                        ret = json_decode(data)
                        if type(ret) == dict:
                            return DbDict(ret)
                        else:
                            res = []
                            for item in ret:
                                res.append(DbDict(item))
                            return res
            return None
        if not cacheDir.is_dir():
            os.makedirs('%s' % cacheDir)
        cacheFile = Path('%s/%s' % (cacheDir, filename))
        fo = open('%s' % cacheFile, 'w+')
        fo.write(json_encode(res))
        fo.close()
        return None

    # 构建SQL语句
    def buildSql(self, sqlType='SELECT'):
        sqlType = sqlType.upper()
        if sqlType == 'SELECT':
            if len(self._field) == 0:
                self._field = ['*']
            sql = 'SELECT %s FROM %s%s' % (', '.join(self._field), self._table, self._alias)
            if len(self._left) > 0:
                sql += ''.join(self._left)
            if len(self._right) > 0:
                sql += ''.join(self._right)
            if len(self._inner) > 0:
                sql += ''.join(self._inner)
            if len(self._cross) > 0:
                sql += ''.join(self._cross)
            limit = ' LIMIT %d,%d' % (self._offset, self._pagesize) if self._pagesize > 0 else ''
            sql += '%s%s%s%s%s' % (self._where, self._group, self._having, self._order, limit)
            return sql
        elif sqlType == 'INSERT':
            sql = 'INSERT INTO %s (%s) VALUES ' % (self._table, ', '.join(self._field))
            values = []
            flag = ''
            for items in self._setParam:
                flag += '('
                for item in items:
                    flag += self._sybmol + ', '
                    values.append(item)
                flag = flag.rstrip(', ') + '), '
            flag = flag.rstrip(', ')
            sql += flag
            if self._replace:
                updateValues = []
                for item in self._field:
                    updateValues.append('%s=VALUES(%s)' % (item, item))
                sql += ' ON DUPLICATE KEY UPDATE %s' % ', '.join(updateValues)
            self._setParam = tuple(values)
            return sql
        elif sqlType == 'UPDATE':
            values = []
            sql = 'UPDATE %s SET ' % self._table
            for k, v in dict(self._setParam).items():
                value = v
                isRaw = False
                if isinstance(value, DbRaw):
                    isRaw = True
                    value = value.data
                sql += '{}='.format(preg_replace(r'(\w+)', r'`\1`', k))
                if isRaw:
                    sql += value
                else:
                    sql += self._sybmol
                    values.append(value)
                sql += ', '
            sql = sql.rstrip(', ')
            sql += '%s' % self._where
            if len(self._whereParam) > 0:
                for item in self._whereParam:
                    values.append(item)
            self._setParam = tuple(values)
            return sql
        elif sqlType == 'DELETE':
            values = []
            sql = 'DELETE' + ' FROM %s%s' % (self._table, self._where)
            if len(self._whereParam) > 0:
                for item in self._whereParam:
                    values.append(item)
            self._setParam = tuple(values)
            return sql


class DbRaw(object):
    data = ''

    def __init__(self, data):
        self.data = data


class DbDict(dict):
    def __getattr__(self, item):
        res = self.get(item)
        if isinstance(res, decimal.Decimal):
            res = float(res)
        return res

    def __setattr__(self, key, value):
        self[key] = value


Db = DbManager(
    host=connections['default'].get('host', 'localhost'),
    post=connections['default'].get("port", 3306),
    user=connections['default'].get('user', 'root'),
    password=connections['default'].get('password', ''),
    database=connections['default'].get('database', ''),
    prefix=connections['default'].get('prefix', ''),
    charset=connections['default'].get('charset', 'utf8')
)
