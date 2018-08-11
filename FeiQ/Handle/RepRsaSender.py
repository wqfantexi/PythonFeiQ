from FeiQ.Struct import IPMSG
from FeiQ.Handle.MsgSender import MsgSender
from FeiQ.Handle.Security.SecurityManager import SecurtInstance

#我方发送RSAKEY
class RepRsaSender(MsgSender):
    def __init__(self):
        MsgSender.__init__(self)
        self.cmd = IPMSG.IPMSG_ANSPUBKEY

    # 纯命令的情况，不需要内容
    def getExtra(self):
        slice1 = b'21003:'
        key = SecurtInstance.getPubKey()
        slice2 = hex(key[0])[2:].encode(IPMSG.ENCODETYPE) #e
        slice3 = b'-'
        slice4 = hex(key[1])[2:].encode(IPMSG.ENCODETYPE)

        return slice1 + slice2 + slice3 + slice4