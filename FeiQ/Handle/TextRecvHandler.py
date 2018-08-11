from FeiQ.Struct import IPMSG
from FeiQ.Struct.Message import Message
from FeiQ.Struct.TextContent import TextContent
from FeiQ.Handle.RecvHandler import RecvHandler

#接收文本内容
class TextRecvHandler(RecvHandler):
    def handle(self, msg:Message):
        if not IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_SENDMSG):
            return False

        if IPMSG.IS_OPT_SET(msg.cmd, IPMSG.IPMSG_ENCRYPTOPT):
            return False

        strExtra = msg.extra.decode(IPMSG.ENCODETYPE)

        try:
            begin = strExtra.index('{')
            end = strExtra.index('}')
            text = strExtra[:begin]
            format = strExtra[begin+1: end]
        except ValueError:
            text = strExtra[:-1]
            format = ''

        content = TextContent(text, format, msg.friend.getId(), False)
        msg.contents.append(content)

        #测试代码
        #self.engine.appendContent(content)

        return False