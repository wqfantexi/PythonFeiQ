from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Struct import IPMSG
from FeiQ.Util.LogHelp import logger
from FeiQ.Struct.Message import Message


class DebugHandler(RecvHandler):
    def handle(self,msg:Message):
        return False
        try:
            logger.debug("DebugHandler::%s--->%d--->%s" % (msg.friend.__str__(), msg.cmd, msg.extra.decode(
                IPMSG.ENCODETYPE)))
        except:
            logger.debug("DebugHandler::%s--->%d--->%s" % (msg.friend.__str__(), msg.cmd, msg.extra))

        return False