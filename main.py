from LogHelp import logger
logger.debug('程序启动')

from socketserver import UDPServer
from SocketHandle import UdpHandle
from WorkThread import Instance
import socket
from SecurityManager import Security


if __name__ == '__main__':
    s=Security()
    #UDPSERVER = UDPServer(('', 2425), UdpHandle)

    #UDPSERVER.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #Instance.startMessage(UDPSERVER.socket.sendto)
    #UDPSERVER.serve_forever()