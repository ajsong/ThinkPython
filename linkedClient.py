from argparse import ArgumentParser
from papp.tool import *
from papp.tool.WebSocket.WebSocketClient import WSClient

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--ch', default='market.btcusdt.kline.1min', type=str)
    args = parser.parse_args()

    topic = args.ch
    lastSub = ''

    def onMessage(msg):
        global lastSub
        if len(lastSub) == 0:
            ws_client.send_message({'sub': topic})
            lastSub = topic
        obj = json.loads(msg)
        if 'ping' in obj:
            ws_client.send_message({'pong': obj['ping']})
        elif 'subbed' in obj:
            pass
            # ws_client.send_message({'req': topic})  # 获取所有数据
        elif 'unsubbed' in obj:
            lastSub = ''
        else:
            print(json_encode(obj), flush=True)

    ws_client = WSClient('wss://api.huobi.pro/ws', onMessage, True)
    ws_client.run()
