import datetime
from enum import Enum


class ContentType(Enum):
    UNKNOWN = 0
    TEXT = 1
    KNOCK = 2

# 报文内容
class PacketContent:
    def __init__(self, type, peer, bIsSend):
        self.type = type
        self.peer = peer #对端ID
        self.tx = bIsSend
        self.time = datetime.datetime.now()

    def __repr__(self):
        return 'PacketContent(peer=%s)'%(self.peer)

    #在显示前做一些准备工作
    def DealBeforeShow(self):
        pass


