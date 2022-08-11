from ..tool import *


class MemberClass(type):

    # 数据库操作(自动设定表名)===================================================
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
            elif curMethods[0] == 'field':
                return method({part: args[0]})
            else:
                return method(part, args[0])

        return fn

    @staticmethod
    def _connectname():
        connection = ''
        if hasattr(MemberClass, '_connection_'):
            connection = getattr(MemberClass, '_connection_')
        if len(connection) == 0:
            return Db
        if connection not in connections.keys():
            raise Exception('Connections have no parameter: ' + connection)
        return DbManager.instance(connections[connection])

    @staticmethod
    def _tablename():
        if hasattr(MemberClass, '_name_'):
            return getattr(MemberClass, '_name_')
        file = __file__
        return uncamelize(file.replace(os.path.dirname(file) + '/', '').replace('.py', ''))

    @staticmethod
    def alias(alias):
        return MemberClass.connectname().name(MemberClass.tablename()).alias(alias)

    @staticmethod
    def leftJoin(table, on):
        return MemberClass.connectname().name(MemberClass.tablename()).leftJoin(table, on)

    @staticmethod
    def rightJoin(table, on):
        return MemberClass.connectname().name(MemberClass.tablename()).rightJoin(table, on)

    @staticmethod
    def innerJoin(table, on):
        return MemberClass.connectname().name(MemberClass.tablename()).innerJoin(table, on)

    @staticmethod
    def crossJoin(table):
        return MemberClass.connectname().name(MemberClass.tablename()).crossJoin(table)

    @staticmethod
    def unionAll(table, field=None, where='', group='', having='', order='', offset=0, pagesize=0):
        return MemberClass._connectname().name(MemberClass._tablename()).unionAll(table, field, where, group, having, order, offset, pagesize)

    @staticmethod
    def where(where, param1='', param2=''):
        return MemberClass.connectname().name(MemberClass.tablename()).where(where, param1, param2)

    @staticmethod
    def whereOr(where, param1='', param2=''):
        return MemberClass.connectname().name(MemberClass.tablename()).whereOr(where, param1, param2)

    @staticmethod
    def whereDay(field, value='today'):
        return MemberClass.connectname().name(MemberClass.tablename()).whereDay(field, value)

    @staticmethod
    def whereTime(field, operator, value=''):
        return MemberClass.connectname().name(MemberClass.tablename()).whereTime(field, operator, value)

    @staticmethod
    def field(field):
        return MemberClass.connectname().name(MemberClass.tablename()).field(field)

    @staticmethod
    def distinct(field):
        return MemberClass.connectname().name(MemberClass.tablename()).distinct(field)

    @staticmethod
    def group(group):
        return MemberClass.connectname().name(MemberClass.tablename()).group(group)

    @staticmethod
    def having(having):
        return MemberClass.connectname().name(MemberClass.tablename()).having(having)

    @staticmethod
    def order(field, order=''):
        return MemberClass.connectname().name(MemberClass.tablename()).order(field, order)

    @staticmethod
    def orderField(field, value):
        return MemberClass.connectname().name(MemberClass.tablename()).orderField(field, value)

    @staticmethod
    def limit(offset, pagesize=-100):
        return MemberClass.connectname().name(MemberClass.tablename()).limit(offset, pagesize)

    @staticmethod
    def page(page, pagesize):
        return MemberClass.connectname().name(MemberClass.tablename()).page(page, pagesize)

    @staticmethod
    def cache(cache):
        return MemberClass.connectname().name(MemberClass.tablename()).cache(cache)

    @staticmethod
    def replace(replace=True):
        return MemberClass.connectname().name(MemberClass.tablename()).replace(replace)

    @staticmethod
    def fetchSql(fetchSql=True):
        return MemberClass.connectname().name(MemberClass.tablename()).fetchSql(fetchSql)

    @staticmethod
    def inc(field, step=1):
        return MemberClass.connectname().name(MemberClass.tablename()).inc(field, step)

    @staticmethod
    def dec(field, step=1):
        return MemberClass.connectname().name(MemberClass.tablename()).dec(field, step)

    @staticmethod
    def exist():
        return MemberClass.connectname().name(MemberClass.tablename()).exist()

    @staticmethod
    def count():
        return MemberClass.connectname().name(MemberClass.tablename()).count()

    @staticmethod
    def max(field):
        return MemberClass.connectname().name(MemberClass.tablename()).max(field)

    @staticmethod
    def min(field):
        return MemberClass.connectname().name(MemberClass.tablename()).min(field)

    @staticmethod
    def avg(field):
        return MemberClass.connectname().name(MemberClass.tablename()).avg(field)

    @staticmethod
    def sum(field):
        return MemberClass.connectname().name(MemberClass.tablename()).sum(field)

    @staticmethod
    def groupConcat(field):
        return MemberClass.connectname().name(MemberClass.tablename()).groupConcat(field)

    @staticmethod
    def value(field):
        return MemberClass.connectname().name(MemberClass.tablename()).value(field)

    @staticmethod
    def column(field):
        return MemberClass.connectname().name(MemberClass.tablename()).column(field)

    @staticmethod
    def find(field=None):
        return MemberClass.connectname().name(MemberClass.tablename()).find(field)

    @staticmethod
    def select(field=None):
        return MemberClass.connectname().name(MemberClass.tablename()).select(field)

    @staticmethod
    def insert(data):
        return MemberClass.connectname().name(MemberClass.tablename()).insert(data)

    @staticmethod
    def update(data=None):
        return MemberClass.connectname().name(MemberClass.tablename()).update(data)

    @staticmethod
    def delete(where=None):
        return MemberClass.connectname().name(MemberClass.tablename()).delete(where)

    @staticmethod
    def buildSql(sqlType='SELECT'):
        return MemberClass._connectname().name(MemberClass._tablename()).buildSql(sqlType)


class Member(metaclass=MemberClass):
    pass
