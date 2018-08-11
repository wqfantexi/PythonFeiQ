from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Struct.Message import Message
from FeiQ.Struct import IPMSG
from FeiQ.Handle.ResponseSender import ResponseSender

#IPMSG_SENDCHECKOPT
class CheckOptRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_OPT_SET(msg.cmd, IPMSG.IPMSG_SENDCHECKOPT):
            # 回应消息
            sender = ResponseSender(IPMSG.IPMSG_RECVMSG, msg.packno)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
        return False