import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import time
from threading import Thread, Timer
import uuid
import argparse

DEFAULT_PORT = 8888

class Server():
	clients = {}
	state = {}

	def __init__(self):
		self.ioloop = tornado.ioloop.IOLoop.instance()
	
	def start(self):
		self.ioloop.start()

	def set_application(self, app, port):
		self.application = app
		app.listen(port)
		print "Listening on port " + str(port)
		self.start()

	def init_state(self):
		return dict(type="init")

	def on_message(self, id, message):
		pass

	def on_open(self, id):
		pass

	def on_close(self, id):
		pass

	def timeout(self, seconds, callback):
		self.ioloop.add_timeout(time.time() + seconds, callback)

	def broadcast(self, msg):
		for c in self.clients.items():
			c[1].write_message(msg)

	def whisper(self, id, msg):
		self.clients[id].write_message(msg)

	def add_client(self, socket):
		self.clients[socket.id] = socket
		self.on_open(socket.id)

	def remove_client(self, id):
		del self.clients[id]
		self.on_close(id)

class Single:
	server = Server()

class WebSocket(tornado.websocket.WebSocketHandler):
	def open(self):
		self.id = uuid.uuid1().hex
		Single.server.add_client(self)
		self.write_message(Single.server.init_state())

	def on_message(self, message):
		Single.server.on_message(self.id, message)

	def on_close(self):
		Single.server.remove_client(self.id)

def application():
	return tornado.web.Application([(r'/ws', WebSocket)])

def set(server):
	Single.server = server
	return server

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='A simple WebSocket server using Tornado.')
	parser.add_argument('-p', metavar='<port>',type=int, help='port number')
	args = parser.parse_args()
	if args.p == None:
		port = DEFAULT_PORT
	else:
		port = args.p

	Single.server.set_application(application(), port)
