import json
import websocket
import time
import threading
import gzip
from io import BytesIO


# pip install websocket_client
class WebsocketClient(object):
    def __init__(self, url, callback=None, ungzip=False):
        super(WebsocketClient, self).__init__()
        self.is_running = False
        self.url = url
        self.callback = callback
        self.ungzip = ungzip

    def on_message(self, ws, message):
        if self.ungzip:
            buff = BytesIO(message)
            f = gzip.GzipFile(fileobj=buff)
            message = f.read().decode('utf-8')
        # print(message)
        if self.callback is not None:
            self.callback(message)

    def on_error(self, error):
        print("Client error:\n", error)

    def on_close(self, ws):
        self.ws.close()
        self.is_running = False

    def on_open(self, ws):
        self.is_running = True

    def close_connect(self):
        self.ws.close()

    def send_message(self, message):
        try:
            if type(message) != str:
                message = json.dumps(message)
            self.ws.send(message)
        except BaseException as err:
            pass

    def run(self):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.url,
                                         on_message=lambda ws, message: self.on_message(ws, message),
                                         on_error=lambda error: self.on_error(error),
                                         on_close=lambda ws: self.on_close(ws))
        self.ws.on_open = lambda ws: self.on_open(ws)
        self.is_running = False
        while True:
            if not self.is_running:
                self.ws.run_forever()
            time.sleep(3)


class WSClient(object):
    def __init__(self, url, callback=None, ungzip=False):
        super(WSClient, self).__init__()
        self.client = WebsocketClient(url, callback, ungzip)
        self.client_thread = None

    def run(self):
        self.client_thread = threading.Thread(target=self.run_client)
        self.client_thread.start()

    def run_client(self):
        self.client.run()

    def close(self):
        self.client.close_connect()

    def send_message(self, message):
        self.client.send_message(message)
