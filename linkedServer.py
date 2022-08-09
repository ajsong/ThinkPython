import ctypes
import inspect
import signal
from argparse import ArgumentParser
from threading import Thread
from papp.tool import *
from papp.tool.WebSocket.WebSocketServer import WebsocketServer, WSServer


clients = []
threads = []


def stopThread(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError('Invalid thread id')
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError('PyThreadState_SetAsyncExc failed')


def getSubprocess(_cmd, index):
    import subprocess
    f = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(f.stdout.readline, b''):
        res = str(line, 'utf-8').strip()
        clients[index].sendMessage(res)


class linkedServer(WebsocketServer):

    def handleMessage(self):
        data = json_decode(self.data)
        if 'set' in data.keys():
            if data['set'] == 'ch':
                symbol = data['symbol']
                period = data['period']
                ch = 'market.%susdt.kline.%s' % (symbol, period)
                for client in clients:
                    if client == self:
                        index = clients.index(client)
                        stopThread(threads[index].ident, SystemExit)
                        _cmd = '/usr/local/bin/python3.8 linkedClient.py --ch ' + ch
                        thread = Thread(target=getSubprocess, args=(_cmd, index,))
                        thread.start()
                        threads[index] = thread

    def handleConnected(self):
        # print('Connected')
        clients.append(self)
        _cmd = '/usr/local/bin/python3.8 linkedClient.py'
        thread = Thread(target=getSubprocess, args=(_cmd, len(clients)-1,))
        thread.start()
        threads.append(thread)

    def handleClose(self):
        for client in clients:
            if client == self:
                index = clients.index(client)
                stopThread(threads[index].ident, SystemExit)
                threads.remove(threads[index])
                break
        clients.remove(self)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--port', default=7312, type=int)
    args = parser.parse_args()

    server = WSServer('', args.port, linkedServer)

    def close_sig_handler(signal, frame):
        server.close()
        sys.exit()
    signal.signal(signal.SIGINT, close_sig_handler)
    server.serveforever()
