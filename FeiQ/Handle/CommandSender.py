from FeiQ.Handle.MsgSender import MsgSender
#命令发送，没有内容
class CommandSender(MsgSender):
    def __init__(self, cmd):
        MsgSender.__init__(self)
        self.cmd = cmd

    #纯命令的情况，不需要内容
    def getExtra(self):
        return b'\0'