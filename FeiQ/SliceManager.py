from FeiQ.Struct.BmpSlice import BmpSlice


# 分片报文处理器
class __SliceManager:
    def __init__(self):
        self.data = dict()

    # 添加分片数据
    def append(self, bs: BmpSlice):
        if bs.key in self.data:
            tmp: dict() = self.data[bs.key]
            tmp[bs.slice] = bs
        else:
            tmp = dict()
            tmp[bs.slice] = bs
            self.data[bs.key] = tmp

    # 检查容器中分片容量
    def count(self, key):
        if key not in self.data:
            return 0
        return len(self.data[key])

    # 移除容器中的数据
    def erase(self, key):
        if key in self.data:
            self.data.pop(key)

    # 获取拼接的数据报文,返回的对象为bytes
    def getData(self, key):
        if key not in self.data:
            return ''
        tmp: dict() = self.data[key]
        if 1 not in tmp:
            return False

        bs: BmpSlice = tmp[1]

        if len(tmp) != bs.totalSlice:
            return ''

        tmpVal = []
        for i in range(1, bs.totalSlice + 1):
            if i not in tmp:
                return ''
            tmpVal.append(tmp[i].data)

        return b''.join(tmpVal)


SliceManagerInstance = __SliceManager()
