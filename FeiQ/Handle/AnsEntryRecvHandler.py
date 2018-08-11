from FeiQ.Util.LogHelp import logger
from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Struct import IPMSG
from FeiQ.Handle.CommandSender import CommandSender
from FeiQ.Struct.Message import Message


#好友响应我们的上线消息
class AnsEntryRecvHandler(RecvHandler):
    def handle(self,msg:Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_ANSENTRY):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            arrData = strExtra.split('\0')
            if len(arrData) > 2:
                msg.friend.nickname = arrData[0]
                msg.friend.groupname = arrData[1]

            # 回应消息
            sender = CommandSender(IPMSG.IPMSG_OPEN_YOU)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)

            self.updateUser(msg.friend)

            logger.debug('好友回应上线:' + msg.friend.__str__())
            return True

        return False