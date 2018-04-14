from LogHelp import logger
from feiqstruct import *

class FeiQUserManager:
    def __init__(self):
        self.UserList = []

    #添加或者更新用户
    def UpdateUser(self, user:User):
        find = next((x for x in self.UserList if x.getId() == user.getId()), None)
        if find is not None:
            self.UserList.append(user)
        else:
            find.update(user)

    #删除用户
    def RemoveUser(self, user:User):
        find = next((x for x in self.UserList if x.getId() == user.getId()), None)
        if find is not None:
            self.UserList.remove(find)
