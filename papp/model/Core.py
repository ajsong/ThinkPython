# Developed by @mario 1.3.20230112
from ..tool import *


class Core(object):
    # 可在继承类中增加以下属性
    # __connection = 'mysql'  # 数据库连接
    # __name = 'table'  # 表名(不带表前缀)
    # __table = 'prefix_table'  # 完整表名
    # __dateFormat = '%Y-%m-%d %H:%M:%S'  # 输出日期字段自动格式化
    # __createTime = 'create_time'  # 创建日期字段名, False关闭自动写入/格式化
    # __updateTime = 'update_time'  # 更新日期字段名, False关闭自动写入/格式化

    def __getattr__(self, name):
        curMethods = uncamelize(name).split('_', 1)

        def fn(*args):
            if len(curMethods) == 1:
                print('Features under development: {}{})'.format(name, str(args).strip(',)')))
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

    def _connectName(self):
        connection = ''
        formatStr = '{}__connection'.format(self.__class__.__name__)
        if formatStr in dir(self):
            connection = getattr(self, formatStr)
        if len(connection) == 0:
            return 'mysql'
        if connection not in Config.connections.keys():
            print('Connections have no parameter: ' + connection)
            exit(0)
        return connection

    def _tableName(self):
        import importlib
        connection = Config.connections[self._connectName()]
        formatStr = '{}__name'.format(self.__class__.__name__)
        if formatStr in dir(self):
            return connection['prefix'] + getattr(self, formatStr).replace(connection['prefix'], '')
        formatStr = '{}__table'.format(self.__class__.__name__)
        if formatStr in dir(self):
            return getattr(self, formatStr)
        file = importlib.import_module(self.__module__).__file__
        return connection['prefix'] + uncamelize(file.replace(os.path.dirname(file) + '/', '').replace('.py', ''))

    def _autoTime(self, attributeType):
        field = ''
        if attributeType == 0:
            formatStr = '{}__dateFormat'.format(self.__class__.__name__)
            if formatStr in dir(self):
                field = getattr(self, formatStr)
        else:
            formatStr = '{}__{}'.format(self.__class__.__name__, 'createTime' if attributeType == 1 else 'updateTime')
            if formatStr in dir(self):
                field = getattr(self, formatStr)
        return field

    def _setDb(self):
        connection = self._connectName()
        return Db if connection == 'mysql' else DbManager.instance(Config.connections[connection])

    def _dbManager(self):
        return self._setDb().table(self._tableName()).dateFormat(self._autoTime(0)).createTime(self._autoTime(1)).updateTime(self._autoTime(2))

    def alias(self, alias):
        return self._dbManager().alias(alias)

    def leftJoin(self, table, alias='', on=''):
        return self._dbManager().leftJoin(table, alias, on)

    def rightJoin(self, table, alias='', on=''):
        return self._dbManager().rightJoin(table, alias, on)

    def innerJoin(self, table, alias='', on=''):
        return self._dbManager().innerJoin(table, alias, on)

    def crossJoin(self, table, alias=''):
        return self._dbManager().crossJoin(table, alias)

    def unionAll(self, table, field=None, where='', group='', having='', order='', offset=0, pagesize=0):
        return self._dbManager().unionAll(table, field, where, group, having, order, offset, pagesize)

    def where(self, where, param1='', param2=''):
        return self._dbManager().where(where, param1, param2)

    def whereRaw(self, where):
        return self._dbManager().whereRaw(where)

    def whereOr(self, where, param1='', param2=''):
        return self._dbManager().whereOr(where, param1, param2)

    def whereYear(self, field, value=''):
        return self._dbManager().whereYear(field, value)

    def whereMonth(self, field, value=''):
        return self._dbManager().whereMonth(field, value)

    def whereWeek(self, field, value=''):
        return self._dbManager().whereWeek(field, value)

    def whereDay(self, field, value='today'):
        return self._dbManager().whereDay(field, value)

    def whereTime(self, field, operator, value=''):
        return self._dbManager().whereTime(field, operator, value)

    def whereColumn(self, field1, operator, field2=None, logic='AND'):
        return self._dbManager().whereColumn(field1, operator, field2, logic)

    def field(self, field):
        return self._dbManager().field(field)

    def fieldRaw(self, field):
        return self._dbManager().fieldRaw(field)

    def withoutField(self, field):
        return self._dbManager().withoutField(field)

    def distinct(self, field):
        return self._dbManager().distinct(field)

    def group(self, group):
        return self._dbManager().group(group)

    def having(self, having):
        return self._dbManager().having(having)

    def order(self, field, order=''):
        return self._dbManager().order(field, order)

    def orderRaw(self, order):
        return self._dbManager().orderRaw(order)

    def orderField(self, field, value):
        return self._dbManager().orderField(field, value)

    def limit(self, offset, pagesize=-100):
        return self._dbManager().limit(offset, pagesize)

    def page(self, page, pagesize):
        return self._dbManager().page(page, pagesize)

    def cache(self, cache):
        return self._dbManager().cache(cache)

    def replace(self, replace=True):
        return self._dbManager().replace(replace)

    def printSql(self, printSql=True):
        return self._dbManager().printSql(printSql)

    def fetchSql(self, fetchSql=True):
        return self._dbManager().fetchSql(fetchSql)

    def inc(self, field, step=1):
        return self._dbManager().inc(field, step)

    def dec(self, field, step=1):
        return self._dbManager().dec(field, step)

    def exist(self):
        return self._dbManager().exist()

    def count(self):
        return self._dbManager().count()

    def max(self, field):
        return self._dbManager().max(field)

    def min(self, field):
        return self._dbManager().min(field)

    def avg(self, field):
        return self._dbManager().avg(field)

    def sum(self, field):
        return self._dbManager().sum(field)

    def groupConcat(self, field):
        return self._dbManager().groupConcat(field)

    def value(self, field):
        return self._dbManager().value(field)

    def column(self, field):
        return self._dbManager().column(field)

    def getFields(self):
        return self._dbManager().getFields()

    def getFieldsType(self):
        return self._dbManager().getFieldsType()

    def find(self, field=None):
        return self._dbManager().find(field)

    def select(self, field=None):
        return self._dbManager().select(field)

    def insert(self, data):
        return self._dbManager().insert(data)

    def update(self, data=None):
        return self._dbManager().update(data)

    def delete(self, where=None):
        return self._dbManager().delete(where)

    def buildSql(self, sqlType='SELECT'):
        return self._dbManager().buildSql(sqlType)
