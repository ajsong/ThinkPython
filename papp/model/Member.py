from ..tool import *


class Member(object):

    # 数据库操作(自动设定表名)===================================================
    @staticmethod
    def connectname():
        connection = ''
        if hasattr(Member, '_connection_'):
            connection = getattr(Member, '_connection_')
        if len(connection) == 0:
            return Db
        if connection not in connections.keys():
            raise Exception('Connections have no parameter: ' + connection)
        sqlite = connections[connection].get('sqlite')
        if sqlite is not None:
            return DbManager(sqlite=sqlite)
        return DbManager(
            host=connections[connection].get('host', 'localhost'),
            post=connections[connection].get('port', 3306),
            user=connections[connection].get('user', 'root'),
            password=connections[connection].get('password', ''),
            database=connections[connection].get('database', ''),
            prefix=connections[connection].get('prefix', ''),
            charset=connections[connection].get('charset', 'utf8')
        )

    @staticmethod
    def tablename():
        if hasattr(Member, '_name_'):
            return getattr(Member, '_name_')
        file = __file__
        return uncamelize(file.replace(os.path.dirname(file) + '/', '').replace('.py', ''))

    @staticmethod
    def alias(alias):
        return Member.connectname().name(Member.tablename()).alias(alias)

    @staticmethod
    def leftJoin(table, on):
        return Member.connectname().name(Member.tablename()).leftJoin(table, on)

    @staticmethod
    def rightJoin(table, on):
        return Member.connectname().name(Member.tablename()).rightJoin(table, on)

    @staticmethod
    def innerJoin(table, on):
        return Member.connectname().name(Member.tablename()).innerJoin(table, on)

    @staticmethod
    def crossJoin(table):
        return Member.connectname().name(Member.tablename()).crossJoin(table)

    @staticmethod
    def where(where, param1='', param2=''):
        return Member.connectname().name(Member.tablename()).where(where, param1, param2)

    @staticmethod
    def whereOr(where, param1='', param2=''):
        return Member.connectname().name(Member.tablename()).whereOr(where, param1, param2)

    @staticmethod
    def whereDay(field, value='today'):
        return Member.connectname().name(Member.tablename()).whereDay(field, value)

    @staticmethod
    def whereTime(field, operator, value=''):
        return Member.connectname().name(Member.tablename()).whereTime(field, operator, value)

    @staticmethod
    def field(field):
        return Member.connectname().name(Member.tablename()).field(field)

    @staticmethod
    def distinct(field):
        return Member.connectname().name(Member.tablename()).distinct(field)

    @staticmethod
    def group(group):
        return Member.connectname().name(Member.tablename()).group(group)

    @staticmethod
    def having(having):
        return Member.connectname().name(Member.tablename()).having(having)

    @staticmethod
    def order(field, order=''):
        return Member.connectname().name(Member.tablename()).order(field, order)

    @staticmethod
    def orderField(field, value):
        return Member.connectname().name(Member.tablename()).orderField(field, value)

    @staticmethod
    def limit(offset, pagesize=-100):
        return Member.connectname().name(Member.tablename()).limit(offset, pagesize)

    @staticmethod
    def page(page, pagesize):
        return Member.connectname().name(Member.tablename()).page(page, pagesize)

    @staticmethod
    def cache(cache):
        return Member.connectname().name(Member.tablename()).cache(cache)

    @staticmethod
    def replace(replace=True):
        return Member.connectname().name(Member.tablename()).replace(replace)

    @staticmethod
    def fetchSql(fetchSql=True):
        return Member.connectname().name(Member.tablename()).fetchSql(fetchSql)

    @staticmethod
    def inc(field, step=1):
        return Member.connectname().name(Member.tablename()).inc(field, step)

    @staticmethod
    def dec(field, step=1):
        return Member.connectname().name(Member.tablename()).dec(field, step)

    @staticmethod
    def exist():
        return Member.connectname().name(Member.tablename()).exist()

    @staticmethod
    def count():
        return Member.connectname().name(Member.tablename()).count()

    @staticmethod
    def max(field):
        return Member.connectname().name(Member.tablename()).max(field)

    @staticmethod
    def min(field):
        return Member.connectname().name(Member.tablename()).min(field)

    @staticmethod
    def avg(field):
        return Member.connectname().name(Member.tablename()).avg(field)

    @staticmethod
    def sum(field):
        return Member.connectname().name(Member.tablename()).sum(field)

    @staticmethod
    def groupConcat(field):
        return Member.connectname().name(Member.tablename()).groupConcat(field)

    @staticmethod
    def value(field):
        return Member.connectname().name(Member.tablename()).value(field)

    @staticmethod
    def column(field):
        return Member.connectname().name(Member.tablename()).column(field)

    @staticmethod
    def find(field=None):
        return Member.connectname().name(Member.tablename()).find(field)

    @staticmethod
    def select(field=None):
        return Member.connectname().name(Member.tablename()).select(field)

    @staticmethod
    def insert(data):
        return Member.connectname().name(Member.tablename()).insert(data)

    @staticmethod
    def update(data=None):
        return Member.connectname().name(Member.tablename()).update(data)

    @staticmethod
    def delete(where=None):
        return Member.connectname().name(Member.tablename()).delete(where)
