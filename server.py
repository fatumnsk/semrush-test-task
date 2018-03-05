import sys
import asyncio
import struct
import bson
from sys import getsizeof


class ParseError(ValueError):
    pass


class Parser:
    def request_encode(self, response):
        body_data = response['body']
        try:
            body = bson.dumps(body_data)
        except Exception as err:
            print(f"error: {err}")
            raise ParseError("wrong data format")
        size, key, magic, rsv = response['header']
        size = getsizeof(body)
        key = b"result"
        header = struct.pack('Q 16s l l', size, key, int(magic, 16), rsv)
        print(f"response sent > header: {(size, key, magic, rsv)} body: {response['body']}")
        return header + b"\n" + body + b"\n\n"

    def request_decode(self, data):
        try:
            parts = data.split(b"\n")
            header, body = parts[0], parts[1]
            size, key, magic, rsv = struct.unpack('Q 16s l l', header)
            # Удаляем NULL символы из поля key
            key = key.split(b"\x00")[0]
            magic = hex(magic)
            header = size, key, magic, rsv
            request = {
                'header': header,
                'body': bson.loads(body)
                }
            print(f"request received > header: {request['header']} body: {request['body']}")
        except (ValueError, IndexError, struct.error) as err:
            print(f"error: {err}")
            raise ParseError("wrong data format")
        return request


class EchoProtocol(asyncio.Protocol):
    def __init__(self):
        self.parser = Parser()

    def process_data(self, data):
        response = self.parser.request_decode(data)
        try:
            response['body']['sum'] = response['body']['a'] + response['body']['b']
            return self.parser.request_encode(response)
        except TypeError as err:
            print(f"cannot calculate {err}")
            self.transport.write(f"error\n{err}\n\n".encode())
            return

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        try:
            response = self.process_data(data)
        except ParseError as err:
            self.transport.write(f"error\n{err}\n\n".encode())
            return
        if response:
            self.transport.write(response)


def run(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        EchoProtocol,
        host, port
    )
    server = loop.run_until_complete(coro)
    print(f"starting server: {host}:{port}")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = sys.argv[1]
        if port.isdigit() and int(port) < 65536:
            run('127.0.0.1', port)
        else:
            print("wrong port number")
    else:
        run('127.0.0.1', 8888)