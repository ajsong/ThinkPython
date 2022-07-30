from WebSocketClient import WSClient

if __name__ == "__main__":
    # ws_client = WSClient("ws://localhost:7312", lambda message: print("call_back message:", message))
    ws_client = WSClient("ws://localhost:7312", None)
    ws_client.run()

    while True:
        msg = input("")
        if msg == 'exit':
            ws_client.close()
            exit(0)
        ws_client.send_message(msg)
