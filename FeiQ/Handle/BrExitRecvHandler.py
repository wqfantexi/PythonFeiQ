from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Struct.Message import Message
from FeiQ.Struct import IPMSG
from FeiQ.Util.LogHelp import logger
#好友下线
class BrExitRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_BR_EXIT):

            self.removeUser(msg.friend)
            logger.debug('好友下线:' + msg.friend.__str__())
            return True

        return False