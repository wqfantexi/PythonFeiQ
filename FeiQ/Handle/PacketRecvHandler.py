from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Struct.Message import Message


#有时候用户直接发送消息，不会发上线通知，所以先把接收到的用户都放到用户处理里面
class PacketRecvHandler(RecvHandler):
    def handle(self,msg:Message):
        self.updateUser(msg.friend)
        return False