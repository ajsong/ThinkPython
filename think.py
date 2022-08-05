# Developed by @mario 1.1.20220803
from argparse import ArgumentParser
from papp.tool import *


def createControllerFile(param):
    path = root_path() + '/papp/controller'
    clazz = camelize(param)
    if '@' in param:
        params = param.split('@')
        path += '/' + params[0].lower()
        clazz = camelize(params[1])
    if not Path(path).is_dir():
        makedir(path)
        file_put_contents(path + '/__init__.py')
    filepath = path + '/' + clazz + '.py'
    if file_exist(filepath):
        print('Controller:\033[31m' + filepath + '\033[m already exist.\n')
        return None
    method = '''from .Core import *


class '''+clazz+'''(Core):

    def index(self):
        return success()
'''
    file_put_contents(filepath, method)
    return filepath


def createModelFile(param):
    path = root_path() + '/papp/model'
    clazz = camelize(param)
    if not Path(path).is_dir():
        makedir(path)
        file_put_contents(path + '/__init__.py')
    filepath = path + '/' + clazz + '.py'
    if file_exist(filepath):
        print('Model:\033[31m' + filepath + '\033[m already exist.\n')
        return None
    method = '''from ..tool import *


class '''+clazz+'''Class(type):

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
            else:
                return method(part, args[0])

        return fn

    @staticmethod
    def _connectname():
        connection = ''
        if hasattr('''+clazz+'''Class, '_connection_'):
            connection = getattr('''+clazz+'''Class, '_connection_')
        if len(connection) == 0:
            return Db
        if connection not in connections.keys():
            raise Exception('Connections have no parameter: ' + connection)
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
    def _tablename():
        if hasattr('''+clazz+'''Class, '_name_'):
            return getattr('''+clazz+'''Class, '_name_')
        file = __file__
        return uncamelize(file.replace(os.path.dirname(file) + '/', '').replace('.py', ''))

    @staticmethod
    def alias(alias):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).alias(alias)

    @staticmethod
    def leftJoin(table, on):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).leftJoin(table, on)

    @staticmethod
    def rightJoin(table, on):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).rightJoin(table, on)

    @staticmethod
    def innerJoin(table, on):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).innerJoin(table, on)

    @staticmethod
    def crossJoin(table):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).crossJoin(table)

    @staticmethod
    def where(where, param1='', param2=''):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).where(where, param1, param2)

    @staticmethod
    def whereOr(where, param1='', param2=''):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).whereOr(where, param1, param2)

    @staticmethod
    def whereDay(field, value='today'):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).whereDay(field, value)

    @staticmethod
    def whereTime(field, operator, value=''):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).whereTime(field, operator, value)

    @staticmethod
    def field(field):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).field(field)

    @staticmethod
    def distinct(field):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).distinct(field)

    @staticmethod
    def group(group):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).group(group)

    @staticmethod
    def having(having):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).having(having)

    @staticmethod
    def order(field, order=''):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).order(field, order)

    @staticmethod
    def orderField(field, value):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).orderField(field, value)

    @staticmethod
    def limit(offset, pagesize=-100):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).limit(offset, pagesize)

    @staticmethod
    def page(page, pagesize):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).page(page, pagesize)

    @staticmethod
    def cache(cache):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).cache(cache)

    @staticmethod
    def replace(replace=True):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).replace(replace)

    @staticmethod
    def fetchSql(fetchSql=True):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).fetchSql(fetchSql)

    @staticmethod
    def inc(field, step=1):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).inc(field, step)

    @staticmethod
    def dec(field, step=1):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).dec(field, step)

    @staticmethod
    def exist():
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).exist()

    @staticmethod
    def count():
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).count()

    @staticmethod
    def max(field):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).max(field)

    @staticmethod
    def min(field):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).min(field)

    @staticmethod
    def avg(field):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).avg(field)

    @staticmethod
    def sum(field):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).sum(field)

    @staticmethod
    def groupConcat(field):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).groupConcat(field)

    @staticmethod
    def value(field):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).value(field)

    @staticmethod
    def column(field):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).column(field)

    @staticmethod
    def find(field=None):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).find(field)

    @staticmethod
    def select(field=None):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).select(field)

    @staticmethod
    def insert(data):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).insert(data)

    @staticmethod
    def update(data=None):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).update(data)

    @staticmethod
    def delete(where=None):
        return '''+clazz+'''Class._connectname().name('''+clazz+'''Class._tablename()).delete(where)


class '''+clazz+'''(metaclass='''+clazz+'''Class):
    pass
'''
    file_put_contents(filepath, method)
    return filepath


if __name__ == '__main__':
    parser = ArgumentParser()  # https://www.jb51.net/article/179189.htm
    parser.add_argument('--make:controller', type=str, dest='controller', help='Create a new resource controller class')
    parser.add_argument('--make:model', type=str, dest='model', help='Create a new model class')
    args = parser.parse_args()

    if args.controller is not None:
        arguments = args.controller.split(',')
        for arg in arguments:
            res = createControllerFile(arg)
            if res is not None:
                print('Controller:\033[32m' + res + '\033[m created successfully.')
        print()
        exit(0)

    if args.model is not None:
        arguments = args.model.split(',')
        for arg in arguments:
            res = createModelFile(camelize(arg))
            if res is not None:
                print('Model:\033[32m' + res + '\033[m created successfully.')
        print()
        exit(0)

    file = __file__
    file = file.replace(os.path.dirname(file) + '/', '')
    usage = '''
\033[33mUsage:\033[m
  python '''+file+''' [commands]

\033[33mAvailable commands:\033[m
  \033[32m--make:controller\033[m   Create a new resource controller class
  \033[32m--make:model\033[m        Create a new model class
'''
    print(usage)
