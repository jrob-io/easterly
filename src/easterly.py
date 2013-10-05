import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import datetime
from threading import Thread, Timer
import uuid
import itertools
import functools
import json
import signal


DEFAULT_PORT = 8888

_servers = {}

class ServerEvent():
	ON_MESSAGE = "on_message"
	ON_CONNECT = "on_connect"
	ON_DISCONNECT = "on_disconnect"

class ServerProtocol():
	@staticmethod
	def SEPERATOR(sep="\n"):
		def _seperator(msg, sep):
			type, nsep, data = msg.partition(sep)
			data = data.split(sep)
			return (type, data)
		return functools.partial(_seperator, sep=sep)	

	@staticmethod	
	def JSON(id="type"):
		def _json(msg, id):
			try:
				data = json.loads(msg)
			except ValueError:
				return ("","")
			type = data[id]
			del data[id]
			return (type, data)
		return functools.partial(_json, id=id)	

	@staticmethod
	def BITS(num_bits):
		def _bits(msg, num_bits=8):
			pass
		return functools.partial(_bits, num_bits=num_bits)



class WebSocketServer():
	def __init__(self, uri, port, protocol=None):
		self.clients = {}		
		self.protocol = protocol
		
		self._callbacks = {}
		self._intervals = {}
		self._interval_counter = itertools.count()

		_servers[uri] = self

		self.ioloop = tornado.ioloop.IOLoop.instance()
		self.application = tornado.web.Application([(uri, WebSocket)])
		self.application.listen(port)

		signal.signal(signal.SIGINT, self._sigint)

	def _sigint(self, signal, frame):
			self.stop()

	'''
	User Event Setters
	'''
	def add_event_listener(self, event, callback):
		self._callbacks[event] = callback

	def add_event_listeners(self, callbacks):
		for event, callback in callbacks:			
			self._callbacks[event] = callback
	
	def remove_event_listener(self, event):
		del self._callbacks[event]

	def dispatch_event(self, event):
		try:
			callback = self._callbacks[event]
			self.ioloop.add_callback(callback)
		except KeyError:
			#print "Error - " + event + ": does not exist"
			pass


	'''
	Server Events
	'''

	def connection_received(self, socket):
		self.clients[socket.id] = socket
		try:
			self._callbacks[ServerEvent.ON_CONNECT](socket.id)
		except KeyError:
			#print "Error - " + ServerEvent.ON_CONNECT + ": does not exist"
			pass

	def msg_received(self, id, message):
		try:
			self._callbacks[ServerEvent.ON_MESSAGE](id, message)
		except KeyError:
			#print "Error - " + ServerEvent.ON_MESSAGE + ": does not exist"
			pass
		if self.protocol != None:						
			type, data = self.protocol(message)
			try:
				self._callbacks["#"+type](id, data)
			except KeyError:
				#print "Error - #" + type + ": does not exist"
				pass


	def connection_lost(self, id):
		del self.clients[id]
		try:
			self._callbacks[ServerEvent.ON_DISCONNECT](socket.id)
		except KeyError:
			#print "Error - " + ServerEvent.ON_DISCONNECT + ": does not exist"
			pass


	'''
	Public
	'''

	def start(self):
		self.ioloop.start()

	def stop(self):
		self.ioloop.stop()

	def set_timeout(self, callback, milliseconds):
		return self.ioloop.add_timeout(datetime.timedelta(milliseconds=milliseconds), callback)

	def clear_timeout(self, id):
		self.ioloop.remove_timeout(id)

	def set_interval(self, callback, seconds):
		def new_interval():
			callback()
			self._intervals[id] = self.set_timeout(new_interval, seconds)
			print	self._intervals[id] 
		id = self._interval_counter.next()
		self._intervals[id] = self.set_timeout(new_interval, seconds)
		return id

	def clear_interval(self, id):
		self.ioloop.remove_timeout(self._intervals[id])
		del self._intervals[id]

	#TODO
	def set_interval_loop(self, callbacks):
		pass		

	def broadcast(self, msg):
		for client in self.clients.values():
			client.write_message(msg)

	def whisper(self, id, msg):
		self.clients[id].write_message(msg)




class WebSocket(tornado.websocket.WebSocketHandler):
	def open(self):
		self.sid = self.request.uri
		self.id = uuid.uuid1().hex
		_servers[self.sid].connection_received(self)

	def on_close(self):
		_servers[self.sid].connection_lost(self.id)

	def on_message(self, message):
		_servers[self.sid].msg_received(self.id, message)

	

