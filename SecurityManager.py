from LogHelp import logger
import rsa
import IPMSG
import time

class RsaKey:
    def __init__(self,id,e,n):
        self.id=id
        self.key = rsa.PublicKey(n, e)
        self.time = time.time()


class Security:
    def __init__(self):
        self.pubKey,self.priKey = rsa.newkeys(1024)
        self.dictKey = dict()

    def getPubKey(self):
        # return IPMSG.PACKET_SEP.join(str(self.pubKey.e).encode(IPMSG.ENCODETYPE),
        #                             str(self.pubKey.n).encode(encoding=IPMSG.ENCODETYPE))
        return (self.pubKey.e, self.pubKey.n)

    def addPubKey(self,id,e,n):
        self.dictKey[id] = RsaKey(id,e,n)


    def hsaKey(self,id):
        #这里需要判断刷新时间
        return id in self.dictKey


    def encrypt(self,id, msg):
        pass

    def decrypt(self,msg):
        pass