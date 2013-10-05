from easterly import WebSocketServer, ServerEvent, ServerProtocol

def on_message(id, message):
	wss.whisper(id, message)

wss = WebSocketServer(r"/ws", 8899)
wss.add_event_listener(ServerEvent.ON_MESSAGE, on_message)
wss.start()
