import importlib
from ..tool import *


class Core(object):

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

    def _connectname(self):
        connection = ''
        if '{}__connection'.format(self.__class__.__name__) in dir(self):
            connection = getattr(self, '{}__connection'.format(self.__class__.__name__))
        if len(connection) == 0:
            self.db = Db
            return Db
        if connection not in Config.connections.keys():
            print('Connections have no parameter: ' + connection)
            exit(0)
        db = DbManager.instance(Config.connections[connection])
        self.db = db
        return db

    def _tablename(self):
        if '{}__name'.format(self.__class__.__name__) in dir(self):
            return self.db.prefix + getattr(self, '{}__name'.format(self.__class__.__name__)).replace(self.db.prefix, '')
        if '{}__table'.format(self.__class__.__name__) in dir(self):
            return getattr(self, '{}__table'.format(self.__class__.__name__))
        file = importlib.import_module(self.__module__).__file__
        return self.db.prefix + uncamelize(file.replace(os.path.dirname(file) + '/', '').replace('.py', ''))

    def _autotime(self, attributeType):
        field = ''
        if attributeType == 0:
            if '{}__timeFormat'.format(self.__class__.__name__) in dir(self):
                field = getattr(self, '{}__timeFormat'.format(self.__class__.__name__))
        else:
            if '{}__{}'.format(self.__class__.__name__, 'createTime' if attributeType == 1 else 'updateTime') in dir(self):
                field = getattr(self, '{}__{}'.format(self.__class__.__name__, 'createTime' if attributeType == 1 else 'updateTime'))
        return field

    def _setDb(self):
        return self._connectname().table(self._tablename()).timeFormat(self._autotime(0)).createTime(self._autotime(1)).updateTime(self._autotime(2))

    def alias(self, alias):
        return self._setDb().alias(alias)

    def leftJoin(self, table, on):
        return self._setDb().leftJoin(table, on)

    def rightJoin(self, table, on):
        return self._setDb().rightJoin(table, on)

    def innerJoin(self, table, on):
        return self._setDb().innerJoin(table, on)

    def crossJoin(self, table):
        return self._setDb().crossJoin(table)

    def unionAll(self, table, field=None, where='', group='', having='', order='', offset=0, pagesize=0):
        return self._setDb().unionAll(table, field, where, group, having, order, offset, pagesize)

    def where(self, where, param1='', param2=''):
        return self._setDb().where(where, param1, param2)

    def whereOr(self, where, param1='', param2=''):
        return self._setDb().whereOr(where, param1, param2)

    def whereDay(self, field, value='today'):
        return self._setDb().whereDay(field, value)

    def whereMonth(self, field, value=''):
        return self._setDb().whereMonth(field, value)

    def whereYear(self, field, value=''):
        return self._setDb().whereYear(field, value)

    def whereTime(self, field, operator, value=''):
        return self._setDb().whereTime(field, operator, value)

    def field(self, field):
        return self._setDb().field(field)

    def withoutField(self, field):
        return self._setDb().withoutField(field)

    def distinct(self, field):
        return self._setDb().distinct(field)

    def group(self, group):
        return self._setDb().group(group)

    def having(self, having):
        return self._setDb().having(having)

    def order(self, field, order=''):
        return self._setDb().order(field, order)

    def orderField(self, field, value):
        return self._setDb().orderField(field, value)

    def limit(self, offset, pagesize=-100):
        return self._setDb().limit(offset, pagesize)

    def page(self, page, pagesize):
        return self._setDb().page(page, pagesize)

    def cache(self, cache):
        return self._setDb().cache(cache)

    def replace(self, replace=True):
        return self._setDb().replace(replace)

    def fetchSql(self, fetchSql=True):
        return self._setDb().fetchSql(fetchSql)

    def inc(self, field, step=1):
        return self._setDb().inc(field, step)

    def dec(self, field, step=1):
        return self._setDb().dec(field, step)

    def exist(self):
        return self._setDb().exist()

    def count(self):
        return self._setDb().count()

    def max(self, field):
        return self._setDb().max(field)

    def min(self, field):
        return self._setDb().min(field)

    def avg(self, field):
        return self._setDb().avg(field)

    def sum(self, field):
        return self._setDb().sum(field)

    def groupConcat(self, field):
        return self._setDb().groupConcat(field)

    def value(self, field):
        return self._setDb().value(field)

    def column(self, field):
        return self._setDb().column(field)

    def getFields(self):
        return self._setDb().getFields()

    def getFieldsType(self):
        return self._setDb().getFieldsType()

    def find(self, field=None):
        return self._setDb().find(field)

    def select(self, field=None):
        return self._setDb().select(field)

    def insert(self, data):
        return self._setDb().insert(data)

    def update(self, data=None):
        return self._setDb().update(data)

    def delete(self, where=None):
        return self._setDb().delete(where)

    def buildSql(self, sqlType='SELECT'):
        return self._setDb().buildSql(sqlType)
