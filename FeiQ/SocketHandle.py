from socketserver import BaseRequestHandler, DatagramRequestHandler
from FeiQ.WorkThread import Instance
from FeiQ.Struct.UdpPacketData import UdpPacketData
from FeiQ.Util.LogHelp import logger
import threading

class UdpHandle(BaseRequestHandler):
    def handle(self):
        # t = threading.Thread(target=self.dealPacket, args=(self.client_address, self.request[0]))
        # t.start()
        # logger.debug('Got Msg from ' + str(self.client_address))
        # self.server.socket.sendto(self.request[0], self.client_address)
        packet=UdpPacketData(self.client_address, self.request[0])
        Instance.putRecvMessage(packet)
        # self.server.socket.sendto(self.request[0], self.client_address)

    def dealPacket(self, address, data):
        logger.debug('Got Msg from ' + str(address))
        packet = UdpPacketData(address, data)
        Instance.putRecvMessage(packet)

    #发送数据报文
    def send(self, packet:UdpPacketData):
        self.server.socket.sendto(packet.ip, packet.data)