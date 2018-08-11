from LogHelp import logger
import IPMSG
from enum import Enum
import time
import datetime
import setting
# 定义UDP报文数据结构
class UdpPacketData:
    PACKETCOUNT = 0  # 定义报文数量,静态全局变量

    ip = '' # IP地址
    port = 0 # 端口号
    data = bytes() # 数据报文
    mac = '' #MAC地址

    version = '' #版本号暂时不解析，里面包含MAC地址

    loginname = ''  # 电脑登录用户名
    hostname = '' #电脑主机名
    nickname = '' #用户设置昵称
    groupname = '' #分组名

    packno = 0 #报文编号

    cmd = 0 #命令码

    extra = bytes()

    #接收时调用的构造函数
    def __init__(self, addr:(str,int)=None, data:bytes=None):
        if addr is None or data is None:
            self.createSendPacket()
            return
        else:
            UdpPacketData.PACKETCOUNT += 1

            self.ip = addr[0]  # IP地址
            self.port = addr[1]  # 端口号
            self.data = data  # 数据报文
    #获取用户的ID
    def getUserId(self):
        return self.ip + self.port

    #发送时调用的构造函数
    def createSendPacket(self):
        UdpPacketData.PACKETCOUNT += 1

        self.packno = UdpPacketData.PACKETCOUNT;

    def dump(self):
        arrBytes = self.data.split(sep=IPMSG.PACKET_SEP)
        if len(arrBytes) < 5:
            logger.error('来自%s的报文不正确，报文内容%s'%(self.ip, self.data.decode(IPMSG.ENCODETYPE)))

        self.version = arrBytes[0].decode(IPMSG.ENCODETYPE)

        arrVersion = self.version.split('#')
        self.mac = arrVersion[2]

        self.packno = int(arrBytes[1])

        self.loginname = arrBytes[2].decode(IPMSG.ENCODETYPE)

        self.hostname = arrBytes[3].decode(IPMSG.ENCODETYPE)

        self.cmd = int(arrBytes[4].decode(IPMSG.ENCODETYPE))

        if len(arrBytes) > 5:
            tmpExtra = IPMSG.PACKET_SEP.join(arrBytes[5:])
            lastIndex = tmpExtra.rfind(b'\0')
            if lastIndex != -1:
                self.extra = tmpExtra[:lastIndex]
            else:
                self.extra = tmpExtra

    def save(self):
        self.data = IPMSG.PACKET_SEP.join([
            self.version.encode(IPMSG.ENCODETYPE),
            str(self.packno).encode(IPMSG.ENCODETYPE),
            self.loginname.encode(IPMSG.ENCODETYPE),
            self.hostname.encode(IPMSG.ENCODETYPE),
            str(self.cmd).encode(IPMSG.ENCODETYPE),
            self.extra + b'\0'#最后一位必须为0
        ])



# 飞秋好友定义
class User:
    ip = ''  # IP地址
    port = 0  # 端口号
    mac = ''  # MAC地址
    version = ''
    loginname = ''  # 电脑登录用户名
    hostname = ''  # 电脑主机名
    nickname = ''  # 用户设置昵称
    groupname = '' # 分组名
    headpic = 'static\\headpic\\001.bmp'
    state = setting.FRIEND_ONLINE

    lstContents = None #聊天记录

    def __init__(self,packet:UdpPacketData = None):
        if packet is None:
            return
        self.ip = packet.ip
        self.port = packet.port
        self.mac = packet.mac
        self.loginname = packet.loginname
        self.hostname = packet.hostname

        self.lstContents = []

    def saveToPacket(self, packet:UdpPacketData):
        packet.ip = self.ip
        packet.port = self.port
        packet.hostname = self.hostname
        packet.loginname = self.loginname
        packet.version = self.version
        packet.nickname = self.nickname
        packet.groupname = self.groupname

    def getId(self):
        return self.ip + '@' + str(self.port)

    def __str__(self):
        return self.loginname + '@' + self.hostname + '#' + self.groupname

    #更新用户数据
    def update(self, user):
        if len(user.version) > 0:
            self.version = user.version
        if len(user.loginname) > 0:
            self.loginname = user.loginname
        if len(user.hostname) > 0:
            self.hostname = user.hostname
        if len(user.nickname) > 0:
            self.nickname = user.nickname
        if len(user.groupname) > 0:
            self.groupname = user.groupname

class ContentType(Enum):
    UNKNOWN = 0
    TEXT = 1
    KNOCK = 2

#报文内容
class PacketContent:
    def __init__(self, type, peer, bIsSend):
        self.type = type
        self.peer = peer #对端ID
        self.tx = bIsSend
        self.time = datetime.datetime.now()

    def __repr__(self):
        return 'PacketContent(peer=%s)'%(self.peer)

# 文本内容
class TextContent(PacketContent):
    def __init__(self, text, format, peer, tx):
        PacketContent.__init__(self, ContentType.TEXT, peer, tx)
        self.text = text
        self.format = format

    def __repr__(self):
        return 'TextContent(text=%s\tformat=%s)'%(self.text,self.format)

#用户发来的数据报文
class Message:
    def __init__(self):
        self.friend = User()
        self.cmd = 0 #命令ID
        self.extra = b'' #数据内容
        self.packno = 0 #当前数据包的报文号
        self.contents=[] #内部存储PacketContent

