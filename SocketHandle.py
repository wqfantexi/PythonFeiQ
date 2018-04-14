from socketserver import BaseRequestHandler
from WorkThread import Instance, UdpPacketData
from LogHelp import logger


class UdpHandle(BaseRequestHandler):
    def handle(self):
        logger.debug('Got Msg from ' + str(self.client_address))

        packet=UdpPacketData(self.client_address, self.request[0])
        Instance.putRecvMessage(packet)

    #发送数据报文
    def send(self, packet:UdpPacketData):
        self.server.socket.sendto(packet.ip, packet.data)