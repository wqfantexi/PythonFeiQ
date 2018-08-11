from FeiQ.Struct import IPMSG
from FeiQ.Struct.Message import Message
from FeiQ.Handle.GroupSender import GroupSender
from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Util.LogHelp import logger

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
            sender = GroupSender(IPMSG.IPMSG_ANSENTRY | IPMSG.FEIQ_EXTEND_CMD)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
            self.updateUser(msg.friend)
            logger.debug('飞秋的分组信息:%s'%(msg.friend,))
            return True

        return False