from easterly import WebSocketServer, ServerEvent, ServerProtocol

users = {}

SET_USERNAME = "#name"
GET_USERS = "#users"
MESSAGE = "#chat"

def on_connect(id):
	users[id] = "Guest"

def on_disconnect(id):
	del users[id]

def set_username(id, data):
	users[id] = data[0]

def get_users(id, data):
	response = {
		'type': 'users',
		'users': users.values()
	}
	wss.whisper(id, response)

def message(id, data):
	response = {
		'type': 'msg',
		'user':	users[id],
		'message': data[0],
	}
	wss.broadcast(response)

wss = WebSocketServer(r"/ws", 8899, protocol=ServerProtocol.SEPERATOR("|"))
wss.add_event_listeners([
	(ServerEvent.ON_CONNECT, on_connect),
	(ServerEvent.ON_DISCONNECT, on_disconnect),
	(SET_USERNAME, set_username),
	(GET_USERS, get_users),
	(MESSAGE, message),
])
wss.start()
