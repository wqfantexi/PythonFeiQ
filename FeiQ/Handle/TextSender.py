from FeiQ.Struct import IPMSG
from FeiQ.Struct.TextContent import TextContent
from FeiQ.Handle.MsgSender import MsgSender

#发送文本内容
class TextSender(MsgSender):
    def __init__(self, content):
        self.content:TextContent = content
        MsgSender.__init__(self)
        self.cmd = IPMSG.IPMSG_SENDMSG | IPMSG.IPMSG_SENDCHECKOPT

    def getExtra(self):
        rawData = self.content.text
        if len(self.content.format) > 0:
            rawData += '{' + self.content.format + '}'

        rawData += '\0'

        return rawData.encode(IPMSG.ENCODETYPE)