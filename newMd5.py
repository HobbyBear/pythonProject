import struct
import math
import binascii

import numbers

lrot = lambda x, n: (x << n) | (x >> 32 - n)  # 循环左移

# 初始向量
A, B, C, D = (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)
register = [0, 0, 0, 0]  # 寄存器
regIndex = 0  # 当前寄存器的位置
readSize = 0
msgSize = 0
sizeArr = [0, 0, 0, 0]

# 循环左移的位移位数
r = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
     5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
     4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
     6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
     ]

k = [int(math.floor(abs(math.sin(i + 1)) * (2 ** 32))) for i in range(64)]


def init_mess(message):
    global A
    global B
    global C
    global D
    global msgSize
    global readSize
    global sizeArr

    msgSize = getMsgSize(message)
    sizeArr = [int(msgSize / 4), int(msgSize / 4 * 2), int(msgSize / 4 * 3), int(msgSize)]
    A, B, C, D = (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)
    length = struct.pack('<Q', len(message) * 8)  # 原消息长度64位比特的添加格式
    while len(message) > 64:
        solve(message[:64])
        message = message[64:]
        readSize += 64
        saveToRegister()
        # 长度不足64个字节消息自行填充
    message += b'\x80'
    # 判断是否足够预留8个字节的消息长度，若不足，则需要多填充一个64个字节的0
    if len(message) > 56:
        message += b'\x00' * (120 - len(message))
        solve(message[:64])  # 每64个字节进行一轮处理
        message = message[64:]
        readSize += 64
        saveToRegister()
    else:
        message += b'\x00' * (56 - len(message))
    # print(type(length))
    message += length  # 将原消息长度加入最后64位比特
    # print binascii.b2a_hex(message)
    solve(message[:64])  # 处理消息的前64个字节，共512位
    readSize += 64
    saveToRegister()


def saveToRegister():
    global msgSize
    global readSize
    global register
    global B
    global sizeArr
    index = 0
    for i in sizeArr:
        if readSize <= i:
            if readSize == i:
                register[index] = B
            j = index-1
            print(index)
            while j >= 0:
                if register[j] == 0:
                    print(j)
                    register[j] = B
                    j += -1
                else:
                    break
        index += 1


def getMsgSize(message):
    size = 0
    length = struct.pack('<Q', len(message) * 8)  # 原消息长度64位比特的添加格式
    while len(message) > 64:
        message = message[64:]
        size += 64
    # 长度不足64个字节消息自行填充
    message += b'\x80'
    # 判断是否足够预留8个字节的消息长度，若不足，则需要多填充一个64个字节的0
    if len(message) > 56:
        message += b'\x00' * (120 - len(message))
        size += 64
        message = message[64:]
    else:
        message += b'\x00' * (56 - len(message))
    message += length  # 将原消息长度加入最后64位比特
    size += 64
    return size


def solve(chunk):
    global A
    global B
    global C
    global D
    w = list(struct.unpack('<' + 'I' * 16, chunk))  # 分成16个组，I代表1组32位
    a, b, c, d = A, B, C, D

    for i in range(64):  # 64轮运算
        if i < 16:  # 每一轮运算只用到了b,c,d三个
            f = (b & c) | ((~b) & d)
            flag = i  # 用于标识处于第几组信息
        elif i < 32:
            f = (b & d) | (c & (~d))
            flag = (5 * i + 1) % 16
        elif i < 48:
            f = (b ^ c ^ d)
            flag = (3 * i + 5) % 16
        else:
            f = c ^ (b | (~d))
            flag = (7 * i) % 16
        tmp = b + lrot((a + f + k[i] + w[flag]) & 0xffffffff, r[i])  # &0xffffffff为了类型转换
        a, b, c, d = d, tmp & 0xffffffff, b, c
    A = (A + a) & 0xffffffff
    B = (B + b) & 0xffffffff
    C = (C + c) & 0xffffffff
    D = (D + d) & 0xffffffff


def digest():
    global A
    global B
    global C
    global D
    return struct.pack('<IIII', A, B, C, D)


def hex_digest():
    return binascii.hexlify(digest()).decode()


def register_hex_digest():
    global register
    return binascii.hexlify(struct.pack('<IIII', register[0], register[1], register[2], register[3])).decode()


# cced11f7bbbffea2f718903216643648
mess = str.encode("2a")
init_mess(mess)
print(hex_digest())
# 01234567b88694cffedcba98003484fd
print(register_hex_digest())
print(msgSize)
