# Developed by @mario 1.0.20220802
from optparse import OptionParser
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
        print("Controller:\033[31m" + filepath + "\033[m already exist.\n")
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
        print("Model:\033[31m" + filepath + "\033[m already exist.\n")
        return None
    method = '''from ..tool import *


class '''+clazz+'''(object):

    # 数据库操作(自动设定表名)===================================================
    @staticmethod
    def connectname():
        connection = ''
        if hasattr('''+clazz+''', '_connection_'):
            connection = getattr('''+clazz+''', '_connection_')
        if len(connection) == 0:
            return Db
        if connection not in connections.keys():
            raise Exception('Connections have no parameter: ' + connection)
        return DbManager(
            host=connections[connection].get('host', 'localhost'),
            post=connections[connection].get("port", 3306),
            user=connections[connection].get('user', 'root'),
            password=connections[connection].get('password', ''),
            database=connections[connection].get('database', ''),
            prefix=connections[connection].get('prefix', ''),
            charset=connections[connection].get('charset', 'utf8')
        )

    @staticmethod
    def tablename():
        if hasattr('''+clazz+''', '_name_'):
            return getattr('''+clazz+''', '_name_')
        file = __file__
        return uncamelize(file.replace(os.path.dirname(file) + '/', '').replace('.py', ''))

    @staticmethod
    def alias(alias):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).alias(alias)

    @staticmethod
    def leftJoin(table, on):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).leftJoin(table, on)

    @staticmethod
    def rightJoin(table, on):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).rightJoin(table, on)

    @staticmethod
    def innerJoin(table, on):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).innerJoin(table, on)

    @staticmethod
    def crossJoin(table):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).crossJoin(table)

    @staticmethod
    def where(where, param1='', param2=''):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).where(where, param1, param2)

    @staticmethod
    def whereOr(where, param1='', param2=''):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).whereOr(where, param1, param2)

    @staticmethod
    def whereDay(field, value='today'):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).whereDay(field, value)

    @staticmethod
    def whereTime(field, operator, value=''):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).whereTime(field, operator, value)

    @staticmethod
    def field(field):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).field(field)

    @staticmethod
    def distinct(field):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).distinct(field)

    @staticmethod
    def group(group):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).group(group)

    @staticmethod
    def having(having):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).having(having)

    @staticmethod
    def order(field, order=''):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).order(field, order)

    @staticmethod
    def orderField(field, value):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).orderField(field, value)

    @staticmethod
    def limit(offset, pagesize=-100):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).limit(offset, pagesize)

    @staticmethod
    def page(page, pagesize):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).page(page, pagesize)

    @staticmethod
    def cache(cache):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).cache(cache)

    @staticmethod
    def replace(replace=True):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).replace(replace)

    @staticmethod
    def fetchSql(fetchSql=True):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).fetchSql(fetchSql)

    @staticmethod
    def inc(field, step=1):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).inc(field, step)

    @staticmethod
    def dec(field, step=1):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).dec(field, step)

    @staticmethod
    def exist():
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).exist()

    @staticmethod
    def count():
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).count()

    @staticmethod
    def max(field):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).max(field)

    @staticmethod
    def min(field):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).min(field)

    @staticmethod
    def avg(field):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).avg(field)

    @staticmethod
    def sum(field):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).sum(field)

    @staticmethod
    def groupConcat(field):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).groupConcat(field)

    @staticmethod
    def value(field):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).value(field)

    @staticmethod
    def column(field):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).column(field)

    @staticmethod
    def find(field=None):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).find(field)

    @staticmethod
    def select(field=None):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).select(field)

    @staticmethod
    def insert(data):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).insert(data)

    @staticmethod
    def update(data=None):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).update(data)

    @staticmethod
    def delete(where=None):
        return '''+clazz+'''.connectname().name('''+clazz+'''.tablename()).delete(where)
'''
    file_put_contents(filepath, method)
    return filepath


if __name__ == '__main__':

    file = __file__
    file = file.replace(os.path.dirname(file) + '/', '')
    usage = '''
  python %prog [commands]

\033[33mAvailable commands:\033[m
 \033[33mmake\033[m
  \033[32m--controller\033[m   Create a new resource controller class
  \033[32m--model\033[m        Create a new model class'''

    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("--controller", type="string", dest="controller", help="Create a new resource controller class")
    parser.add_option("--model", type="string", dest="model", help="Create a new model class")
    (options, args) = parser.parse_args()

    if options.controller is not None:
        arguments = options.controller.split(',')
        for arg in arguments:
            res = createControllerFile(arg)
            if res is not None:
                print("Controller:\033[32m" + res + "\033[m created successfully.")
        print()
        exit(0)

    if options.model is not None:
        arguments = options.model.split(',')
        for arg in arguments:
            res = createModelFile(camelize(arg))
            if res is not None:
                print("Model:\033[32m" + res + "\033[m created successfully.")
        print()
        exit(0)

    print('\n\033[33mUsage:\033[m' + usage.replace('%prog', file) + '\n')
