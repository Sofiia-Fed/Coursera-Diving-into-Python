import asyncio

storage = {}

class IncorrectRequestFormatError(Exception):
	pass

class ClientServerProtocol(asyncio.Protocol):
	def connection_made(self, transport):
		self.transport = transport

	def data_received(self, data):
		request = self.process_data(data.decode())
		print(request)
		self.transport.write(request.encode())

	def process_data(self, request):
		try:
			if not request.endswith('\n'):
				raise IncorrectRequestFormatError('Request must end with "\\n"!')

			command, *information = request[:-1].split()
			
			if command == 'get' and len(information) == 1:
				answer = 'ok\n'
				if information[0] == '*':
					for metric in storage:
						answer += '\n'.join(storage[metric]) + '\n'
				else:
					if information[0] in storage:
						answer += '\n'.join(storage[information[0]]) + '\n'

				return answer + '\n'

			elif command == 'put' and len(information) == 3:
				metric, value, timestamp = information
				value, timestamp = float(value), int(timestamp)

				if metric not in storage:
					storage[metric] = []

				information = f'{metric} {value} {timestamp}'

				existing_value = list(filter(lambda x: x.split()[-1] == str(timestamp), storage[metric]))
				if not existing_value:
					storage[metric].append(information)
				else:
					index = storage[metric].index(existing_value[0])
					storage[metric][index] = information

				return 'ok\n\n'

			else:
				error_message = 'Request commands must be "get" ot "put" only or'
				error_message += '\nthere\'re a lot of or not enough values in the request!'
				raise IncorrectRequestFormatError(error_message)

		except IncorrectRequestFormatError as err:
			print(f'IncorrectRequestFormatError: {err}.')
			return 'error\nwrong command\n\n'

		except ValueError as err:
			print(f'ValueError: {err}. Unable to convert data types!')
			return 'error\nwrong command\n\n'


def run_server(host, port):
	loop = asyncio.get_event_loop()
	coro = loop.create_server(ClientServerProtocol, host, port)
	server = loop.run_until_complete(coro)

	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass

	server.close()
	loop.run_until_complete(server.wait_closed())
	loop.close()


