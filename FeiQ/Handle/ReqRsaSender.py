from FeiQ.Struct import IPMSG
from FeiQ.Handle.MsgSender import MsgSender

#我方发送请求RSAKEY
class ReqRsaSender(MsgSender):
    def __init__(self):
        MsgSender.__init__(self)
        self.cmd = IPMSG.IPMSG_GETPUBKEY

    # 纯命令的情况，不需要内容
    def getExtra(self):
        return b'21003'