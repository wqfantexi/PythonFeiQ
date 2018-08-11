#消息发送的基类

from FeiQ.Struct.User import User
from FeiQ.Struct.UdpPacketData import UdpPacketData


#消息发送类
class MsgSender:
    packet:UdpPacketData = None
    cmd = 0

    def __init__(self):
        self.packet = UdpPacketData()

    def setData(self,me:User,ip,port):
        me.saveToPacket(self.packet)
        self.packet.ip = ip
        self.packet.port = port

    # 序列化数据
    def save(self):
        self.packet.cmd = self.cmd
        self.packet.extra = self.getExtra()

        self.packet.save()

    #子类必须实现
    def getExtra(self):
        pass