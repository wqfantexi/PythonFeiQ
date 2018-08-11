from FeiQ.Struct import IPMSG
from FeiQ.Struct.Message import Message
from FeiQ.Handle.RepRsaSender import RepRsaSender
from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Util.LogHelp import logger

#对方请求RSA pubkey
class ReqRsaRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_GETPUBKEY):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            if strExtra.startswith('21003'):
                # 回应消息
                sender = RepRsaSender()
                self.sendSender(sender, msg.friend.ip, msg.friend.port)
            logger.debug('对方请求RSA PUBLIC KEY:' + msg.friend.__str__())
            return True

        return False