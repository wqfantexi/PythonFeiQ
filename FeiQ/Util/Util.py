
#移除bytes数组末尾的0
def RemoveLastZero(data:bytes):
    pos = data.rindex(b'\0')
    if pos > 0:
        return data[:pos]
    return data