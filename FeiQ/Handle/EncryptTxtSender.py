from FeiQ.Handle.MsgSender import MsgSender
from FeiQ.Struct.TextContent import TextContent
from FeiQ.Struct import IPMSG
from FeiQ.Handle.Security.SecurityManager import SecurtInstance

#发送加密文本
class EncryptTxtSender(MsgSender):
    def __init__(self, content):
        self.content:TextContent = content
        MsgSender.__init__(self)
        self.cmd = IPMSG.IPMSG_SENDMSG | IPMSG.IPMSG_SENDCHECKOPT | IPMSG.IPMSG_ENCRYPTOPT

    def getExtra(self):
        rawData = self.content.text
        if len(self.content.format) > 0:
            rawData += '{' + self.content.format + '}'
        rawData += '\0'

        enKey, enMsg = SecurtInstance.encrypt(self.content.peer, rawData.encode(IPMSG.ENCODETYPE))

        resultData = '20002:'+enKey.hex() + ':' + enMsg.hex() + '\0'

        return resultData.encode(IPMSG.ENCODETYPE)