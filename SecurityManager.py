from LogHelp import logger
import rsa
import IPMSG
import time
from os import urandom
import blowfish

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
        return (self.pubKey.e, self.pubKey.n)

    def addPubKey(self,id,e,n):
        self.dictKey[id] = RsaKey(id,e,n)


    def hsaKey(self,id):
        #这里需要判断刷新时间
        return id in self.dictKey


    def encrypt(self,id, byteMsg):
        if id not in self.dictKey:
            return None

        arKey = urandom(16)
        iv = b'\0\0\0\0\0\0\0\0'
        iByteLen = len(byteMsg)
        ext = iByteLen % 8
        if ext > 0:
            byteMsg += str((8 - ext)).encode()*(8-ext)
        encryptMsg = b''.join(blowfish.Cipher(key=arKey).encrypt_cbc(byteMsg, iv))

        pubKey = self.dictKey[id]
        encryptkey = rsa.encrypt(arKey, pubKey.key)

        return (encryptkey, encryptMsg)

    def decrypt(self,encryptkey, encryptMsg):
        arKey = rsa.decrypt(encryptkey, self.priKey)
        iv = b'\0\0\0\0\0\0\0\0'

        byteMsg = b''.join(blowfish.Cipher(key=arKey).decrypt_cbc(encryptMsg, iv))

        return byteMsg

#单例模式
SecurtInstance = Security()