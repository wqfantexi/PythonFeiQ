from FeiQ.Struct import IPMSG
from FeiQ.Util.LogHelp import logger


# {0}_lbt4_{1}#{2}#{3}#{4}#{5}#{6}#{7}#{8}
#
# {0}: 版本号，为1，确保和ipmsg兼容
# {1}: 内建头像的ID号。
# {2}: 个人等级标志。用十进制标示，以下转换成16进制分析（你懂的 :D ）
#      0x100XX -- ☉☉
#      0x080XX -- ☉?
#     0x040XX -- ☉☆
#      0x020XX -- ☉
#      0x010XX -- ??
#     0x008XX -- ?☆
#      0x004XX -- ?
#     0x002XX -- ☆☆
#      0x001XX -- ☆
# {3}: MAC 地址
# {4}: 自定义头像的图片文件的大小，没有则为0
# {5}: 自我形象的图片文件大小，没有则为0
# {6}: 不知道，还没分析出来，填0
# {7}: 4000
# {8}: 9
#
# 定义UDP报文数据结构


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

    systemHeadPic = 0
    level = 0
    customFaceSize = 0
    customStyleSize = 0
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
            logger.error('来自%s的报文不正确，报文内容%s' % (self.ip, self.data.decode(IPMSG.ENCODETYPE)))
            return False
        self.version = arrBytes[0].decode(IPMSG.ENCODETYPE)

        arrVersion = self.version.split('#')

        arrTmp = arrVersion[0].split('_');
        self.systemHeadPic = int(arrTmp[2]) + 166;  # 编号从166开始
        self.level = int(arrVersion[1], 16)
        self.mac = arrVersion[2]
        self.customFaceSize = int(arrVersion[3]);
        self.customStyleSize = int(arrVersion[4]);

        self.packno = int(arrBytes[1])

        self.loginname = arrBytes[2].decode(IPMSG.ENCODETYPE)

        self.hostname = arrBytes[3].decode(IPMSG.ENCODETYPE)

        self.cmd = int(arrBytes[4].decode(IPMSG.ENCODETYPE))

        if len(arrBytes) > 5:
            tmpExtra = IPMSG.PACKET_SEP.join(arrBytes[5:])
            # lastIndex = tmpExtra.rfind(b'\0')
            # if lastIndex != -1:
            #     self.extra = tmpExtra[:lastIndex]
            # else:
            #     self.extra = tmpExtra
            self.extra = tmpExtra
        return True
    def save(self):
        self.data = IPMSG.PACKET_SEP.join([
            self.version.encode(IPMSG.ENCODETYPE),
            str(self.packno).encode(IPMSG.ENCODETYPE),
            self.loginname.encode(IPMSG.ENCODETYPE),
            self.hostname.encode(IPMSG.ENCODETYPE),
            str(self.cmd).encode(IPMSG.ENCODETYPE),
            self.extra + b'\0'#最后一位必须为0
        ])