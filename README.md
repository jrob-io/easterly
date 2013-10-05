easterly
========
*unstable - in early development*

**easterly** is a simple event-based WebSocket server built on top of Tornado.

Sample usage:
````python
# Simple echo server
from easterly import WebSocketServer, ServerEvent

def on_message(id, message):
	wss.whisper(id, message)

wss = WebSocketServer(r"/ws", 8899)
wss.add_event_listener(ServerEvent.ON_MESSAGE, on_message)
wss.start()
````

Some Documentation
-------------
*WebSocketServer*.**add_event_listener**(event, callback)
> Adds a listener for the provided *event*. Calls *callback* when the event is triggered. The server has three events: ServerEvent.ON_MESSAGE, ServerEvent.ON_CONNECT, ServerEvent.ON_DISCONNECT

> You can add custom events to interact with the ServerProtocol. For example, you can assign a callback for when the client sends a '#chat' event (see the Better Chat Server example).

*WebSocketServer*.**remove_event_listener**(event)
> Removes the listener for the provided *event*.

*WebSocketServer*.**set_interval**(callback, milliseconds)

*WebSocketServer*.**set_timeout**(callback, milliseconds)
> Adds *callback* to the IOLoop to be called every n *milliseconds*.

> Returns an id to be passed into **clear_interval**.

*WebSocketServer*.**clear_interval**(id)

*WebSocketServer*.**clear_timeout**(id)
> Cancels the repeated action set up using **set_interval**.

*WebSocketServer*.**whisper**(id, message)
> Sends a *message* to the client matching the provided *id*.

*WebSocketServer*.**broadcast**(message)
> Sends a *message* to all connected clients.


Examples
--------

### Basic Chat Server
A basic chat server that echos incoming messages to all connections.
````python
from easterly import WebSocketServer, ServerEvent

def message(id, message):
	wss.broadcast(message)

wss = WebSocketServer(r"/ws", 8899)
wss.add_event_listener(ServerEvent.ON_MESSAGE, message)
wss.start()
````

### Better Chat Server
A little more advanced chat server that supports usernames.
```python
from easterly import WebSocketServer, ServerEvent, ServerProtocol

users = {}

SET_USERNAME = "#name"
GET_USERS = "#users"
MESSAGE = "#chat"

def set_guest(id):
	users[id] = "Guest"

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
	(ServerEvent.ON_CONNECT, set_guest),
	(SET_USERNAME, set_username),
	(GET_USERS, get_users),
	(MESSAGE, message),
])
wss.start()
```

