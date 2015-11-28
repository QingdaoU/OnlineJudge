# coding=utf-8
import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from runner import JudgeInstanceRunner


class AsyncXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer):
    pass


server = AsyncXMLRPCServer(('0.0.0.0', 8080), SimpleXMLRPCRequestHandler, allow_none=True)
server.register_instance(JudgeInstanceRunner())
server.serve_forever()