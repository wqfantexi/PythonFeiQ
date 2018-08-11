from FeiQ.Struct.IPMSG import ENCODETYPE
from FeiQ.Util.LogHelp import logger


# 图像分片数据
class BmpSlice:
    def __init__(self):
        self.key = ''  # 文件名
        self.totalLen = 0  # 总数据长度
        self.offset = 0  # 当前片偏移
        self.totalSlice = 0  # 总分片数
        self.slice = 0  # 当前分片，从1开始
        self.length = 0  # 当前分片数据长度

        self.opt1 = 0  # 扩展，不清楚含义
        self.opt2 = 1  # 扩展，不清楚含义
        self.opt3 = 0  # 扩展，不清楚含义
        self.data = bytes()  # 报文数据

    # 从字节流中加载数据
    def load(self, data: bytes):
        pos = data.index(b'\0')
        self.data = data[pos + 1:]
        header = data[:pos]
        arrInfo = header.decode(ENCODETYPE).split('|')
        self.key = arrInfo[0]
        self.totalLen = int(arrInfo[1])
        self.offset = int(arrInfo[2])
        self.totalSlice = int(arrInfo[3])
        self.slice = int(arrInfo[4])
        self.length = int(arrInfo[5])
        self.opt1 = int(arrInfo[6])
        self.opt2 = int(arrInfo[7])
        self.opt3 = int(arrInfo[8])

        tmplen = len(self.data)
        if self.length != len(self.data):
            logger.error('BMP slice:%d 长度不匹配,头部:%d 实际:%d' % (self.slice, self.length, tmplen))
            return False

        return True

    # 将数据存储到字符串中
    def save(self):
        result = '|'.join(self.key,
                          str(self.totalLen),
                          str(self.offset),
                          str(self.totalSlice),
                          str(self.slice),
                          str(self.length),
                          str(self.opt1),
                          str(self.opt2),
                          str(self.opt3),
                          '00000000#') + '\0' + self.data

        return result
