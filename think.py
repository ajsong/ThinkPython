# Developed by @mario 1.6.20220829
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
    method = '''from .Core import *


class _'''+clazz+'''(Core):
    pass


'''+clazz+''' = _'''+clazz+'''()
'''
    file_put_contents(filepath, method)
    return filepath


if __name__ == '__main__':
    # from argparse import ArgumentParser
    # parser = ArgumentParser()  # https://www.jb51.net/article/179189.htm
    # parser.add_argument('--make:controller', type=str, dest='controller', help='Create a new resource controller class')
    # parser.add_argument('--make:model', type=str, dest='model', help='Create a new model class')
    # args = parser.parse_args()

    args = sys.argv[1:]
    if len(args) > 0:
        commands = args[0]
        if 'make:' in commands:
            if len(args) == 1:
                print('Missing arguments')
                exit(0)
            commands = commands.strip('make:')
            if commands == 'controller':
                arguments = args[1].split(',')
                for arg in arguments:
                    res = createControllerFile(arg)
                    if res is not None:
                        print('Controller:\033[32m' + res + '\033[m created successfully.')
                print()
                exit(0)

            if commands == 'model':
                arguments = args[1].split(',')
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
  \033[32mmake:controller\033[m   Create a new resource controller class
  \033[32mmake:model\033[m        Create a new model class
'''
    print(usage)
