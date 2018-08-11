from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Struct.Message import Message
from FeiQ.Struct import IPMSG
from FeiQ.Handle.CommandSender import CommandSender
from FeiQ.Util.LogHelp import logger
#好友上线
class BrEntryRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_BR_ENTRY):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            arrData = strExtra.split(' ')
            if len(arrData) > 2:
                msg.friend.nickname = arrData[0]
                msg.friend.groupname = arrData[1]

            # 回应消息
            sender = CommandSender(IPMSG.IPMSG_ANSENTRY)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
            self.updateUser(msg.friend)
            logger.debug('好友上线:' + msg.friend.__str__())
            return True

        return False