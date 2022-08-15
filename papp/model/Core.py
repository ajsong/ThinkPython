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
        if connection not in connections.keys():
            print('Connections have no parameter: ' + connection)
            exit(0)
        db = DbManager.instance(connections[connection])
        self.db = db
        return db

    def _tablename(self):
        if '{}__name'.format(self.__class__.__name__) in dir(self):
            return self.db.prefix + getattr(self, '{}__name'.format(self.__class__.__name__)).replace(self.db.prefix, '')
        if '{}__table'.format(self.__class__.__name__) in dir(self):
            return getattr(self, '{}__table'.format(self.__class__.__name__))
        file = importlib.import_module(self.__module__).__file__
        return uncamelize(file.replace(os.path.dirname(file) + '/', '').replace('.py', ''))

    def alias(self, alias):
        return self._connectname().table(self._tablename()).alias(alias)

    def leftJoin(self, table, on):
        return self._connectname().table(self._tablename()).leftJoin(table, on)

    def rightJoin(self, table, on):
        return self._connectname().table(self._tablename()).rightJoin(table, on)

    def innerJoin(self, table, on):
        return self._connectname().table(self._tablename()).innerJoin(table, on)

    def crossJoin(self, table):
        return self._connectname().table(self._tablename()).crossJoin(table)

    def unionAll(self, table, field=None, where='', group='', having='', order='', offset=0, pagesize=0):
        return self._connectname().table(self._tablename()).unionAll(table, field, where, group, having, order, offset, pagesize)

    def where(self, where, param1='', param2=''):
        return self._connectname().table(self._tablename()).where(where, param1, param2)

    def whereOr(self, where, param1='', param2=''):
        return self._connectname().table(self._tablename()).whereOr(where, param1, param2)

    def whereDay(self, field, value='today'):
        return self._connectname().table(self._tablename()).whereDay(field, value)

    def whereMonth(self, field, value=''):
        return self._connectname().table(self._tablename()).whereMonth(field, value)

    def whereYear(self, field, value=''):
        return self._connectname().table(self._tablename()).whereYear(field, value)

    def whereTime(self, field, operator, value=''):
        return self._connectname().table(self._tablename()).whereTime(field, operator, value)

    def field(self, field):
        return self._connectname().table(self._tablename()).field(field)

    def withoutField(self, field):
        return self._connectname().table(self._tablename()).withoutField(field)

    def distinct(self, field):
        return self._connectname().table(self._tablename()).distinct(field)

    def group(self, group):
        return self._connectname().table(self._tablename()).group(group)

    def having(self, having):
        return self._connectname().table(self._tablename()).having(having)

    def order(self, field, order=''):
        return self._connectname().table(self._tablename()).order(field, order)

    def orderField(self, field, value):
        return self._connectname().table(self._tablename()).orderField(field, value)

    def limit(self, offset, pagesize=-100):
        return self._connectname().table(self._tablename()).limit(offset, pagesize)

    def page(self, page, pagesize):
        return self._connectname().table(self._tablename()).page(page, pagesize)

    def cache(self, cache):
        return self._connectname().table(self._tablename()).cache(cache)

    def replace(self, replace=True):
        return self._connectname().table(self._tablename()).replace(replace)

    def fetchSql(self, fetchSql=True):
        return self._connectname().table(self._tablename()).fetchSql(fetchSql)

    def inc(self, field, step=1):
        return self._connectname().table(self._tablename()).inc(field, step)

    def dec(self, field, step=1):
        return self._connectname().table(self._tablename()).dec(field, step)

    def exist(self):
        return self._connectname().table(self._tablename()).exist()

    def count(self):
        return self._connectname().table(self._tablename()).count()

    def max(self, field):
        return self._connectname().table(self._tablename()).max(field)

    def min(self, field):
        return self._connectname().table(self._tablename()).min(field)

    def avg(self, field):
        return self._connectname().table(self._tablename()).avg(field)

    def sum(self, field):
        return self._connectname().table(self._tablename()).sum(field)

    def groupConcat(self, field):
        return self._connectname().table(self._tablename()).groupConcat(field)

    def value(self, field):
        return self._connectname().table(self._tablename()).value(field)

    def column(self, field):
        return self._connectname().table(self._tablename()).column(field)

    def getFields(self):
        return self._connectname().table(self._tablename()).getFields()

    def find(self, field=None):
        return self._connectname().table(self._tablename()).find(field)

    def select(self, field=None):
        return self._connectname().table(self._tablename()).select(field)

    def insert(self, data):
        return self._connectname().table(self._tablename()).insert(data)

    def update(self, data=None):
        return self._connectname().table(self._tablename()).update(data)

    def delete(self, where=None):
        return self._connectname().table(self._tablename()).delete(where)

    def buildSql(self, sqlType='SELECT'):
        return self._connectname().table(self._tablename()).buildSql(sqlType)
