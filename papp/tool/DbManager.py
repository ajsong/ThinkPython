# Developed by @mario 3.0.20220920
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
    _union = []
    _where = ''
    _field = []
    _group = ''
    _having = ''
    _order = ''
    _offset = 0
    _pagesize = 0
    _cache = 0
    _createTime = ''
    _updateTime = ''
    _dateFormat = ''
    _whereParam = []
    _setParam = []
    _replace = False
    _printSql = False
    _fetchSql = False
    _fieldsType = None

    _sybmol = '%s'
    _datetime_field = 'create_time,update_time'

    # 构造函数
    def __init__(self, **kwargs):
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
            print('Connection param is invalid')
            exit(0)
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
            if len(curMethods) == 1:
                print('Features under development:\n{}{})'.format(name, str(args).strip(',)')))
                exit(0)
            if curMethods[0] not in dir(self):
                print('{} have no attribute: {}{})'.format(self.__class__.__name__, name, str(args).strip(',)')))
                exit(0)
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
            elif curMethods[0] == 'field':
                return method({part: args[0]})
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
            exit(0)

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
        self._union = []
        self._where = ''
        self._field = []
        self._group = ''
        self._having = ''
        self._order = ''
        self._offset = 0
        self._pagesize = 0
        self._cache = 0
        self._createTime = ''
        self._updateTime = ''
        self._dateFormat = ''
        self._whereParam = []
        self._setParam = []
        self._replace = False
        self._printSql = False
        self._fetchSql = False
        self._fieldsType = None

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
            exit(0)
        if len(self.sqlite) == 0:
            self.close()
        return cnt

    # 表名(自动加表前缀)
    def name(self, name):
        return self.table(self.prefix + name.replace(self.prefix, ''))

    # 表名
    def table(self, table):
        self.restore()
        if type(table) == dict:
            tables = table
            key = tables.keys()[0]
            table = key
            self.alias(tables.get(key))
        if re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if ' ' in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = tables[0]
                self.alias(tables[1])
            table = '`{}`'.format(table)
        else:
            table = '({})'.format(table)
        self._table = table
        return self

    # 表别名
    def alias(self, alias):
        self._alias = ' `' + alias + '`' if len(alias) > 0 else ''
        return self

    # 左联接
    def leftJoin(self, table, alias='', on=''):
        from ..model.Core import Core
        if len(alias) > 0:
            if '=' in alias:
                on = alias
                alias = ''
            else:
                alias = ' `' + alias + '`'
        if type(table) == dict:
            tables = table
            key = list(tables.keys())[0]
            if isinstance(key, Core):
                table = getattr(key, '_tableName')()
            else:
                table = key
            alias = ' `' + tables.get(key) + '`'
        isOverall = False
        if isinstance(table, Core):
            table = '`{}{}`'.format(self.prefix, getattr(table, '_tableName')().replace(self.prefix, ''))
        elif re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if ' ' in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = tables[0]
                alias = ' `' + tables[1] + '`'
            table = '`{}{}`'.format(self.prefix, table.replace(self.prefix, ''))
        else:
            isOverall = True
            table = '({})'.format(table)
        sql = ' LEFT JOIN {}{}'.format(table, alias)
        if len(on) > 0:
            sql += ' ON ' + preg_replace(r'(\w+)', r'`\1`', on)
        else:
            if isOverall is False:
                sql += ' ON ' + preg_replace(r'(\w+)', r'`\1`', '{}.id={}.{}_id'.format(self._alias.strip().strip('`'), alias.strip().strip('`'), self._table.strip('`').strip(self.prefix)))
        self._left.append(sql)
        return self

    # 右联接
    def rightJoin(self, table, alias='', on=''):
        from ..model.Core import Core
        if len(alias) > 0:
            if '=' in alias:
                on = alias
                alias = ''
            else:
                alias = ' `' + alias + '`'
        if type(table) == dict:
            tables = table
            key = list(tables.keys())[0]
            if isinstance(key, Core):
                table = getattr(key, '_tableName')()
            else:
                table = key
            alias = ' `' + tables.get(key) + '`'
        isOverall = False
        if isinstance(table, Core):
            table = '`{}{}`'.format(self.prefix, getattr(table, '_tableName')().replace(self.prefix, ''))
        elif re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if ' ' in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = tables[0]
                alias = ' `' + tables[1] + '`'
            table = '`{}{}`'.format(self.prefix, table.replace(self.prefix, ''))
        else:
            isOverall = True
            table = '({})'.format(table)
        sql = ' RIGHT JOIN {}{}'.format(table, alias)
        if len(on) > 0:
            sql += ' ON ' + preg_replace(r'(\w+)', r'`\1`', on)
        else:
            if isOverall is False:
                sql += ' ON ' + preg_replace(r'(\w+)', r'`\1`', '{}.id={}.{}_id'.format(alias.strip().strip('`'), self._alias.strip().strip('`'), table.strip('`').strip(self.prefix)))
        self._right.append(sql)
        return self

    # 等值联接
    def innerJoin(self, table, alias='', on=''):
        from ..model.Core import Core
        if len(alias) > 0:
            if '=' in alias:
                on = alias
                alias = ''
            else:
                alias = ' `' + alias + '`'
        if type(table) == dict:
            tables = table
            key = list(tables.keys())[0]
            if isinstance(key, Core):
                table = getattr(key, '_tableName')()
            else:
                table = key
            alias = ' `' + tables.get(key) + '`'
        isOverall = False
        if isinstance(table, Core):
            table = '`{}{}`'.format(self.prefix, getattr(table, '_tableName')().replace(self.prefix, ''))
        elif re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if ' ' in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = tables[0]
                alias = ' `' + tables[1] + '`'
            table = '`{}{}`'.format(self.prefix, table.replace(self.prefix, ''))
        else:
            isOverall = True
            table = '({})'.format(table)
        sql = ' INNER JOIN {}{}'.format(table, alias)
        if len(on) > 0:
            sql += ' ON ' + preg_replace(r'(\w+)', r'`\1`', on)
        else:
            if isOverall is False:
                sql += ' ON ' + preg_replace(r'(\w+)', r'`\1`', '{}.id={}.{}_id'.format(self._alias.strip().strip('`'), alias.strip().strip('`'), self._table.strip('`').strip(self.prefix)))
        self._inner.append(sql)
        return self

    # 多联接
    def crossJoin(self, table, alias=''):
        from ..model.Core import Core
        if len(alias) > 0:
            alias = ' `' + alias + '`'
        if type(table) == dict:
            tables = table
            key = list(tables.keys())[0]
            if isinstance(key, Core):
                table = getattr(key, '_tableName')()
            else:
                table = key
            alias = ' `' + tables.get(key) + '`'
        if isinstance(table, Core):
            table = '`{}{}`'.format(self.prefix, getattr(table, '_tableName')().replace(self.prefix, ''))
        elif re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if ' ' in table:
                tables = re.sub(r'\s+', ' ', table).split(' ')
                table = tables[0]
                alias = ' `' + tables[1] + '`'
            table = '`{}{}`'.format(self.prefix, table.replace(self.prefix, ''))
        else:
            table = '({})'.format(table)
        self._cross.append(', {}{}'.format(table, alias))
        return self

    # 联合查询
    def unionAll(self, table, field=None, where='', group='', having='', order='', offset=0, pagesize=0):
        from ..model.Core import Core
        if type(table) == dict:
            tables = table
            key = list(tables.keys())[0]
            if isinstance(key, Core):
                table = getattr(key, '_tableName')()
            else:
                table = key
        if isinstance(table, Core) or re.compile(r'^\w+(\s+\w+)?$').match(str(table)) is not None:
            if isinstance(table, Core):
                table = getattr(table, '_tableName')()
            else:
                if ' ' in table:
                    tables = re.sub(r'\s+', ' ', table).split(' ')
                    table = tables[0]
            table = '`{}{}`'.format(self.prefix, table.replace(self.prefix, ''))
            sql = 'SELECT {} FROM {}'.format(', '.join(self._fieldAdapter(field, True)), table)
            where = self._whereAdapter(where, ' AND ', '', '', True)
            group = ' GROUP BY ' + preg_replace(r'(\w+)', r'`\1`', group) if len(group) > 0 else ''
            having = ' HAVING ' + having if len(having) > 0 else ''
            order = self._orderAdapter(order, '', True)
            limit = ' LIMIT {},{}'.format(offset, pagesize) if pagesize > 0 else ''
            sql += '{}{}{}{}{}'.format(where, group, having, order, limit)
        else:
            sql = '({})'.format(table)
        self._union.append(' UNION ALL {}'.format(sql))
        return self

    # 条件
    def where(self, where, param1='', param2=''):
        return self._whereAdapter(where, ' AND ', param1, param2)

    def whereRaw(self, where):
        return self.where(where)

    def whereOr(self, where, param1='', param2=''):
        return self._whereAdapter(where, ' OR ', param1, param2)

    def _whereAdapter(self, where, andOr=' AND ', param1='', param2='', directReturn=False):
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
                    field = item[0]
                    value = item[2]
                    if isinstance(field, DbRaw):
                        field = field.data
                    else:
                        field = preg_replace(r'(\w+)', r'`\1`', field)
                    isRaw = False
                    if isinstance(value, DbRaw):
                        isRaw = True
                        value = value.data
                    _where_ += ' AND {}'.format(field)
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
                field = k
                value = v
                if isinstance(field, DbRaw):
                    field = field.data
                else:
                    field = preg_replace(r'(\w+)', r'`\1`', field)
                isRaw = False
                if isinstance(value, DbRaw):
                    isRaw = True
                    value = value.data
                _where_ += ' AND {}='.format(field)
                if isRaw:
                    _where_ += value
                else:
                    _where_ += self._sybmol
                self._whereParam.append(str(value))
            _where += _where_.lstrip(' AND ') + ')'
        elif isinstance(where, DbRaw) or (type(where) == str and len(where) > 0):
            field = where
            if isinstance(field, DbRaw):
                field = field.data
            elif preg_match(r'^[\w.]+$', field):
                field = preg_replace(r'(\w+)', r'`\1`', field)
            else:
                field = '({})'.format(field)
            _where += '{}{}'.format(andOr, field)
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
            elif isinstance(param1, DbRaw) or len(str(param1)) > 0:
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
        if directReturn:
            return ' WHERE ' + _where.lstrip(andOr) if len(_where) > 0 else ''
        if len(_where) > 0:
            self._where += ' WHERE ' + _where.lstrip(andOr) if len(self._where) == 0 else _where
        return self

    # 时间对比查询
    def whereYear(self, field, value=''):
        if len(value) > 0:
            year = date('%Y', strtotime(value))
        else:
            year = date('%Y')
        return self.whereTime(field, [year+'-1-1', year+'-12-31'])

    def whereMonth(self, field, value=''):
        if len(value) > 0:
            timeStamp = strtotime(value)
            Ym = date('%Y-%m', timeStamp)
            monthDay = date('%t', timeStamp)
        else:
            Ym = date('%Y-%m')
            monthDay = date('%t')
        return self.whereTime(field, [Ym+'-1', Ym+'-'+monthDay])

    def whereWeek(self, field, value=''):
        if len(value) > 0:
            timeStamp = strtotime(value)
            Ymd = date('%Y-%m-%d', timeStamp)
        else:
            Ymd = date('%Y-%m-%d')
        day = datetime.datetime.strptime(Ymd, '%Y-%m-%d')
        monday = datetime.datetime.strftime(day - datetime.timedelta(day.weekday()), '%Y-%m-%d')
        monday_ = datetime.datetime.strptime(monday, '%Y-%m-%d')
        sunday = datetime.datetime.strftime(monday_ + datetime.timedelta(monday_.weekday() + 6), '%Y-%m-%d')
        return self.whereTime(field, [monday, sunday])

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
            print('whereTime value is list and len is 0')
            exit(0)
        where = ' {} '.format('AND')
        if '<' in operator:
            if type(value) == list:
                value = value[0]
            timeStamp = strtotime(date('%Y-%m-%d 00:00:00', strtotime(value)))
            where += '`{}`{}{}'.format(field, operator, self._sybmol)
            self._whereParam.append(str(timeStamp))
        elif '>' in operator:
            if type(value) == list:
                value = value[0]
            timeStamp = strtotime(date('%Y-%m-%d 23:59:59', strtotime(value)))
            where += '`{}`{}{}'.format(field, operator, self._sybmol)
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
            where += '`{0}`>={1} AND `{0}`<={1}'.format(field, self._sybmol)
            self._whereParam.extend([str(start), str(end)])
        self._where += ' WHERE ' + where.lstrip(' AND ') if len(self._where) == 0 else where
        return self

    # 比较两个字段
    def whereColumn(self, field1, operator, field2=None, logic='AND'):
        if operator is None or len(operator) == 0:
            print('whereColumn Missing parameter')
            exit(0)
        if field2 is None:
            field2 = operator
            operator = '='
        where = ' {} {}{}{}'.format(logic, preg_replace(r'\b([a-z_]+)\b', DbManager.fieldMatcher, field1), operator, preg_replace(r'\b([a-z_]+)\b', DbManager.fieldMatcher, field2))
        self._where += ' WHERE ' + where.lstrip(' {} '.format(logic)) if len(self._where) == 0 else where
        return self

    # 字段
    def field(self, field):
        return self._fieldAdapter(field)

    # 字段(不自动加字段引号)
    def fieldRaw(self, field):
        return self._fieldAdapter(field, False, False)

    # 不包含字段
    def withoutField(self, field):
        _fields = self.getFields().keys()
        _field = self._fieldAdapter(field, True)
        fields = []
        for item in _fields:
            if '`{}`'.format(item) not in _field:
                fields.append(item)
        return self._fieldAdapter(fields)

    def _fieldAdapter(self, field, directReturn=False, autoQuotes=True):
        _field = []
        if type(field) == list and len(field) > 0:
            for item in field:
                if len(item) > 0:
                    _field.append(preg_replace(r'\b([a-z_]+)\b', DbManager.fieldMatcher, item) if autoQuotes else item)
        elif type(field) == dict:
            for k, v in field.items():
                if len(k) > 0 or len(v) > 0:
                    if len(k) > 0:
                        _field.append('{} AS `{}`'.format(preg_replace(r'\b([a-z_]+)\b', DbManager.fieldMatcher, k) if autoQuotes else k, v) if len(v) > 0 else k)
                    else:
                        _field.append("'' AS `{}`".format(v))
        elif type(field) == str:
            fields = field.split(',') if len(field) > 0 else ['*']
            for item in fields:
                _field.append(preg_replace(r'\b([a-z_]+)\b', DbManager.fieldMatcher, item.strip()) if autoQuotes else item.strip())
        if directReturn:
            return _field
        if type(self._field) != list:
            self._field = []
        self._field.extend(_field)
        _fields = []
        [_fields.append(i) for i in self._field if i not in _fields]
        self._field = _fields
        return self

    @staticmethod
    def fieldMatcher(matcher):
        if matcher.group(1).upper() in 'AS,COUNT,MAX,MIN,AVG,SUM,GROUP_CONCAT,IF,IFNULL,ABS,CEIL,FLOOR,RAND,PI,POW,EXP,MOD,CONCAT,UPPER,LOWER,LEFT,RIGHT,LRTIM,RTRIM,TRIM,REPEAT,REPLACE,REVERSE,CURDATE,CURTIME,NOW,FROM_UNIXTIME,UNIX_TIMESTAMP,DATE_FORMAT,MONTH,WEEK,HOUR,MINUTE,SECOND'.split(','):
            return matcher.group(1)
        else:
            return '`{}`'.format(matcher.group(1))

    # 去重分组
    def distinct(self, field):
        self._field = ['DISTINCT {}'.format(preg_replace(r'(\w+)', r'`\1`', field))]
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
        return self._orderAdapter(field, order)

    def _orderAdapter(self, field, order='', directReturn=False):
        _order = ''
        if type(field) == list:
            _order += ' ORDER BY'
            for item in field:
                _order += ' {} ASC,'.format(preg_replace(r'(\w+)', r'`\1`', item))
            _order = _order.rstrip(', ')
        elif type(field) == dict:
            _order += ' ORDER BY'
            for k, v in field.items():
                _order += ' {} {},'.format(preg_replace(r'(\w+)', r'`\1`', k), v.upper())
            _order = _order.rstrip(', ')
        elif type(field) == str:
            if len(field) > 0:
                _order += ' ORDER BY ' + (preg_replace(r'(\w+)', r'`\1`', field) if len(field) > 0 else '') + (' ' + order.upper() if len(order) > 0 else '')
        if directReturn:
            return _order
        self._order = _order
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
    def printSql(self, printSql=True):
        self._printSql = printSql
        return self

    # 获取sql
    def fetchSql(self, fetchSql=True):
        self._fetchSql = fetchSql
        return self

    # 自动时间, False为关闭自动写入/格式化
    def autoTime(self, autoTime):
        if type(autoTime) == bool and autoTime is False:
            self._createTime = False
            self._updateTime = False
        return self

    # 自动格式化时间的格式
    def dateFormat(self, formatStr):
        self._dateFormat = formatStr
        return self

    # 自动写入创建时间
    def createTime(self, field):
        self._createTime = field
        return self

    # 自动写入更新时间
    def updateTime(self, field):
        self._updateTime = field
        return self

    # 递增(update用)
    def inc(self, field, step=1):
        self._setParam = {field: DbRaw('{}+{}'.format(preg_replace(r'(\w+)', r'`\1`', field), step))}
        return self

    # 递减(update用)
    def dec(self, field, step=1):
        self._setParam = {field: DbRaw('{}-{}'.format(preg_replace(r'(\w+)', r'`\1`', field), step))}
        return self

    # 记录是否存在
    def exist(self):
        return self.count() > 0

    # 记录数
    def count(self):
        if len(self._field) == 0 or preg_match(r'^(MAX|MIN|AVG|SUM|GROUP_CONCAT)\(', self._field[0]) is False or (len(self._field) == 1 and self._field[0] == '*'):
            self._field = ['COUNT(*)']
        else:
            if 'DISTINCT ' in ''.join(self._field):
                self._field = ['COUNT({})'.format(''.join(self._field))]
        data = self.find()
        if self._fetchSql:
            return data
        res = list(data.values())
        return res[0]

    # 最大值
    def max(self, field):
        self._field = ['MAX({})'.format(preg_replace(r'(\w+)', r'`\1`', field))]
        return self.count()

    # 最小值
    def min(self, field):
        self._field = ['MIN({})'.format(preg_replace(r'(\w+)', r'`\1`', field))]
        return self.count()

    # 平均值
    def avg(self, field):
        self._field = ['AVG({})'.format(preg_replace(r'(\w+)', r'`\1`', field))]
        return self.count()

    # 集合值
    def sum(self, field):
        self._field = ['SUM({})'.format(preg_replace(r'(\w+)', r'`\1`', field))]
        return self.count()

    # 分组连接
    def groupConcat(self, field):
        self._field = ['GROUP_CONCAT({})'.format(preg_replace(r'(\w+)', r'`\1`', field))]
        return self.count()

    # 数据字段值
    def value(self, field):
        self.field(field)
        if '.' in field:
            _field = field
            _field = _field.split('.')
            _field = _field[1]
        else:
            _field = field
        data = self.find()
        if data is None:
            return None
        return data.get(_field)

    # 列
    def column(self, field):
        column = []
        self._field = []
        self.field(field)
        if '.' in field:
            _field = field
            _field = _field.split('.')
            _field = _field[1]
        else:
            _field = field
        _list = self.select()
        for item in _list:
            column.append(item.get(_field))
        return column

    # 获取表字段
    def getFields(self):
        is_sqlite3 = False
        if len(self.sqlite) > 0:
            is_sqlite3 = True
            desc = self.query('PRAGMA table_info({})'.format(self._table))
        else:
            desc = self.query('SHOW COLUMNS FROM {}'.format(self._table))
            # SHOW FULL COLUMNS FROM table  # 数据表结构(包括注释)
            # SHOW TABLE STATUS  # 数据表与注释
            # SHOW TABLE STATUS LIKE 'table'  # 指定数据表
        fields = {}
        for item in desc:
            item = dict(item)
            if preg_match('^(char|varchar|text|tinytext|mediumtext|longtext)', item['type'] if is_sqlite3 else item['Type'], re.I):
                if is_sqlite3:
                    fields[item['name']] = '' if item['dflt_value'] is None else item['dflt_value'].strip("'")
                else:
                    fields[item['Field']] = '' if item['Default'] is None else item['Default']
            elif preg_match('^(datetime|date|time|timestamp)', item['type'] if is_sqlite3 else item['Type'], re.I):
                if is_sqlite3:
                    fields[item['name']] = item['dflt_value'].strip("'")
                else:
                    fields[item['Field']] = item['Default']
            elif ('Field' in item) and (item['Field'] == 'id'):
                fields[item['Field']] = 0
            elif ('name' in item) and (item['name'] == 'id'):
                fields[item['name']] = 0
            else:
                if preg_match('^(float|decimal|double|numeric)', item['type'] if is_sqlite3 else item['Type'], re.I):
                    if is_sqlite3:
                        fields[item['name']] = 0 if item['dflt_value'] is None else float(item['dflt_value'].strip("'"))
                    else:
                        fields[item['Field']] = 0 if item['Default'] is None else float(item['Default'])
                else:
                    if is_sqlite3:
                        fields[item['name']] = 0 if item['dflt_value'] is None else int(item['dflt_value'].strip("'"))
                    else:
                        fields[item['Field']] = 0 if item['Default'] is None else int(item['Default'])
        return fields

    # 获取表字段类型
    def getFieldsType(self):
        is_sqlite3 = False
        if len(self.sqlite) > 0:
            is_sqlite3 = True
            desc = self.query('PRAGMA table_info({})'.format(self._table))
        else:
            desc = self.query('SHOW COLUMNS FROM {}'.format(self._table))
        fields = {}
        for item in desc:
            item = dict(item)
            field = {}
            if preg_match('^(char|varchar|text|tinytext|mediumtext|longtext)', item['type'] if is_sqlite3 else item['Type'], re.I):
                if is_sqlite3:
                    field['default'] = '' if item['dflt_value'] is None else item['dflt_value'].strip("'")
                else:
                    field['default'] = '' if item['Default'] is None else item['Default']
                field['type'] = 'string'
            elif preg_match('^(datetime|date|time|timestamp)', item['type'] if is_sqlite3 else item['Type'], re.I):
                if is_sqlite3:
                    field['default'] = item['dflt_value'].strip("'")
                    field['type'] = item['type']
                else:
                    field['default'] = item['Default']
                    field['type'] = item['Type']
            elif preg_match('^(float|decimal|double|numeric)', item['type'] if is_sqlite3 else item['Type'], re.I):
                if is_sqlite3:
                    field['default'] = 0 if item['dflt_value'] is None else float(item['dflt_value'].strip("'"))
                else:
                    field['default'] = 0 if item['Default'] is None else float(item['Default'])
                field['type'] = 'float'
            else:
                if is_sqlite3:
                    field['default'] = 0 if item['dflt_value'] is None else int(item['dflt_value'].strip("'"))
                else:
                    field['default'] = 0 if item['Default'] is None else int(item['Default'])
                field['type'] = 'int'
            if is_sqlite3:
                field['null'] = 1 if item['notnull'] == 0 else 0
            else:
                field['null'] = 1 if item['Null'] == 'YES' else 0
            if is_sqlite3:
                fields[item['name']] = field
            else:
                fields[item['Field']] = field
        return fields

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
        if self._printSql:
            print('{}\n{}\n'.format(sql, self._whereParam))
        if self._fetchSql:
            return '{}'.format(sql) % self._whereParam
        self.execute(sql, self._whereParam)
        res = self.cur.fetchone()
        if res is None:
            return res
        if self._cache > 0:
            self._cacheSql(sql, res)
        return DbDict(self._autoFormatTime(res))

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
        if self._printSql:
            print('{}\n{}\n'.format(sql, self._whereParam))
        if self._fetchSql:
            return '{}'.format(sql) % self._whereParam
        self.execute(sql, self._whereParam)
        ret = self.cur.fetchall()
        if len(ret) == 0:
            return ret
        if self._cache > 0:
            self._cacheSql(sql, ret)
        res = []
        for item in ret:
            res.append(DbDict(self._autoFormatTime(item)))
        return DbList(res)

    # 新增并返回新增ID, data: 字典类型{} 数组类型[{}]
    def insert(self, data):
        if type(data) == list and len(data) == 0:
            return 0
        if type(data) != list:
            data = [data]
        self._setParam = []
        fields = []
        for k, v in data[0].items():
            if len(self._field) > 0:
                if k in self._field:
                    fields.append(k)
            else:
                fields.append(k)
        self._field = []
        self.field(fields)
        for item in data:
            param = []
            for k, v in item.items():
                param.append(str(v))
            self._setParam.append(param)
        sql = self.buildSql('INSERT')
        if self._printSql:
            print('{}\n{}\n'.format(sql, self._setParam))
        if self._fetchSql:
            return '{}'.format(sql) % self._whereParam
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
        if self._printSql:
            print('{}\n{}\n'.format(sql, self._setParam))
        if self._fetchSql:
            return '{}'.format(sql) % self._whereParam
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
        if self._printSql:
            print('{}\n{}\n'.format(sql, self._setParam))
        if self._fetchSql:
            return '{}'.format(sql) % self._whereParam
        try:
            self.execute(sql, self._setParam)
            return self.cur.rowcount
        except Exception as e:
            print(str(e))
            self.conn.rollback()
            exit(0)

    # 执行原生SQL语句
    def query(self, sql, params=None):
        if params is None:
            params = tuple()
        if sql.upper().startswith('SELECT ') or sql.upper().startswith('PRAGMA ') or sql.upper().startswith('SHOW '):
            self.execute(sql, params)
            ret = self.cur.fetchall()
            res = []
            for item in ret:
                res.append(DbDict(item))
            return DbList(res)
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
        if Config.cache_type == 'redis':
            r = Redis()
            if r.ping():
                if res is None:
                    ret = r.get(md5(sql))
                    if ret is not None:
                        ret = json_decode(ret)
                        if type(ret) == dict:
                            return DbDict(self._autoFormatTime(ret))
                        else:
                            res = []
                            for item in ret:
                                res.append(DbDict(self._autoFormatTime(item)))
                            return DbList(res)
                    return None
                r.set(md5(sql), json_encode(res), ex=self._cache)
                return None
        filename = md5(sql)
        cacheDir = Path(runtime_path() + '/sql')
        if res is None:
            if cacheDir.is_dir():
                cacheFile = Path('{}/{}'.format(cacheDir, filename))
                if cacheFile.is_file():
                    if int(time.time()) - int(os.path.getmtime(cacheFile)) < self._cache:
                        fo = open('{}'.format(cacheFile), 'r')
                        data = fo.read()
                        fo.close()
                        ret = json_decode(data)
                        if type(ret) == dict:
                            return DbDict(self._autoFormatTime(ret))
                        else:
                            res = []
                            for item in ret:
                                res.append(DbDict(self._autoFormatTime(item)))
                            return DbList(res)
            return None
        makedir(cacheDir)
        fo = open('{}/{}'.format(cacheDir, filename), 'w+')
        fo.write(json_encode(res))
        fo.close()
        return None

    # 自动格式化时间
    def _autoFormatTime(self, item):
        if type(Config.auto_timestamp) == bool and Config.auto_timestamp is False:
            return item
        if type(self._createTime) == bool and self._createTime is False and type(self._updateTime) == bool and self._updateTime is False:
            return item
        if self._fieldsType is None:
            if type(Config.auto_timestamp) == str:
                self._fieldsType = Config.auto_timestamp
            else:
                self._fieldsType = self.getFieldsType()
        times = Config.datetime_field
        if len(times) == 0:
            times = self._datetime_field
        times = times.split(',')
        if type(self._createTime) == str and len(self._createTime) == 0:
            self._createTime = times[0]
        if type(self._updateTime) == str and len(self._updateTime) == 0:
            self._updateTime = times[1] if len(times) > 1 else 'update_time'
        datetimeFormat = self._dateFormat if len(self._dateFormat) > 0 else Config.datetime_format
        if type(self._createTime) == str and self._createTime in item:
            if type(self._fieldsType) == str:
                if self._fieldsType == 'int':
                    item[self._createTime] = date(datetimeFormat, item[self._createTime])
            elif self._fieldsType[self._createTime]['type'] == 'int':
                item[self._createTime] = date(datetimeFormat, item[self._createTime])
        if type(self._updateTime) == str and self._updateTime in item:
            if type(self._fieldsType) == str:
                if self._fieldsType == 'int':
                    item[self._updateTime] = date(datetimeFormat, item[self._updateTime])
            elif self._fieldsType[self._updateTime]['type'] == 'int':
                item[self._updateTime] = date(datetimeFormat, item[self._updateTime])
        return item

    # 构建SQL语句
    def buildSql(self, sqlType='SELECT'):
        sqlType = sqlType.upper()
        if (sqlType == 'SELECT') | (sqlType == 'S'):
            if len(self._field) == 0:
                self._field = ['*']
            sql = 'SELECT {} FROM {}{}'.format(', '.join(self._field), self._table, self._alias)
            if len(self._left) > 0:
                sql += ''.join(self._left)
            if len(self._right) > 0:
                sql += ''.join(self._right)
            if len(self._inner) > 0:
                sql += ''.join(self._inner)
            if len(self._cross) > 0:
                sql += ''.join(self._cross)
            if len(self._union) > 0:
                sql += ''.join(self._union)
            limit = ' LIMIT {},{}'.format(self._offset, self._pagesize) if self._pagesize > 0 else ''
            sql += '{}{}{}{}{}'.format(self._where, self._group, self._having, self._order, limit)
            return sql
        elif (sqlType == 'INSERT') | (sqlType == 'I'):
            self._fieldsType = None
            if type(self._createTime) != str or (type(Config.auto_timestamp) == bool and Config.auto_timestamp is False):
                pass
            else:
                _fieldsType = self.getFieldsType()
                times = Config.datetime_field
                if len(times) == 0:
                    times = self._datetime_field
                times = times.split(',')
                if len(self._createTime) == 0:
                    self._createTime = times[0]
                if self._createTime in _fieldsType:
                    if type(Config.auto_timestamp) == str:
                        self._fieldsType = Config.auto_timestamp
                    else:
                        self._fieldsType = _fieldsType[self._createTime]['type']
            if self._fieldsType is not None and self._createTime not in self._field:
                self._field.append('`{}`'.format(self._createTime))
            sql = 'INSERT INTO {} ({}) VALUES '.format(self._table, ', '.join(self._field))
            values = []
            flag = ''
            for items in self._setParam:
                flag += '('
                for item in items:
                    flag += self._sybmol + ', '
                    values.append(item)
                if self._fieldsType is not None:
                    flag += self._sybmol + ', '
                    item = ''
                    if self._fieldsType == 'int' or self._fieldsType == 'timestamp':
                        item = timestamp()
                    elif self._fieldsType == 'datetime':
                        item = date()
                    elif self._fieldsType == 'date':
                        item = date('%Y-%m-%d')
                    elif self._fieldsType == 'time':
                        item = date('%H:%M:%S')
                    elif self._fieldsType == 'year':
                        item = date('%Y')
                    values.append(item)
                flag = flag.rstrip(', ') + '), '
            flag = flag.rstrip(', ')
            sql += flag
            if self._replace:
                updateValues = []
                for item in self._field:
                    updateValues.append('{0}=VALUES({0})'.format(item))
                sql += ' ON DUPLICATE KEY UPDATE {}'.format(', '.join(updateValues))
            self._setParam = tuple(values)
            return sql
        elif (sqlType == 'UPDATE') | (sqlType == 'U'):
            self._fieldsType = None
            if type(self._updateTime) == str and (type(Config.auto_timestamp) == bool and Config.auto_timestamp is False):
                pass
            else:
                _fieldsType = self.getFieldsType()
                times = Config.datetime_field
                if len(times) == 0:
                    times = self._datetime_field
                times = times.split(',')
                if len(self._updateTime) == 0:
                    self._updateTime = times[1] if len(times) > 1 else 'update_time'
                if self._updateTime in _fieldsType:
                    if type(Config.auto_timestamp) == str:
                        self._fieldsType = Config.auto_timestamp
                    else:
                        self._fieldsType = _fieldsType[self._updateTime]['type']
            values = []
            sql = 'UPDATE {} SET '.format(self._table)
            for k, v in dict(self._setParam).items():
                if len(self._field) > 0:
                    if k not in self._field:
                        continue
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
            if self._fieldsType is not None and self._updateTime not in dict(self._setParam):
                sql += '{}=%s'.format(preg_replace(r'(\w+)', r'`\1`', self._updateTime))
                item = ''
                if self._fieldsType == 'int' or self._fieldsType == 'timestamp':
                    item = timestamp()
                elif self._fieldsType == 'datetime':
                    item = date()
                elif self._fieldsType == 'date':
                    item = date('%Y-%m-%d')
                elif self._fieldsType == 'time':
                    item = date('%H:%M:%S')
                elif self._fieldsType == 'year':
                    item = date('%Y')
                values.append(item)
            sql = sql.rstrip(', ')
            sql += str(self._where)
            if len(self._whereParam) > 0:
                for item in self._whereParam:
                    values.append(item)
            self._setParam = tuple(values)
            return sql
        elif (sqlType == 'DELETE') | (sqlType == 'D'):
            values = []
            sql = 'DELETE' + ' FROM {}{}'.format(self._table, self._where)
            if len(self._whereParam) > 0:
                for item in self._whereParam:
                    values.append(item)
            self._setParam = tuple(values)
            return sql

    # 是否存在表
    def tableExist(self, table):
        # ALTER TABLE table ENGINE=InnoDB  # 修改数据表引擎为InnoDB
        table = preg_replace('^'+self.prefix, '', table)
        has_table = False
        if len(self.sqlite) > 0:
            sql = "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{}'".format(self.prefix + table.replace(self.prefix, ''))
        else:
            sql = "SHOW TABLES LIKE '{}'".format(self.prefix + table.replace(self.prefix, ''))
        res = self.query(sql)
        if len(res) > 0:
            has_table = True
        return has_table

    # 创建数据表, 支持sqlite3
    def tableCreate(self, tables, re_create=False):
        """
        Db.tableCreate({
            'table': {
                'table_engine': 'InnoDB',
                'table_auto_increment': 10,
                'table_comment': '表注释',
                'id': {'type': 'key'},
                'name': {'type': 'varchar(255)', 'comment': '名称', 'charset': 'utf8mb4'},
                'price': {'type': 'decimal(10,2)', 'default': '0.00', 'comment': '价格'},
                'content': {'type': 'text', 'comment': '内容'},
                'clicks': {'type': 'int', 'comment': '点击数', 'index': 'clicks'},
                'add_time': {'type': 'int', 'comment': '添加时间'}
            }
        });
        """
        sql = ''
        if type(tables) == str:
            sql = tables
        else:
            for table_name, table_info in dict(tables).items():
                table_name = self.prefix + table_name.replace(self.prefix, '')
                if re_create is False and self.tableExist(table_name):
                    continue
                key_field = ''
                field_sql = ''
                index = []  # 索引
                self.tableRemove(table_name)
                sql += 'CREATE TABLE `{}` (\n'.format(table_name)
                for field_name, field_info in dict(table_info).items():
                    if field_name in ['table_engine', 'table_auto_increment', 'table_comment']:
                        continue
                    field_sql += '`{}`'.format(field_name)
                    if 'type' in field_info:
                        if field_info['type'] == 'key':
                            key_field = field_name
                            field_sql += ' integer NOT NULL PRIMARY KEY AUTOINCREMENT' if len(self.sqlite) > 0 else ' int(11) NOT NULL AUTO_INCREMENT'
                        elif len(self.sqlite) > 0 and 'varchar' in field_info['type'].lower():
                            field_sql += ' text'
                        elif len(self.sqlite) > 0 and 'int' in field_info['type'].lower():
                            field_sql += ' integer'
                        elif len(self.sqlite) > 0 and 'decimal' in field_info['type'].lower():
                            field_sql += ' numeric'
                        else:
                            field_sql += ' ' + field_info['type'].lower()
                    else:
                        field_sql += ' text' if len(self.sqlite) > 0 else ' varchar(255)'
                    if len(self.sqlite) == 0 and 'charset' in field_info:
                        field_sql += ' CHARACTER SET ' + field_info['charset'].lower()
                    if 'default' in field_info:
                        field_sql += " DEFAULT '" + field_info['default'] + "'"
                    elif 'type' in field_info and ('int' in field_info['type'].lower() or 'decimal' in field_info['type'].lower()):
                        field_sql += " DEFAULT '0.00'" if 'decimal' in field_info['type'].lower() else " DEFAULT '0'"
                    elif 'type' in field_info and 'varchar' in field_info['type'].lower():
                        field_sql += ' DEFAULT NULL'
                    if len(self.sqlite) == 0 and 'index' in field_info:
                        index.append({'name': field_info['index'], 'column': field_name})
                    if len(self.sqlite) == 0 and 'comment' in field_info:
                        field_sql += " COMMENT '" + field_info['comment'].replace("'", "\'") + "'"
                    field_sql += ',\n'
                if len(self.sqlite) == 0 and len(key_field) > 0:
                    field_sql += 'PRIMARY KEY (`{}`)'.format(key_field)
                field_sql = field_sql.strip().strip(',')
                if len(index) > 0:
                    for item in index:
                        field_sql += ',\n' + 'KEY `' + item['name'] + '` (`' + item['column'] + '`)'
                sql += field_sql.strip().strip(',') + '\n'
                sql += ')'
                if len(self.sqlite) == 0:
                    engine = table_info['table_engine'] if 'table_engine' in table_info else 'InnoDB'
                    sql += ' ENGINE={}'.format(engine)
                    if 'table_auto_increment' in table_info:
                        sql += ' AUTO_INCREMENT={}'.format(table_info['table_auto_increment'])
                    sql += ' DEFAULT CHARSET=utf8'
                    if 'table_comment' in table_info:
                        sql += " COMMENT='" + table_info['table_comment'].replace("'", "\'") + "'"
                sql += ';'
        if len(sql):
            return self.query(sql)
        return self

    # 删除表
    def tableRemove(self, table):
        return self.query('DROP TABLE IF EXISTS `{}`'.format(table))


class DbRaw(object):
    data = ''

    def __init__(self, data):
        self.data = data
        # CONVERT(`stringField`, SIGNED)  # 字符串字段转为整数
        # CONVERT(`stringField`, DECIMAL(10,2))  # 字符串字段转为浮点数
        # CONVERT(`numberField`, CHAR)  # 数值型字段转为字符串


class DbDict(dict):
    # 使用 dict.attribute 形式取值
    def __getattr__(self, item):
        if item not in self:
            return None
        return self.get(item)

    # 使用 dict.attribute 形式赋值
    def __setattr__(self, key, value):
        self[key] = value

    def __str__(self):
        return json_encode(self)


class DbList(object):
    def __init__(self, data=None):
        self.data = [] if data is None else data

    # 通过列表下标访问列表元素(支持切片)
    def __getitem__(self, index):
        if isinstance(index, int):  # 访问的是整数类型
            return self.data[index]
        elif type(index) is slice:  # 访问的是切片类型(selice切片类型)
            # index.start  # 切片起始值
            # index.stop  # 切片结束值
            # index.step  # 切片步长
            return self.data[index]
        return None

    # 通过列表下标更改列表元素
    def __setitem__(self, index, value):
        self.data[index] = value

    # 判断传入的元素是否在列表中
    def __contains__(self, item):
        return self.data.__contains__(item)

    # 返回数组元素数量
    def __len__(self, *args, **kwargs):
        return len(self.data)

    # 反转数组
    def reverse(self):
        return self.data.reverse()

    # 向列表中添加元素
    def append(self, item):
        self.data.append(item)

    # 删除并返回最后一个元素
    def pop(self, index=-1):
        return self.data.pop(index)

    # 删除指定下标元素
    def __delitem__(self, index):
        del self.data[index]

    def __str__(self):
        return json_encode(self.data)


Db = DbManager(
    host=Config.connections['mysql'].get('host', 'localhost'),
    post=Config.connections['mysql'].get('port', 3306),
    user=Config.connections['mysql'].get('user', 'root'),
    password=Config.connections['mysql'].get('password', ''),
    database=Config.connections['mysql'].get('database', ''),
    prefix=Config.connections['mysql'].get('prefix', ''),
    charset=Config.connections['mysql'].get('charset', 'utf8')
)
