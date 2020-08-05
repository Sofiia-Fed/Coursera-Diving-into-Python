import socket
import time

class ClientError(Exception):
	pass

class Client:
	def __init__(self, host, port, timeout=None):
		self.sock = socket.create_connection((host, port), timeout)

	def get(self, metric_name):
		try:
			request = f'get {metric_name}\n'
			self.sock.sendall(request.encode('utf-8'))

			answer = self.sock.recv(1024).decode()
			if answer.startswith('error'):
				raise ClientError

			try:
				result = {}
				if answer != 'ok\n\n':
					answer = answer.split('\n')[1:-2]

					for line in answer:
						metric, value, time = line.split(" ")
						if metric not in result:
							result[metric] = []
						result[metric].append((int(time), float(value)))

					for metric in result:
						result[metric].sort(key=lambda x: x[0])

				return result

			except ValueError:
				raise ClientError

		except socket.error as err:
			print(f'Socket error data: {err}')

	def put(self, metric_name, value, timestamp=None):
		timestamp = timestamp or int(time.time())

		try:
			request = f'put {metric_name} {value} {timestamp}\n'
			self.sock.sendall(request.encode('utf-8'))
			answer = self.sock.recv(1024).decode()
			if not answer.startswith('ok'):
				raise ClientError

		except socket.error as err:
			print(f'Socket error data: {err}')

	def close(self):
		self.sock.close()