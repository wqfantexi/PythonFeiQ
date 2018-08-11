from FeiQ.Handle.RecvHandler import RecvHandler
from FeiQ.Struct.Message import Message
from FeiQ.Struct import IPMSG
from FeiQ.Struct.BmpSlice import BmpSlice
from FeiQ.Handle.ResponseBmpRecvSender import ResponseBmpRecvSender
from FeiQ.SliceManager import SliceManagerInstance as SMI
from FeiQ.Algorithm.Lzw import ImgLzw
from FeiQ.Config.setting import RECV_IMAGE_PATH
from FeiQ.Util.LogHelp import logger


# 接收图像分片数据
class BmpRecvHandler(RecvHandler):
    def handle(self, msg: Message):
        if not IPMSG.IS_CMD_SET(msg.cmd, IPMSG.IPMSG_SENDIMAGE):
            return False

        if not IPMSG.IS_OPT_SET(msg.cmd, IPMSG.IPMSG_FILEATTACHOPT):
            return False

        rawData = msg.extra

        bs = BmpSlice()
        # 如果解析成功
        if bs.load(rawData):
            # 回应消息
            sender = ResponseBmpRecvSender(bs.key, bs.slice)
            self.sendSender(sender, msg.friend.ip, msg.friend.port)
            logger.debug('接收到分片报文:%s  %d : %d' % (bs.key, bs.slice, bs.totalSlice))
            # 清除任务队列中的重传请求,用key_slice作为关键字
            self.engine.EraseReleateTask(bs.key + '_' + str(bs.slice))

            SMI.append(bs)

            # 设置报文重传请求
            if SMI.count(bs.key) == 1 and bs.totalSlice != 1:
                # TODO 这里设置报文重传请求
                pass

            # 如果容器中存储的数据还不满，那么不需要后续处理了
            if SMI.count(bs.key) != bs.totalSlice:
                return True

            bmpData = SMI.getData(bs.key)
            if len(bmpData) == 0:
                return True

            lw = ImgLzw()
            lw.decodeImage(bmpData, RECV_IMAGE_PATH + bs.key)

            return True

        logger.error('加载bmp分片报文失败')
        # 如果解析失败，后续不需要再解析了
        return True
