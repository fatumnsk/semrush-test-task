import socket
import bson
import struct
from sys import getsizeof

right = ["Q 16s l l", (0, b"sum", 0xAA34529A, 0)]
wrong = ["Q 16s 16s l", (0, b"sum", b"0xAA34529A", 0)]

test_data = [
    {'header': right, 'body': {'a': 1, 'b': 2}},
    {'header': right, 'body': {'a': 32, 'b': -11}},
    {'header': right, 'body': {'a': 0, 'b': 23}},
    {'header': right, 'body': {'a': -5, 'b': -2}},
    {'header': right, 'body': {'a': 1, 'b': 18446744073709551614}},
    {'header': right, 'body': {'a': 0.1, 'b': 0.1}},
    {'header': right, 'body': {'a': 3, 'b': 18446744073709551613}},
    {'header': right, 'body': {'a': 3, 'b': None}},
    {'header': right, 'body': {'a': 3, 'b': 'a'}},
    {'header': right, 'body': {'a': 3, 'b': ''}},
    {'header': wrong, 'body': {'a': 3, 'b': 1}},
    ]


class ClientError(Exception):
    pass


class ClientSocketError(ClientError):
    pass


class Client:
    def __init__(self, host, port, timeout=None):
        self.host, self.port = host, port
        try:
            self.connection = socket.create_connection((host, port), timeout)
        except socket.error as err:
            raise ClientSocketError("error create connection", err)

    def prepare(self, data):
        size, key, magic, rsv = data['header'][1]
        body = bson.dumps(data['body'])
        size = getsizeof(body)
        header = struct.pack(data['header'][0], size, key, magic, rsv)
        request_data = header + b"\n" + body + b"\n\n"
        return request_data

    def read(self):
        data = b""
        while not data.endswith(b"\n\n"):
            try:
                data += self.connection.recv(1024)
            except socket.error as err:
                raise ClientSocketError("error receiving data", err)

        try:
            header_data, body_data = data.split(b"\n")[:2]
            header = struct.unpack('Q 16s l l', header_data)
            body = bson.loads(body_data)
        except struct.error as err:
            raise ClientSocketError("error receiving data", err)
        return header, body

    def send(self, data):
        request = self.prepare(data)
        try:
            self.connection.sendall(
                request
            )
        except socket.error as err:
            raise ClientSocketError("send data error", err)

        try:
            data = self.read()
            print(data)
            return data
        except ClientSocketError as err:
            print(f"unsuccess {data} {err}")

    def close(self):
        try:
            self.connection.close()
        except socket.error as err:
            raise ClientSocketError("error close connection", err)


def main():
    client = Client("127.0.0.1", 8888, timeout=5)
    for data in test_data:
        client.send(data)
    client.close()


if __name__ == "__main__":
    main()
