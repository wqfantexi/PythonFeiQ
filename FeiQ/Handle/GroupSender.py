from .MsgSender import MsgSender
from FeiQ.Struct import IPMSG


# 发送分组数据
class GroupSender(MsgSender):
    def __init__(self, cmd):
        MsgSender.__init__(self)
        self.cmd = cmd

    # 需要内容
    def getExtra(self):
        return self.packet.nickname.encode(IPMSG.ENCODETYPE) + b'\0' + \
               self.packet.groupname.encode(IPMSG.ENCODETYPE) + b'\0'