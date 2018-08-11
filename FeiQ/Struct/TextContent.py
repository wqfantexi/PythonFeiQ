from FeiQ.Struct.PacketContent import PacketContent, ContentType
from FeiQ.Config.setting import RECV_IMAGE_PATH
import glob
import re
# 文本内容
class TextContent(PacketContent):
    def __init__(self, text, format, peer, tx):
        PacketContent.__init__(self, ContentType.TEXT, peer, tx)
        self.text = text
        self.format = format

    def __repr__(self):
        return 'TextContent(text=%s\tformat=%s)'%(self.text,self.format)

    def ReplaceImage(self, matchVaule):
        imagekey:str = matchVaule.group('IMAGE')
        imagepath = RECV_IMAGE_PATH + imagekey + '.jfif'
        lst = glob.glob(RECV_IMAGE_PATH + imagekey+'.')
        if len(lst) > 0:
            imagepath = lst[0]

        return '<img src="%s" />'%(imagepath,)
    # 替换文本中的图片
    def DealBeforeShow(self):
        self.text = re.sub('\/~#>(?P<IMAGE>[0-9a-f]+)<[B]{1}~', self.ReplaceImage, self.text)