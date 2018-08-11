from FeiQ.Struct.Message import Message
from FeiQ.Handle.MsgSender import MsgSender
from FeiQ.Handle.GroupSender import GroupSender
from FeiQ.Struct import IPMSG


#报文处理类
class RecvHandler:
    def __init__(self):
        pass

    def handle(self,msg:Message):
        pass

    # 这是把MainWorkThread的对象传递来，方便回调处理
    def setEngine(self, engine):
        self.engine = engine

    def sendSender(self, sender:MsgSender, ip, port):
        self.engine.putSendMessage(sender, ip, port)

    def updateUser(self, user):
        bAdd = self.engine.usermanager.UpdateUser(user)
        if bAdd: #如果是新增加，那么请求对方的昵称等信息
            sender = GroupSender(IPMSG.IPMSG_ANSENTRY | IPMSG.FEIQ_EXTEND_CMD)
            self.sendSender(sender, user.ip, user.port)


    def removeUser(self, user):
        self.engine.usermanager.RemoveUser(user)