from FeiQ.Struct import IPMSG
from FeiQ.Struct.Message import Message
from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Handle.Security.SecurityManager import SecurtInstance
from FeiQ.Util.LogHelp import logger
from FeiQ.Util import Util
#对方发送RSA pubkey
class RepRsaRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_ANSPUBKEY):
            strExtra = Util.RemoveLastZero(msg.extra).decode(IPMSG.ENCODETYPE)

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