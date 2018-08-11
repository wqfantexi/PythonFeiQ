from FeiQ.Config import setting
from FeiQ.Struct.UdpPacketData import UdpPacketData

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

    systemHeadPic = 0
    level = 0
    customFaceSize = 0
    customStyleSize = 0

    state = setting.FRIEND_ONLINE

    lstContents = None #聊天记录

    def __init__(self, packet: UdpPacketData = None):
        if packet is None:
            return
        self.ip = packet.ip
        self.port = packet.port
        self.mac = packet.mac
        self.loginname = packet.loginname
        self.hostname = packet.hostname
        self.groupname = packet.groupname
        self.nickname = packet.nickname
        self.lstContents = []

        self.systemHeadPic = packet.systemHeadPic
        self.level = packet.level
        self.customFaceSize = packet.customFaceSize
        self.customStyleSize = packet.customStyleSize

        # 系统内置的头像ID
        self.headpic = 'static\\headpic\\BITMAP_' + str(self.systemHeadPic) + '.bmp'

    def saveToPacket(self, packet: UdpPacketData):
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

    # 更新用户数据,最后会返回数据是否更新
    def Update(self, user):
        update = False
        if user.version != self.version and len(user.version) > 0:
            self.version = user.version;
            update = True;

        if user.loginname != self.loginname and len(user.loginname) > 0:
            self.loginname = user.loginname;
            update = True;

        if user.hostname != self.hostname and len(user.hostname) > 0:
            self.hostname = user.hostname;
            update = True

        if user.nickname != self.nickname and len(user.nickname) > 0:
            self.nickname = user.nickname;
            update = True

        if user.groupname != self.groupname and len(user.groupname) and user.groupname != "未知":
            self.groupname = user.groupname;
            update = True

        if user.customStyleSize != self.customStyleSize:
            self.customStyleSize = user.customStyleSize

        if user.customFaceSize != self.customFaceSize:
            self.customFaceSize = user.customFaceSize

        if user.systemHeadPic != self.systemHeadPic:
            self.systemHeadPic = user.systemHeadPic;
            if self.customFaceSize == 0:
                # 系统内置的头像ID
                self.headpic = 'static\\headpic\\BITMAP_' + str(self.systemHeadPic) + '.bmp'
                update = True

        if user.level != self.level:
            self.level = user.level;
            update = True;

        return update;
