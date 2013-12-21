from operator import attrgetter

class Handler():
	def __init__(self, event, priority, callback):
		self.event = event
		self.priority = priority
		self.callback = callback
		self.hid = -1

	def __str__(self):
		return "Handler(event='%s', priority=%d, callback='%s')" % (self.event, self.priority, self.callback)

	def __repr__(self):
		return self.__str__()

class HandlerManager():
	def __init__(self):
		self.handlers = {}
		self._counter = 0

	def add_handler(self, handler):
		self._counter += 1
		handler.hid = self._counter
		try:
			self.handlers[handler.event].append(handler)
		except:
			self.handlers[handler.event] = [handler]
		return self._counter

	def remove_handler(self, hid):
		for handler_list in self.handlers.values():
			# TODO: make this loop Pythonic:
			for i in range(len(handler_list) - 1):
				if handler_list[i].hid == hid:
					del handler_list[i]
					return True
		return False

	def sort_handlers(self): #Need to make this reverse the list!
		for k in self.handlers:
			self.handlers[k].sort(key=attrgetter('priority'), reverse=True)

	def printhandlers(self):
		for hid in self.handlers:
			handler = self.handlers[hid]
			print("%s: %s" % (hid, repr(handler)))

# TODO: Enum for event priorities or something?
