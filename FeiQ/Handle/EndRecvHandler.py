from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Struct.Message import Message
from FeiQ.Util.LogHelp import logger

#内容接收结束处理器
class EndRecvHandler(RecvHandler):
    def handle(self, msg:Message):
        for item in msg.contents:
            logger.debug('内容接收结束处理器---->%s'% item)
            self.engine.onRecvContent(item)
        
        return True