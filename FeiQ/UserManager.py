from FeiQ.Struct.PacketContent import PacketContent
from FeiQ.Struct.User import User
from FeiQ.Config import setting
from FeiQ.View.ContentView import ContentView
from FeiQ.View.UserView import UserView


class FeiQUserManager:
    def __init__(self, onSendContentCB):
        self.UserList = []
        #self.content = dict()
        self.Sendcallback = onSendContentCB
        self.viewEventCallback = None

    def setViewEvent(self, viewCallback):
        self.viewEventCallback = viewCallback

    def getAddr(self, id):
        find = next((x for x in self.UserList if x.getId() == id), None)
        if find is not None:
            return (find.ip,find.port)
        else:
            return None

    def findUser(self,id):
        return next((x for x in self.UserList if x.getId() == id), None)

    #添加或者更新用户
    def UpdateUser(self, user:User):
        find = next((x for x in self.UserList if x.getId() == user.getId()), None)
        if find is None:
            self.UserList.append(user)
            self.reportUser(user)
        else:
            if find.Update(user):
                self.reportUser(find)


    #删除用户
    def RemoveUser(self, user:User):
        find = next((x for x in self.UserList if x.getId() == user.getId()), None)
        if find is not None:
            find.state = setting.FRIEND_OFFLINE
            self.reportUser(find)

    #添加聊天内容
    def AddContent(self, content:PacketContent):
        find:User = self.findUser(content.peer)
        if find is None:
            return

        if content.tx:
            self.Sendcallback(content)
        else:
            self.reportContent(content)

        find.lstContents.append(content)

    #上报用户更新信息
    def reportUser(self,user):
        if self.viewEventCallback is not None:
            view = UserView(user)
            self.viewEventCallback(view)

    #上报消息更新
    def reportContent(self,content):
        if self.viewEventCallback is not None:
            view = ContentView(content)
            self.viewEventCallback(view)