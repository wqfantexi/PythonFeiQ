from LogHelp import logger
from feiqstruct import *

OPE_ADD = 0
OPE_MOD = 1
OPE_DEL = 2

VIEW_UNKNOWN = 0
VIEW_USER = 1
VIEW_CONTENT = 2

class View:
    def __init__(self):
        pass

    def type(self):
        return VIEW_UNKNOWN

class UserView(View):
    def __init__(self, user):
        self.user = user
        View.__init__(self)

    def type(self):
        return VIEW_USER

class ContentView(View):
    def __init__(self, content):
        self.content = content
        View.__init__(self)

    def type(self):
        return VIEW_CONTENT

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
        else:
            find.update(user)
        self.reportUser(user)

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