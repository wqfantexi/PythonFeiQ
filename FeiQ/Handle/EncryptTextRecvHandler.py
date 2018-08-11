from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Struct.Message import Message
from FeiQ.Struct.TextContent import TextContent
from FeiQ.Struct import IPMSG
from FeiQ.Handle.Security.SecurityManager import SecurtInstance


#接收加密文本
class EncryptTextRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if not IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_SENDMSG):
            return False

        if not IPMSG.IS_OPT_SET(msg.cmd, IPMSG.IPMSG_ENCRYPTOPT):
            return False

        encryptData = msg.extra.decode(IPMSG.ENCODETYPE)
        try:
            found = encryptData.index('\0')
            encryptData = encryptData[:found]
        except:
            pass
        # 加密数据分三段，
        # 第一段为20002，
        # 第二段为通过RAS加密的内容，
        # 第三段通过第二段解密内容作为key进行解密
        arrSplit = encryptData.split(':')
        if len(arrSplit)< 3 or arrSplit[0] != "20002":
            return False

        decryptData = SecurtInstance.decrypt(bytes.fromhex(arrSplit[1]), bytes.fromhex(arrSplit[2]))

        strExtra = decryptData.decode(IPMSG.ENCODETYPE)
        try:
            found = strExtra.index('\0')
            strExtra = strExtra[:found]
        except:
            pass

        try:
            begin = strExtra.rindex('{')
            end = strExtra.rindex('}')
            text = strExtra[:begin]
            format = strExtra[begin + 1 : end]
        except ValueError:
            text = strExtra[:-1]
            format = ''

        content = TextContent(text, format, msg.friend.getId(), False)
        msg.contents.append(content)

        # 测试代码
        #self.engine.appendContent(content)

        return False
