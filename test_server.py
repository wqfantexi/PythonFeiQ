from socketserver import ThreadingUDPServer
from socketserver import BaseRequestHandler, DatagramRequestHandler
import socket
import logging
import time, datetime


class UdpHandle(BaseRequestHandler):
    COUNT = 0

    def handle(self):
        # t = threading.Thread(target=self.dealPacket, args=(self.client_address, self.request[0]))
        # t.start()
        packet = self.request[0]

        # print(datetime.datetime.now().isoformat()+str(UdpHandle.COUNT))
        self.server.socket.sendto(packet, self.client_address)
        UdpHandle.COUNT += 1


UDPSERVER = ThreadingUDPServer(('0.0.0.0', 50001), UdpHandle)
UDPSERVER.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
UDPSERVER.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 60000)

UDPSERVER.serve_forever()
