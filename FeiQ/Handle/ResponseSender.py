from .MsgSender import MsgSender
import FeiQ.Struct.IPMSG as IPMSG


# 命令发送,回应收到报文
class ResponseSender(MsgSender):
    def __init__(self, cmd, packetno):
        MsgSender.__init__(self)
        self.cmd = cmd
        self.packetno = packetno

    # 纯命令的情况，不需要内容
    def getExtra(self):
        return str(self.packetno).encode(IPMSG.ENCODETYPE) + b'\0'