from LogHelp import logger
import IPMSG
from feiqstruct import *
from TaskManager import *
from UserManager import FeiQUserManager
from SecurityManager import SecurtInstance
import setting

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

    # 需要内容
    def getExtra(self):
        return self.packet.nickname.encode(IPMSG.ENCODETYPE) + b'\0' + \
               self.packet.groupname.encode(IPMSG.ENCODETYPE) + b'\0'





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


class DebugHandler(RecvHandler):
    def handle(self,msg:Message):
        logger.debug("DebugHandler::%s--->%d--->%s"%(msg.friend.__str__(), msg.cmd, msg.extra.decode(IPMSG.ENCODETYPE)))
        return False

class FilterRecvHandler(RecvHandler):
    def handle(self,msg:Message):
        if msg.friend.ip == setting.IPADDRESS and msg.friend.port == setting.PORT:
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

            self.updateUser(msg.friend)

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
            self.updateUser(msg.friend)

            logger.debug('飞秋的119协议:' + msg.friend.__str__())
            return True

        return False

#收到用户发送的分组的数据，需要回应,6291457
class GroupRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_BR_ENTRY) and \
                IPMSG.IS_OPT_SET(msg.cmd, IPMSG.FEIQ_EXTEND_CMD):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            arrData = strExtra.split('\0')
            if len(arrData) >= 2:
                msg.friend.nickname = arrData[0]
                msg.friend.groupname = arrData[1]
            elif len(arrData) >= 1:
                msg.friend.nickname = arrData[0]

            #回应消息
            sender = GroupSender(IPMSG.IPMSG_ANSENTRY|IPMSG.FEIQ_EXTEND_CMD)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
            self.updateUser(msg.friend)
            logger.debug('飞秋的分组信息:%s'%(msg.friend,))
            return True

        return False
#收到用户分组的数据，不需要回应,6291459
class Group2RecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_ANSENTRY) and \
                IPMSG.IS_OPT_SET(msg.cmd, IPMSG.FEIQ_EXTEND_CMD):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            arrData = strExtra.split('\0')
            if len(arrData) >= 2:
                msg.friend.nickname = arrData[0]
                msg.friend.groupname = arrData[1]
            elif len(arrData) >= 1:
                msg.friend.nickname = arrData[0]

            #回应消息
            #sender = GroupSender(IPMSG.IPMSG_ANSENTRY|IPMSG.FEIQ_EXTEND_CMD)
            #self.sendSender(sender, msg.friend.ip, msg.friend.port)
            #self.updateUser(msg.friend)
            logger.debug('飞秋的分组信息:%s'%(msg.friend,))
            return True

        return False
#好友上线
class BrEntryRecvHandler(RecvHandler):
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
            self.updateUser(msg.friend)
            logger.debug('好友上线:' + msg.friend.__str__())
            return True

        return False

#好友下线
class BrExitRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_BR_EXIT):

            self.removeUser(msg.friend)
            logger.debug('好友下线:' + msg.friend.__str__())
            return True

        return False

#有时候用户直接发送消息，不会发上线通知，所以先把接收到的用户都放到用户处理里面
class PacketRecvHandler(RecvHandler):
    def handle(self,msg:Message):
        self.updateUser(msg.friend)
        return False

#IPMSG_SENDCHECKOPT
class CheckOptRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_OPT_SET(msg.cmd, IPMSG.IPMSG_SENDCHECKOPT):
            # 回应消息
            sender = ResponseSender(IPMSG.IPMSG_RECVMSG, msg.packno)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
        return False

#IPMSG_RECVMSG,对方告知我方已经收到报文
class ReportPacketRecvHandler(RecvHandler):
    def handle(self,msg:Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_RECVMSG):
            packno = str(msg.extra.decode())
            self.engine.EraseReleateTask(packno)

        return False


#我方发送请求RSAKEY
class ReqRsaSender(MsgSender):
    def __init__(self):
        MsgSender.__init__(self)
        self.cmd = IPMSG.IPMSG_GETPUBKEY

    # 纯命令的情况，不需要内容
    def getExtra(self):
        return b'21003'

#我方发送RSAKEY
class RepRsaSender(MsgSender):
    def __init__(self):
        MsgSender.__init__(self)
        self.cmd = IPMSG.IPMSG_ANSPUBKEY

    # 纯命令的情况，不需要内容
    def getExtra(self):
        slice1 = b'21003:'
        key = SecurtInstance.getPubKey()
        slice2 = hex(key[0])[2:].encode(IPMSG.ENCODETYPE) #e
        slice3 = b'-'
        slice4 = hex(key[1])[2:].encode(IPMSG.ENCODETYPE)

        return slice1 + slice2 + slice3 + slice4

#对方请求RSA pubkey
class ReqRsaRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_GETPUBKEY):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            if strExtra.startswith('21003'):
                # 回应消息
                sender = RepRsaSender()
                self.sendSender(sender, msg.friend.ip, msg.friend.port)
            logger.debug('对方请求RSA PUBLIC KEY:' + msg.friend.__str__())
            return True

        return False

#对方发送RSA pubkey
class RepRsaRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_ANSPUBKEY):
            strExtra = msg.extra.decode(IPMSG.ENCODETYPE)
            if strExtra.startswith('21003:'):
                strE,strN = strExtra[6:].split('-')
                intE = int(strE, 16)
                intN = int(strN, 16)
                SecurtInstance.addPubKey(msg.friend.getId(), intE, intN)

                #对方发送密钥后需要通知任务队里的任务,设置用户ID类任务全部执行
                self.engine.SetReleateTaskRun('PUBKEY_' + msg.friend.getId())

            logger.debug('对方发送RSA PUBLIC KEY:' + msg.friend.__str__())
            return True

        return False

#接收文本内容
class TextRecvHandler(RecvHandler):
    def handle(self, msg:Message):
        if not IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_SENDMSG):
            return False

        if IPMSG.IS_OPT_SET(msg.cmd, IPMSG.IPMSG_ENCRYPTOPT):
            return False

        strExtra = msg.extra.decode(IPMSG.ENCODETYPE)

        try:
            begin = strExtra.index('{')
            end = strExtra.index('}')
            text = strExtra[:begin]
            format = strExtra[begin+1: end]
        except ValueError:
            text = strExtra[:-1]
            format = ''

        content = TextContent(text, format, msg.friend.getId(), False)
        msg.contents.append(content)

        #测试代码
        #self.engine.appendContent(content)

        return False

#接收加密文本
class EncryptTextRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if not IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_SENDMSG):
            return False

        if not IPMSG.IS_OPT_SET(msg.cmd, IPMSG.IPMSG_ENCRYPTOPT):
            return False

        encryptData = msg.extra.decode(IPMSG.ENCODETYPE)
        try:
            found = encryptData.index('\0')
            encryptData = encryptData[:found]
        except:
            pass
        # 加密数据分三段，
        # 第一段为20002，
        # 第二段为通过RAS加密的内容，
        # 第三段通过第二段解密内容作为key进行解密
        arrSplit = encryptData.split(':')
        if len(arrSplit)< 3 or arrSplit[0] != "20002":
            return False

        decryptData = SecurtInstance.decrypt(bytes.fromhex(arrSplit[1]), bytes.fromhex(arrSplit[2]))

        strExtra = decryptData.decode(IPMSG.ENCODETYPE)
        try:
            found = strExtra.index('\0')
            strExtra = strExtra[:found]
        except:
            pass

        try:
            begin = strExtra.rindex('{')
            end = strExtra.rindex('}')
            text = strExtra[:begin]
            format = strExtra[begin + 1 : end]
        except ValueError:
            text = strExtra[:-1]
            format = ''

        content = TextContent(text, format, msg.friend.getId(), False)
        msg.contents.append(content)

        # 测试代码
        #self.engine.appendContent(content)

        return False

#发送文本内容
class TextSender(MsgSender):
    def __init__(self, content):
        self.content:TextContent = content
        MsgSender.__init__(self)
        self.cmd = IPMSG.IPMSG_SENDMSG | IPMSG.IPMSG_SENDCHECKOPT

    def getExtra(self):
        rawData = self.content.text
        if len(self.content.format) > 0:
            rawData += '{' + self.content.format + '}'

        rawData += '\0'

        return rawData.encode(IPMSG.ENCODETYPE)

#发送加密文本
class EncryptTxtSender(MsgSender):
    def __init__(self, content):
        self.content:TextContent = content
        MsgSender.__init__(self)
        self.cmd = IPMSG.IPMSG_SENDMSG | IPMSG.IPMSG_SENDCHECKOPT | IPMSG.IPMSG_ENCRYPTOPT

    def getExtra(self):
        rawData = self.content.text
        if len(self.content.format) > 0:
            rawData += '{' + self.content.format + '}'
        rawData += '\0'

        enKey, enMsg = SecurtInstance.encrypt(self.content.peer, rawData.encode(IPMSG.ENCODETYPE))

        resultData = '20002:'+enKey.hex() + ':' + enMsg.hex() + '\0'

        return resultData.encode(IPMSG.ENCODETYPE)


#内容接收结束处理器
class EndRecvHandler(RecvHandler):
    def handle(self, msg:Message):
        for item in msg.contents:
            logger.debug('内容接收结束处理器---->%s'% item)
            self.engine.onRecvContent(item)

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
        self.__recvHandler.append(FilterRecvHandler())

        self.__recvHandler.append(DebugHandler())

        self.__recvHandler.append(PacketRecvHandler()) #只有收到对方的报文，就把对方加为好友

        self.__recvHandler.append(ReportPacketRecvHandler()) #对方告知已经收到报文

        self.__recvHandler.append(CheckOptRecvHandler())

        self.__recvHandler.append(GroupRecvHandler())
        self.__recvHandler.append(Group2RecvHandler())

        self.__recvHandler.append(AnsEntryRecvHandler())

        self.__recvHandler.append(FeiQRecvAnsEntry())

        self.__recvHandler.append(BrEntryRecvHandler())

        self.__recvHandler.append(BrExitRecvHandler())

        self.__recvHandler.append(ReqRsaRecvHandler())

        self.__recvHandler.append(RepRsaRecvHandler())

        self.__recvHandler.append(TextRecvHandler())

        self.__recvHandler.append(EncryptTextRecvHandler())

        self.__recvHandler.append(EndRecvHandler())

        for handle in self.__recvHandler:
            handle.setEngine(self)

    def onLogin(self):
        for ip, port in setting.INITADDRESS:
            noop = CommandSender(IPMSG.IPMSG_NOOPERATION)
            self.putSendMessage(noop, ip, port)

            entry = CommandSender(IPMSG.IPMSG_BR_ENTRY)
            self.putSendMessage(entry, ip, port)

            group = GroupSender(IPMSG.IPMSG_BR_ENTRY|IPMSG.FEIQ_EXTEND_CMD)
            self.putSendMessage(group, ip, port)

            group2 = GroupSender(IPMSG.IPMSG_ANSENTRY | IPMSG.FEIQ_EXTEND_CMD)
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
    def putSendMessage(self,sender:MsgSender, ip, port, iDelayMillsecond = 0, taskname='',taskkey=''):
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
            sender = EncryptTxtSender(content)
        else:
            sender = TextSender(content)

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
            rsaSender = ReqRsaSender()
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
            packet.dump() #初步解析数据
            msg=Message()
            msg.friend = User(packet)
            msg.cmd = packet.cmd
            msg.extra = packet.extra
            msg.packno = packet.packno

            for handler in self.__recvHandler:
                if handler.handle(msg):
                    break

            logger.debug('数据报文%d处理完成'%msg.packno)
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