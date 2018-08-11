from FeiQ.Struct import IPMSG
from FeiQ.Struct.Message import Message
from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Util import Util
#IPMSG_RECVMSG,对方告知我方已经收到报文
class ReportPacketRecvHandler(RecvHandler):
    def handle(self,msg:Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_RECVMSG):
            packno = Util.RemoveLastZero(msg.extra).decode(IPMSG.ENCODETYPE)

            self.engine.EraseReleateTask(packno)

        return False