from FeiQ.Struct.Message import Message
from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Config import setting

#过滤掉本地发送的报文
class FilterRecvHandler(RecvHandler):
    def handle(self,msg:Message):
        if msg.friend.ip == setting.IPADDRESS and msg.friend.port == setting.PORT:
            return True