from FeiQ.Struct.Message import Message
from FeiQ.Struct.PacketContent import PacketContent, ContentType
from FeiQ.Struct.User import User
from FeiQ.Struct.UdpPacketData import UdpPacketData
from FeiQ.Struct import IPMSG
from FeiQ.TaskManager import *
from FeiQ.UserManager import FeiQUserManager
from FeiQ.Handle.Security.SecurityManager import SecurtInstance
from FeiQ.Config import setting
from FeiQ import Handle

#此类主要处理数据，不负责收发消息
class MainWorkThread(TaskManager):
    me:User = User()

    __recvHandler = [

    ]

    def __init__(self):
        self.me.version = setting.VERSION
        self.me.hostname = setting.HOSTNAME
        self.me.loginname = setting.LOGINNAME
        self.me.nickname = setting.NICKNAME
        self.me.groupname = setting.GROUPNAME

        TaskManager.__init__(self, 5, 50)

        self.initRecvHandler()

        self.sendFunc=None

    #设置内容结束回调函数
    #def setRecvContentCB(self, contentRecvHandler):
    #    self.contentRecvHandler = contentRecvHandler

    #初始化接收处理器
    def initRecvHandler(self):
        #过滤器放最前面
        self.__recvHandler.append(Handle.FilterRecvHandler())

        self.__recvHandler.append(Handle.DebugHandler())

        self.__recvHandler.append(Handle.PacketRecvHandler()) #只有收到对方的报文，就把对方加为好友

        self.__recvHandler.append(Handle.ReportPacketRecvHandler()) #对方告知已经收到报文

        self.__recvHandler.append(Handle.CheckOptRecvHandler())

        self.__recvHandler.append(Handle.GroupRecvHandler())
        self.__recvHandler.append(Handle.Group2RecvHandler())

        self.__recvHandler.append(Handle.AnsEntryRecvHandler())

        self.__recvHandler.append(Handle.FeiQRecvAnsEntry())

        self.__recvHandler.append(Handle.BrEntryRecvHandler())

        self.__recvHandler.append(Handle.BrExitRecvHandler())

        self.__recvHandler.append(Handle.ReqRsaRecvHandler())

        self.__recvHandler.append(Handle.RepRsaRecvHandler())

        self.__recvHandler.append(Handle.TextRecvHandler())

        self.__recvHandler.append(Handle.BmpRecvHandler())

        self.__recvHandler.append(Handle.EncryptTextRecvHandler())

        self.__recvHandler.append(Handle.EndRecvHandler())

        for handle in self.__recvHandler:
            handle.setEngine(self)

    def onLogin(self):
        for ip, port in setting.INITADDRESS:
            noop = Handle.CommandSender(IPMSG.IPMSG_NOOPERATION)
            self.putSendMessage(noop, ip, port)

            entry = Handle.CommandSender(IPMSG.IPMSG_BR_ENTRY)
            self.putSendMessage(entry, ip, port)

            group = Handle.GroupSender(IPMSG.IPMSG_BR_ENTRY | IPMSG.FEIQ_EXTEND_CMD)
            self.putSendMessage(group, ip, port)

            group2 = Handle.GroupSender(IPMSG.IPMSG_ANSENTRY | IPMSG.FEIQ_EXTEND_CMD)
            self.putSendMessage(group, ip, port)
    #启动
    def start(self,sendfunc, onViewCallback):
        self.sendFunc=sendfunc
        self.usermanager = FeiQUserManager(self.appendContent)
        self.usermanager.setViewEvent(onViewCallback)
        self.onLogin()  # 登录上线

    #停止
    def stopAll(self):
        TaskManager.Stop(self)

    #把接收到的数据包放进去
    def onRecvContent(self,content):
        self.usermanager.AddContent(content)

    #由UDPserver负责把数据放入
    def putRecvMessage(self,packet:UdpPacketData):
        self.CreateImmediatelyTask(self.__func_recv(packet), '接收报文处理')

    #发送数据,属于直接发送，特殊处理不能使用这个函数
    def putSendMessage(self,sender:Handle.MsgSender, ip, port, iDelayMillsecond = 0, taskname='',taskkey=''):
        sender.setData(self.me, ip, port)
        self.CreateDelayTask(self.__func_send(sender), iDelayMillsecond, taskname, taskkey)

    #发送数据报文
    def appendContent(self, content:PacketContent):
        if content.type == ContentType.TEXT:
            # 先使用加密发送
            self.sendTextContent(content, True)
        elif content.type == ContentType.KNOCK:
            self.sendTextContent()

    #发送超时消息
    def onPacketTimeout(self, content):
        logger.error('发送报文超时---->%s'%content)

    #发送文本内容
    def sendTextContent(self, content:PacketContent, useEncrypt = True):
        addr = self.usermanager.getAddr(content.peer)
        if addr is None:
            logger.error('发送任务失败，无法获取需要发送的地址:%s'%content.peer)
            return
        if useEncrypt:
            sender = Handle.EncryptTxtSender(content)
        else:
            sender = Handle.TextSender(content)

        sender.setData(self.me, addr[0], addr[1])

        # 超时后发送消息
        def sendTimeout():
            self.onPacketTimeout(content)

        #发送数据
        def send():
            #批量发送文本
            self.BatchCreateDelayTask(self.__func_send(sender), str(sender.packet.packno), '批量发送文本', 0, 1000, 4)

            #准备到期超时消息,5000ms后超时
            self.CreateDelayTask(sendTimeout, 5000, '消息超时', str(sender.packet.packno))


        if not useEncrypt or SecurtInstance.hsaKey(content.peer):
            send()
        else:
            rsaSender = Handle.ReqRsaSender()
            rsaSender.setData(self.me, addr[0], addr[1])
            self.CreateImmediatelyTask(self.__func_send(rsaSender), "请求RAS PUBKEY", 'PUBKEY_' + content.peer)

            self.CreateSwitchTask(send, sendTimeout, 'PUBKEY_' + content.peer, 5000, '请求密钥后发送消息任务')
    #发送弹窗
    def sendKnock(self):
        pass
    def __socketSend(self,addr,message:bytes):
        if self.sendFunc is not None:
            self.sendFunc(message, addr)

    #获取处理接收报文的函数
    def __func_recv(self, packet):
        def func():
            if not packet.dump():  # 初步解析数据
                return
            msg=Message()
            msg.friend = User(packet)
            msg.cmd = packet.cmd
            msg.extra = packet.extra
            msg.packno = packet.packno

            for handler in self.__recvHandler:
                if handler.handle(msg):
                    break

            # logger.debug('数据报文%d处理完成'%msg.packno)
        return func

    #获取处理发送报文的函数
    def __func_send(self, sender:Handle.MsgSender):
        def func():
            #logger.debug('开始处理一个发送数据报文')
            sender.save() #封装数据

            addr = (sender.packet.ip, sender.packet.port)
            self.__socketSend(addr, sender.packet.data)
        return func



Instance = MainWorkThread()