from .MsgSender import MsgSender
from FeiQ.Struct import IPMSG


# 通知对方已经收到了分片数据
class ResponseBmpRecvSender(MsgSender):
    def __init__(self, key, slice):
        MsgSender.__init__(self)
        self.cmd = IPMSG.IPMSG_REPORT_RECVIMAGE
        self.key = key
        self.slice = slice

    # 纯命令的情况，不需要内容
    def getExtra(self):
        return (self.key + '|' + str(self.slice) + '#').encode(IPMSG.ENCODETYPE)
