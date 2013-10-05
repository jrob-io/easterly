from easterly import WebSocketServer, ServerEvent, ServerProtocol

def message(id, message):
	wss.broadcast(message)

wss = WebSocketServer(r"/ws", 8899)
wss.add_event_listener(ServerEvent.ON_MESSAGE, message)
wss.start()
