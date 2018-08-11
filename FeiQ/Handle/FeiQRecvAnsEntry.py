from FeiQ.Struct import IPMSG
from FeiQ.Struct.Message import Message
from FeiQ.Handle.CommandSender import CommandSender
from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Util.LogHelp import logger

#飞秋的119协议，上线，回应120
class FeiQRecvAnsEntry(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_OPEN_YOU):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            arrData = strExtra.split('\0')
            if len(arrData) > 2:
                msg.friend.nickname = arrData[0]
                msg.friend.groupname = arrData[1]

            #回应消息
            sender = CommandSender(IPMSG.IPMSG_RESP_YOU)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
            self.updateUser(msg.friend)

            logger.debug('飞秋的119协议:' + msg.friend.__str__())
            return True

        return False