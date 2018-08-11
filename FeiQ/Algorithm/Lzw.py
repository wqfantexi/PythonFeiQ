import bitstring
import struct
import binascii
from FeiQ.Util.LogHelp import logger
# 飞秋图片格式
# 头部12字节 4字节（LZW!)|4字节解码后数据长度|4字节CRC解码后数据
# LZW编码后数据

IMAGE_DECODE_OFFSET = 12  # 解码时偏移字节数
IMAGE_ENCODE_OFFSET = 14  # 编码时偏移字节数


# 这个类用来解压、压缩图片的
# 飞秋图片解压方式为：从流中按照9位/10/11/12读取为int，然后把int进行解压，即为原始的数据
class ImgLzw:
    def __init__(self):
        pass

    # 将数据流转换为9BIT一个的int数据
    def __loadData(self, data: bytes):
        # 将数据读取为bitarray
        arrBits = bitstring.BitArray(data)

        # 转换为int数组
        pos = 0
        bitlen = 9
        index = 256
        result = []

        while pos + bitlen < len(arrBits):
            tmp = arrBits[pos: pos + bitlen]
            tmp._reverse()
            result.append(tmp.uint)
            pos += bitlen
            index += 1
            if 1 << bitlen == index and bitlen != 12:
                bitlen += 1

        return result

    # LZW解码
    def __decodeRawData(self, data: []):
        dictionary = {i: [i] for i in range(0, 256)}
        dictSize = 256

        it = iter(data)
        w = [next(it)]

        result = list()
        result.append(w[0])

        entry = 0
        for k in it:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dictSize:
                entry = w + w[0:1]
            else:
                raise ValueError('Bad compressed k')

            result += entry

            # Add w+entry[0] to the dictionary.
            dictionary[dictSize] = w + entry[0:1]
            dictSize += 1
            w = entry
            if dictSize >= 4096:
                print('重新生成字典')
                dictionary = {i: [i] for i in range(0, 256)}
                dictSize = 256

        return result

    # 解码流，并保存到指定的路径
    def decodeImage(self, data: bytes, filepath: str):
        if data.startswith(b'\xff\xd8'):  # 这是jiff文件
            with open(filepath + '.jfif', 'wb') as fp:
                fp.write(data)
        elif data.startswith(b'LZW!'):  # 这是BMP文件
            # 测试代码
            # with open(filepath+'_src.bin', 'wb') as sp:
            #     sp.write(data)

            arrInt = self.__loadData(data[IMAGE_DECODE_OFFSET:])
            # print(len(arrInt))
            # print(arrInt)
            arrRaw = self.__decodeRawData(arrInt)

            # BITMAP头部
            # typedef struct tagBITMAPFILEHEADER {
            #         WORD    bfType;
            #         DWORD   bfSize;
            #         WORD    bfReserved1;
            #         WORD    bfReserved2;
            #         DWORD   bfOffBits;
            # } BITMAPFILEHEADER, FAR *LPBITMAPFILEHEADER, *PBITMAPFILEHEADER;
            bytesFileHeader = struct.pack('<HIHHI', 0x4d42, 14 + len(arrRaw), 0, 0, 54)
            bytesData = bytes(arrRaw)
            with open(filepath + '.jfif', 'wb') as fp:
                fp.write(bytesFileHeader)
                fp.write(bytesData)
        else:
            logger.error('未知的图像数据')
            logger.debug(data)

    # LZW编码数据,数组bytes，输出int数组
    def __encodeRawData(self, data: bytes):
        arTmp = bytearray(range(256))
        dictionary = {bytes(arTmp[i:i + 1]): i for i in range(256)}
        dictSize = 256

        result = []
        w = bytes()
        for c in data:
            wc = w + bitstring.BitArray('uint:8=' + str(c)).bytes

            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = dictSize
                dictSize += 1
                w = bitstring.BitArray('uint:8=' + str(c)).bytes

            if dictSize >= 4096:
                dictionary = {i: [i] for i in range(0, 256)}
                dictSize = 256

        if len(w) > 0:
            result.append(dictionary[w])

        return result

    # 保存数据，将int数组保存为9 bit一位的bytes
    def __saveData(self, data: []):
        result = bitstring.BitArray()
        bitlen = 9
        index = 256
        for d in data:
            tmp = bitstring.BitArray('uint:%d=%d' % (bitlen, d))
            tmp._reverse()
            result.append(tmp)
            index += 1
            if 1 << bitlen == index and bitlen != 12:
                bitlen += 1


        # 补0，对齐8位
        lens = len(result)
        append = 8 - lens % 8
        if append > 0 and append < 8:
            result.append('uint:' + str(append) + '=0')

        return result.bytes

    # 编码数据，返回字节流
    def encodeImage(self, filepath: str):
        with open(filepath, 'rb') as fp:
            fileData = fp.read()  # 文件内容
            rawData = fileData[IMAGE_ENCODE_OFFSET:]  # 截掉文件头

            arrHeader = struct.pack('<4s2I', b'LZW!', len(rawData), binascii.crc32(rawData))

            arrEncodeData = self.__encodeRawData(rawData)
            arrEncodeBytes = self.__saveData(arrEncodeData)

            return arrHeader + arrEncodeBytes


if __name__ == '__main__':
    lw = ImgLzw()
    fp = open('D:\\WorkSpace\\PythonFeiQ\\Static\\recvimage\\bd1f1935.bmp_src.bin', mode='rb')
    arrBytes = fp.read()
    fp.close()
    ret = lw.decodeImage(arrBytes, 'd:\\test')
    # print(ret)
    # with open('d:\\test_encode.bin', 'wb') as fp:
    #    fp.write(lw.encodeImage('D:\\WorkSpace\\PythonFeiQ\\Static\\recvimage\\ade45749.bmp'))
