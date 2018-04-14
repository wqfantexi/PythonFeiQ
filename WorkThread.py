from LogHelp import logger
import IPMSG
from feiqstruct import *
from TaskManager import *
from UserManager import FeiQUserManager



#消息发送类
class MsgSender:
    packet:UdpPacketData = None
    cmd = 0

    def __init__(self):
        self.packet = UdpPacketData()

    def setData(self,me:User,ip,port):
        me.saveToPacket(self.packet)
        self.packet.ip = ip
        self.packet.port = port

    # 序列化数据
    def save(self):
        self.packet.cmd = self.cmd
        self.packet.extra = self.getExtra()

        self.packet.save()

    #子类必须实现
    def getExtra(self):
        pass

#命令发送，没有内容
class CommandSender(MsgSender):
    def __init__(self, cmd):
        MsgSender.__init__(self)
        self.cmd = cmd

    #纯命令的情况，不需要内容
    def getExtra(self):
        return b'\0'


# 命令发送,回应收到报文
class ResponseSender(MsgSender):
    def __init__(self, cmd, packetno):
        MsgSender.__init__(self)
        self.cmd = cmd
        self.packetno = packetno

    # 纯命令的情况，不需要内容
    def getExtra(self):
        return str(self.packetno).encode(IPMSG.ENCODETYPE) + b'\0'

# 发送分组数据
class GroupSender(MsgSender):
    def __init__(self, cmd):
        MsgSender.__init__(self)
        self.cmd = cmd

    # 纯命令的情况，不需要内容
    def getExtra(self):
        return self.packet.nickname.encode(IPMSG.ENCODETYPE) + b'\0' + \
               self.packet.groupname.encode(IPMSG.ENCODETYPE) + b'\0'


#用户发来的数据报文
class Message:
    friend = User()
    cmd = 0 #命令ID
    extra = b'' #数据内容
    contents=[] #内部存储PacketContent


#报文处理类
class RecvHandler:
    def __init__(self):
        pass

    def handle(self,msg:Message):
        pass

    def setSendHandle(self, sendfunc):
        self.sendfunc = sendfunc

    def setUpdateUserHandle(self, updateFunc):
        self.update = updateFunc

    def setRemoveUserHandle(self, removeFunc):
        self.remove = removeFunc

    def sendSender(self, sender:MsgSender, ip, port):
        self.sendfunc(sender, ip, port)

    def updateUser(self, user):
        self.update(user)

    def removeUser(self, user):
        self.remove(user)


class DebugHandler(RecvHandler):
    def handle(self,msg:Message):
        logger.debug("DebugHandler::%s--->%d--->%s"%(msg.friend.__str__(), msg.cmd, msg.extra.decode(IPMSG.ENCODETYPE)))
        return False

class FilterRecvHandler(RecvHandler):
    def handle(self,msg:Message):
        if msg.friend.ip is '10.168.17.149':
            return True

#好友响应我们的上线消息
class AnsEntryRecvHandler(RecvHandler):
    def handle(self,msg:Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_ANSENTRY):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            arrData = strExtra.split('\0')
            if len(arrData) > 2:
                msg.friend.nickname = arrData[0]
                msg.friend.groupname = arrData[1]

            # 回应消息
            sender = CommandSender(IPMSG.IPMSG_OPEN_YOU)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)

            self.update(msg.friend)

            logger.debug('好友回应上线:' + msg.friend.__str__())
            return True

        return False

#飞秋的119协议，上线，回应120
class FeiQRecvAnsEntry(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_OPEN_YOU):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            arrData = strExtra.split('\0')
            if len(arrData) > 2:
                msg.friend.nickname = arrData[0]
                msg.friend.groupname = arrData[1]

            #回应消息
            sender = CommandSender(IPMSG.IPMSG_RESP_YOU)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
            self.update(msg.friend)

            logger.debug('飞秋的119协议:' + msg.friend.__str__())
            return True

        return False

#收到用户分组的数据
class GroupRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_ANSENTRY) and \
                IPMSG.IS_OPT_SET(msg.cmd, IPMSG.FEIQ_EXTEND_CMD):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            arrData = strExtra.split('\0')
            if len(arrData) > 2:
                msg.friend.nickname = arrData[0]
                msg.friend.groupname = arrData[1]

            #回应消息
            sender = GroupSender(IPMSG.IPMSG_ANSENTRY|IPMSG.FEIQ_EXTEND_CMD)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
            self.update(msg.friend)
            logger.debug('飞秋的分组信息:%s'%(msg.friend,))
            return True

        return False

#好友上线
class RecvBrEntry(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_BR_ENTRY):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            arrData = strExtra.split(' ')
            if len(arrData) > 2:
                msg.friend.nickname = arrData[0]
                msg.friend.groupname = arrData[1]

            # 回应消息
            sender = CommandSender(IPMSG.IPMSG_ANSENTRY)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
            self.update(msg.friend)
            logger.debug('好友上线:' + msg.friend.__str__())
            return True

        return False

#好友下线
class RecvBrExit(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_BR_EXIT):

            self.remove(msg.friend)
            logger.debug('好友下线:' + msg.friend.__str__())
            return True

        return False


#此类主要处理数据，不负责收发消息
class MainWorkThread(TaskManager):
    me:User = User()

    __recvHandler = [

    ]

    def __init__(self):
        self.usermanager = FeiQUserManager()
        self.me.version = '1_lbt4_3#128#005056A37E16#0#0#0'
        self.me.hostname = '我的电脑'
        self.me.loginname = 'ohaiyou'

        self.initRecvHandler()

        self.sendFunc=None

        TaskManager.__init__(self, 5, 50)

        self.onLogin() #登录上线

    #初始化接收处理器
    def initRecvHandler(self):
        #过滤器放最前面
        self.__recvHandler.append(FilterRecvHandler())

        self.__recvHandler.append(DebugHandler())

        self.__recvHandler.append(GroupRecvHandler())

        self.__recvHandler.append(AnsEntryRecvHandler())

        self.__recvHandler.append(FeiQRecvAnsEntry())

        self.__recvHandler.append(RecvBrEntry())

        self.__recvHandler.append(RecvBrExit())

        for handle in self.__recvHandler:
            handle.setSendHandle(self.putSendMessage)
            handle.setUpdateUserHandle(self.usermanager.UpdateUser)
            handle.setRemoveUserHandle(self.usermanager.RemoveUser)

    def onLogin(self):
        network='<broadcast>'
        noop = CommandSender(IPMSG.IPMSG_NOOPERATION)
        self.putSendMessage(noop, network, 2425)

        entry = CommandSender(IPMSG.IPMSG_BR_ENTRY)
        self.putSendMessage(entry, network, 2425)

    def startMessage(self,sendfunc):
        self.sendFunc=sendfunc

    #由UDPserver负责把数据放入
    def putRecvMessage(self,packet:UdpPacketData):
        self.CreateImmediatelyTask(self.__func_recv(packet), '接收报文处理')

    #发送数据,属于直接发送，特殊处理不能使用这个函数
    def putSendMessage(self,sender:MsgSender, ip, port, iDelayMillsecond = 0, taskname='',taskkey=''):
        sender.setData(self.me, ip, port)
        self.CreateDelayTask(self.__func_send(sender), iDelayMillsecond, taskname, taskkey)

    def __socketSend(self,addr,message:bytes):
        if self.sendFunc is not None:
            self.sendFunc(message, addr)

    #获取处理接收报文的函数
    def __func_recv(self, packet):
        def func():
        #packet: UdpPacketData=self.recvTask.get()
            logger.debug('开始处理一个数据报文')
            packet.dump() #初步解析数据
            msg=Message()
            msg.friend = User(packet)
            msg.cmd = packet.cmd
            msg.extra = packet.extra

            for handler in self.__recvHandler:
                if handler.handle(msg):
                    break
        return func

    #获取处理发送报文的函数
    def __func_send(self, sender:MsgSender):
        def func():
            logger.debug('开始处理一个发送数据报文')
            sender.save() #封装数据

            addr = (sender.packet.ip, sender.packet.port)
            self.__socketSend(addr, sender.packet.data)
        return func

Instance = MainWorkThread()