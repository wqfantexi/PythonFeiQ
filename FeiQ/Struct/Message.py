from FeiQ.Struct.User import User

#用户发来的数据报文
class Message:
    def __init__(self):
        self.friend = User()
        self.cmd = 0 #命令ID
        self.extra = b'' #数据内容
        self.packno = 0 #当前数据包的报文号
        self.contents=[] #内部存储PacketContent